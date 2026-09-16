from __future__ import annotations

import hashlib
import json
import math
import os
import re
from typing import Any

from config import Settings


class LLMAdapter:
    """OpenAI-compatible adapter with deterministic local fallbacks for setup and tests."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = None
        if settings.use_openai and os.getenv("OPENAI_API_KEY"):
            try:
                from openai import OpenAI

                kwargs: dict[str, Any] = {"api_key": os.getenv("OPENAI_API_KEY")}
                if settings.openai_base_url:
                    kwargs["base_url"] = settings.openai_base_url
                self.client = OpenAI(**kwargs)
            except Exception:
                self.client = None

    @property
    def mode(self) -> str:
        return "openai" if self.client else "local-fallback"

    def embed(self, texts: list[str]) -> list[list[float]]:
        if self.client:
            response = self.client.embeddings.create(model=self.settings.embedding_model, input=texts)
            return [item.embedding for item in response.data]
        return [self._hash_embedding(text) for text in texts]

    @staticmethod
    def _hash_embedding(text: str, dimensions: int = 256) -> list[float]:
        vector = [0.0] * dimensions
        for token in re.findall(r"[a-z0-9_]+", text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % dimensions
            sign = 1.0 if digest[4] % 2 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    def structured(self, system: str, user: str, fallback: dict[str, Any]) -> dict[str, Any]:
        if not self.client:
            return fallback
        try:
            response = self.client.chat.completions.create(
                model=self.settings.chat_model,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            )
            return json.loads(response.choices[0].message.content or "{}")
        except Exception:
            return fallback

    def text(self, system: str, user: str, fallback: str) -> str:
        if not self.client:
            return fallback
        try:
            response = self.client.chat.completions.create(
                model=self.settings.chat_model,
                temperature=0.1,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            )
            return (response.choices[0].message.content or fallback).strip()
        except Exception:
            return fallback

