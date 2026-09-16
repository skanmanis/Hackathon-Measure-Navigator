from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path
from typing import Iterable

from config import Settings
from llm import LLMAdapter
from models import Chunk, Evidence


class KnowledgeStore:
    def __init__(self, settings: Settings, llm: LLMAdapter):
        self.settings = settings
        self.llm = llm
        self._fallback_path = settings.root / "data" / "catalog.json"
        self._fallback: list[dict] = []
        self.collection = None
        try:
            import chromadb

            settings.chroma_path.mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=str(settings.chroma_path))
            self.collection = client.get_or_create_collection(
                "measure_navigator_my2026", metadata={"hnsw:space": "cosine"}
            )
        except Exception:
            self.collection = None
        self._load_fallback()

    @property
    def backend(self) -> str:
        return "chromadb" if self.collection is not None else "portable-json"

    def _load_fallback(self) -> None:
        if self._fallback_path.exists():
            self._fallback = json.loads(self._fallback_path.read_text(encoding="utf-8"))

    def clear(self) -> None:
        if self.collection is not None:
            existing = self.collection.get(include=[])
            if existing.get("ids"):
                self.collection.delete(ids=existing["ids"])
        self._fallback = []
        if self._fallback_path.exists():
            self._fallback_path.unlink()

    def upsert(self, chunks: list[Chunk], batch_size: int = 64) -> None:
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            vectors = self.llm.embed([chunk.text for chunk in batch])
            rows = [
                {"id": chunk.chunk_id, "document": chunk.text, "metadata": chunk.metadata(), "embedding": vector}
                for chunk, vector in zip(batch, vectors)
            ]
            if self.collection is not None:
                self.collection.upsert(
                    ids=[row["id"] for row in rows],
                    documents=[row["document"] for row in rows],
                    metadatas=[row["metadata"] for row in rows],
                    embeddings=[row["embedding"] for row in rows],
                )
            self._fallback.extend(rows)
        self._fallback_path.write_text(json.dumps(self._fallback, indent=2), encoding="utf-8")

    def count(self) -> int:
        if self.collection is not None:
            return self.collection.count()
        return len(self._fallback)

    def search(self, query: str, measure_id: str, measurement_year: int, top_k: int = 6) -> list[Evidence]:
        vector = self.llm.embed([query])[0]
        rows: list[tuple[str, str, dict, float]] = []
        if self.collection is not None and self.collection.count():
            where = {"$and": [{"measure_id": measure_id}, {"measurement_year": measurement_year}]}
            result = self.collection.query(
                query_embeddings=[vector], n_results=min(max(top_k * 3, 10), self.collection.count()), where=where
            )
            for idx, chunk_id in enumerate(result.get("ids", [[]])[0]):
                distance = result.get("distances", [[]])[0][idx]
                rows.append((chunk_id, result["documents"][0][idx], result["metadatas"][0][idx], 1.0 - distance))
        else:
            for row in self._fallback:
                meta = row["metadata"]
                if meta.get("measure_id") != measure_id or int(meta.get("measurement_year", 0)) != measurement_year:
                    continue
                semantic = sum(a * b for a, b in zip(vector, row["embedding"]))
                rows.append((row["id"], row["document"], meta, semantic))

        query_terms = set(re.findall(r"[a-z0-9_]+", query.lower()))
        ranked: list[Evidence] = []
        for chunk_id, text, meta, semantic in rows:
            text_terms = set(re.findall(r"[a-z0-9_]+", text.lower()))
            lexical = len(query_terms & text_terms) / max(len(query_terms), 1)
            authority_bonus = max(0, 6 - int(meta.get("authority", 6))) * 0.01
            score = 0.72 * max(semantic, 0) + 0.28 * lexical + authority_bonus
            ranked.append(Evidence(
                chunk_id=chunk_id, text=text, measure_id=meta["measure_id"],
                measurement_year=int(meta["measurement_year"]), source_type=meta["source_type"],
                source_name=meta["source_name"], locator=meta.get("locator", ""),
                authority=int(meta.get("authority", 6)), score=min(score, 1.0), title=meta.get("title", "")
            ))
        return sorted(ranked, key=lambda item: (-item.score, item.authority))[:top_k]

    def list_faqs(self, measure_id: str | None = None) -> list[dict]:
        path = self.settings.root / "data" / "seed-faq.csv"
        if not path.exists():
            return []
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        if measure_id:
            aliases = {measure_id, f"SYN-{measure_id}"}
            rows = [row for row in rows if row.get("measure_id") in aliases]
        return rows

