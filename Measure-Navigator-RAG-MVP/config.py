from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    root: Path = ROOT
    measurement_year: int = 2026
    measures: tuple[str, ...] = ("CBP", "GSD", "KED", "EED", "SPC")
    chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-5-mini")
    embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    openai_base_url: str | None = os.getenv("OPENAI_BASE_URL") or None
    use_openai: bool = os.getenv("USE_OPENAI", "true").lower() == "true"
    faq_threshold: float = 0.73
    document_threshold: float = 0.20
    top_k: int = 6

    @property
    def knowledge_root(self) -> Path:
        configured = Path(os.getenv("KNOWLEDGE_ROOT", "knowledge/MY2026"))
        return configured if configured.is_absolute() else self.root / configured

    @property
    def chroma_path(self) -> Path:
        return self.root / "data" / "chroma"


settings = Settings()

