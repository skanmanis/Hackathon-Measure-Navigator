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
    "compliance": ["reading_values", "reading_dates", "care_setting"],
    "eligibility": ["scenario_facts"],
    "exclusion": ["scenario_facts"],
}

DEEP_DIVE_FACTS = ["pos_code", "claim_code", "reading_source", "modifier", "numerator_loaded"]


FACT_QUESTIONS = {
    "reading_values": "What readings should I evaluate? You can provide only the clinical values without identifiers.",
    "reading_dates": "Were the readings taken on the same date or on different dates?",
    "care_setting": "What was the care setting for the reading—outpatient, inpatient, emergency department, home, or another setting?",
    "pos_code": "Do you know the place-of-service (POS) code associated with the reading?",
    "claim_code": "Do you know the claim, CPT, or CPT II code used to submit the reading?",
    "reading_source": "Where was the reading documented—for example, a claim, medical record, supplemental file, or another source?",
    "modifier": "Was a modifier submitted with the blood-pressure code? If so, what was it?",
    "numerator_loaded": "Can you confirm whether the qualifying reading reached the numerator input or staging table?",
    "scenario_facts": "What non-identifying facts have you already confirmed for this scenario?",
}

UNKNOWN_VALUES = {"unknown", "i don't know", "i dont know", "not sure", "unsure", "don't know", "dont know", "n/a"}


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
        if len(readings) == 1:
            facts["reading_dates"] = "single reading"
    if "same day" in lowered or "same date" in lowered:
        facts["reading_dates"] = "same date"
    elif "different day" in lowered or "different date" in lowered:
        facts["reading_dates"] = "different dates"
    for setting in ("inpatient", "outpatient", "home", "telehealth"):
        if setting in lowered:
            facts["care_setting"] = setting
    if "emergency" in lowered or re.search(r"\bed\b", lowered):
        facts["care_setting"] = "emergency department"
    pos = re.search(r"(?i)\b(?:pos|place of service)\s*(?:code)?\s*[:#-]?\s*(\d{2})\b", text)
    if pos:
        facts["pos_code"] = pos.group(1)
    claim = re.search(r"(?i)\b(?:cpt|cpt ii|hcpcs|claim code)\s*[:#-]?\s*([A-Z0-9]{4,7})\b", text)
    if claim:
        facts["claim_code"] = claim.group(1).upper()
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
        if fact not in facts:
            return fact
    if facts.get("care_setting") == "UNKNOWN" and "pos_code" not in facts:
        return "pos_code"
    if facts.get("pos_code") == "UNKNOWN" and "claim_code" not in facts:
        return "claim_code"
    if facts.get("_deep_dive"):
        for fact in DEEP_DIVE_FACTS:
            if fact not in facts:
                return fact
    return None


def normalize_fact_response(fact: str, text: str) -> tuple[bool, Any, dict[str, Any]]:
    lowered = text.strip().lower()
    if lowered in UNKNOWN_VALUES:
        return True, "UNKNOWN", {}
    extracted = fallback_facts(text)
    if fact in extracted:
        return True, extracted[fact], extracted
    if fact == "reading_dates":
        if "single" in lowered or "only one" in lowered:
            return True, "single reading", extracted
        if re.search(r"\b(?:2026|\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\b", lowered):
            return True, text.strip(), extracted
        return False, None, extracted
    if fact == "pos_code" and re.fullmatch(r"\d{2}", lowered):
        return True, lowered, extracted
    if fact in {"claim_code", "modifier"} and re.fullmatch(r"[a-z0-9-]{2,12}", lowered):
        return True, text.strip().upper(), extracted
    if fact in {"reading_source", "numerator_loaded", "scenario_facts"}:
        return True, text.strip(), extracted
    if fact == "care_setting":
        return False, None, extracted
    return True, text.strip(), extracted
