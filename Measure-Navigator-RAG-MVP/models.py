from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Chunk:
    chunk_id: str
    text: str
    measure_id: str
    measurement_year: int
    source_type: str
    source_name: str
    locator: str
    authority: int
    title: str = ""
    sql_text: str = ""
    review_status: str = "hackathon"
    dependency_names: list[str] = field(default_factory=list)

    def metadata(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("text")
        data.pop("dependency_names")
        data["dependency_names"] = "|".join(self.dependency_names)
        return data


@dataclass
class Evidence:
    chunk_id: str
    text: str
    measure_id: str
    measurement_year: int
    source_type: str
    source_name: str
    locator: str
    authority: int
    score: float
    title: str = ""

    @property
    def citation(self) -> str:
        return f"{self.source_name} — {self.locator}" if self.locator else self.source_name


@dataclass
class SessionState:
    session_id: str
    measure_id: str
    measurement_year: int
    original_question: str
    intent: str = "general_measure_question"
    intent_confidence: float = 0.0
    facts: dict[str, Any] = field(default_factory=dict)
    asked_facts: list[str] = field(default_factory=list)
    turns: list[dict[str, str]] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    status: str = "ACTIVE"

