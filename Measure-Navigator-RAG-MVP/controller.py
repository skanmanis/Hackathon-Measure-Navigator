from __future__ import annotations

import re
from typing import Any


INTENT_RULES = [
    ("sql_implementation", ("stored procedure", "sql", "code", "query", "cte", "implementation")),
    ("exclusion", ("exclude", "excluded", "exclusion", "hospice", "death")),
    ("eligibility", ("eligible", "eligibility", "enrollment", "denominator", "age")),
    ("reading_selection", ("reading", "blood pressure", "lowest", "same day", "bp")),
    ("value_set", ("value set", "code", "oid", "hcpcs", "cpt", "icd")),
    ("medication", ("medication", "drug", "ndc", "rxnorm", "statin")),
    ("data_source", ("claim", "inpatient", "outpatient", "data source", "permitted", "allowed")),
    ("compliance", ("compliant", "non compliant", "noncompliant", "numerator", "met")),
]


REQUIRED_FACTS: dict[str, list[str]] = {
    "reading_selection": ["reading_values", "reading_dates", "care_setting"],
    "compliance": ["scenario_facts"],
    "eligibility": ["scenario_facts"],
    "exclusion": ["scenario_facts"],
}


FACT_QUESTIONS = {
    "reading_values": "What readings should I evaluate? You can provide only the clinical values without identifiers.",
    "reading_dates": "Were the readings taken on the same date or on different dates?",
    "care_setting": "What was the care setting for these readings, such as outpatient, inpatient, or home?",
    "scenario_facts": "What non-identifying facts have you already confirmed for this scenario?",
}


def classify_intent(question: str) -> tuple[str, float]:
    lowered = question.lower()
    for intent, terms in INTENT_RULES:
        hits = sum(term in lowered for term in terms)
        if hits:
            return intent, min(0.72 + hits * 0.08, 0.96)
    return "specification_clarification", 0.64


def fallback_facts(text: str) -> dict[str, Any]:
    lowered = text.lower()
    facts: dict[str, Any] = {}
    readings = re.findall(r"\b(\d{2,3})\s*/\s*(\d{2,3})\b", text)
    if readings:
        facts["reading_values"] = [f"{a}/{b}" for a, b in readings]
        facts["_scenario_mode"] = True
    if "same day" in lowered or "same date" in lowered:
        facts["reading_dates"] = "same date"
    elif "different day" in lowered or "different date" in lowered:
        facts["reading_dates"] = "different dates"
    for setting in ("inpatient", "outpatient", "home", "telehealth"):
        if setting in lowered:
            facts["care_setting"] = setting
    if any(marker in lowered for marker in ("member", "my values", "this scenario", "this case")):
        facts["_scenario_mode"] = True
        facts["scenario_facts"] = text
    return facts


def next_missing_fact(intent: str, facts: dict[str, Any], asked: list[str], evidence_available: bool) -> str | None:
    # A directly answerable specification question should not be burdened with scenario questions.
    if intent in {"specification_clarification", "sql_implementation", "value_set", "medication", "data_source"}:
        return None
    if not facts.get("_scenario_mode"):
        return None
    for fact in REQUIRED_FACTS.get(intent, []):
        if fact not in facts and fact not in asked:
            return fact
    return None
