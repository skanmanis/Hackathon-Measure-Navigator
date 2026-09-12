"""Deterministic, fact-driven measure evaluation. The model never decides a rule."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path


class CheckEvaluator:
    def __init__(self, root: Path):
        self.catalog_data = json.loads((root / "check_catalog.json").read_text(encoding="utf-8"))
        self.catalog = {item["check_id"]: item for item in self.catalog_data["checks"]}
        self.value_sets = json.loads((root / "value_sets.synthetic.json").read_text(encoding="utf-8"))

    def lookup_value_set(self, oid: str, code_system: str, code: str) -> bool:
        systems = self.value_sets.get(oid, {}).get("codes", {})
        values = systems.get(code_system.upper(), [])
        return code.upper() in {str(value).upper() for value in values}

    def required_facts(self, check_id: str) -> list[dict]:
        if check_id not in self.catalog:
            raise ValueError(f"Unknown check: {check_id}")
        return self.catalog[check_id]["required_facts"]

    def evaluate(self, check_id: str, facts: dict) -> dict:
        check = self.catalog.get(check_id)
        if not check:
            return {"status": "UNKNOWN_CHECK", "check_id": check_id}
        required = [item["name"] for item in check["required_facts"]]
        missing = [name for name in required if facts.get(name) in (None, "")]
        if missing:
            return {"status": "NEEDS_MORE_INFO", "check_id": check_id, "missing_facts": missing}
        unknown = [name for name in required if str(facts.get(name)).upper() == "UNKNOWN"]
        if unknown:
            return {"status": "OPEN_CONDITION", "check_id": check_id, "unknown_facts": unknown,
                    "explanation": check["if_unknown"]}

        oid = check.get("value_set_oid")
        if oid:
            code_name = next(name for name in required if "code" in name or name == "pos_code" or "modifier" in name)
            system = facts.get("code_system") or ("POS" if code_name == "pos_code" else "MODIFIER" if "modifier" in code_name else "ICD-10-CM")
            member = self.lookup_value_set(oid, str(system), str(facts[code_name]))
            inverse = check_id in {"CHK-READING-SETTING", "CHK-READING-MODIFIER"}
            met = not member if inverse else member
            return {"status": "MET" if met else "NOT_MET", "check_id": check_id, "value_set_oid": oid,
                    "explanation": f"{facts[code_name]} {'is' if member else 'is not'} in {oid}."}

        if check_id == "CHK-DATE-BY-JUN30":
            met = date.fromisoformat(str(facts["service_date"])) <= date(int(facts["measurement_year"]), 6, 30)
        elif check_id == "CHK-DATE-BY-YEAREND":
            met = date.fromisoformat(str(facts["the_date"])) <= date(int(facts["measurement_year"]), 12, 31)
        elif check_id == "CHK-READING-DATE-VALID":
            met = date.fromisoformat(str(facts["reading_date"])) >= date.fromisoformat(str(facts["second_dx_date"]))
        elif check_id == "CHK-AGE-66-PLUS":
            met = float(facts["age"]) >= 66
        elif check_id == "CHK-BP-CONTROLLED":
            met = float(facts["systolic"]) < 140 and float(facts["diastolic"]) < 90
        else:
            return {"status": "UNKNOWN_CHECK", "check_id": check_id}
        return {"status": "MET" if met else "NOT_MET", "check_id": check_id,
                "explanation": check["logic"] + (" is satisfied." if met else " is not satisfied.")}


class DecisionTreeEngine:
    def __init__(self, root: Path, taxonomy_path: Path | None = None):
        self.tree = json.loads((root / "decision_tree.generated.json").read_text(encoding="utf-8"))
        self.evaluator = CheckEvaluator(root)
        taxonomy_path = taxonomy_path or root / "intent_taxonomy.json"
        self.taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8")) if taxonomy_path.exists() else None

    def classify_intent(self, question: str) -> dict:
        q = question.lower()
        if not self.taxonomy:
            return {"intent":"DENOMINATOR_ENTRY","route":"check_htn_dx_1","confidence":0.5,"status":"REVIEW_REQUIRED"}
        scored=[]
        for intent in self.taxonomy["intents"]:
            hits=sum(1 for term in intent["terms"] if term in q)
            if hits:
                confidence=min(0.98,0.48 + hits * 0.16)
                scored.append((confidence,intent))
        if not scored:
            return {"intent":"UNCLASSIFIED","route":None,"confidence":0.0,"status":"CHOOSE_INTENT"}
        confidence,intent=max(scored,key=lambda item:item[0])
        threshold=float(self.taxonomy["confidence_threshold"])
        return {"intent":intent["id"],"route":intent["route"],"confidence":confidence,
                "threshold":threshold,"status":"ROUTED" if confidence>=threshold else "CHOOSE_INTENT"}

    def choose_route(self, question: str) -> str:
        classification=self.classify_intent(question)
        return classification.get("route") or "route_by_question_type"

    def advance(self, node_id: str, facts: dict, open_conditions: list, max_steps: int = 20) -> dict:
        trace = []
        for _ in range(max_steps):
            if node_id in self.tree["conclusions"]:
                conclusion = self.tree["conclusions"][node_id]
                return {"status": "COMPLETE", "node_id": node_id, "conclusion": conclusion,
                        "trace": trace, "open_conditions": open_conditions}
            node = self.tree["nodes"][node_id]
            if node["type"] == "router":
                return {"status": "CHOOSE_ROUTE", "node_id": node_id, "options": node["options"], "trace": trace}
            check_id = node["check_id"]
            result = self.evaluator.evaluate(check_id, facts)
            trace.append(result)
            if result["status"] == "NEEDS_MORE_INFO":
                required = [item for item in self.evaluator.required_facts(check_id) if item["name"] in result["missing_facts"]]
                return {"status": "NEEDS_MORE_INFO", "node_id": node_id, "check_id": check_id,
                        "question": self.evaluator.catalog[check_id]["question"], "required_facts": required,
                        "trace": trace, "open_conditions": open_conditions}
            if result["status"] == "OPEN_CONDITION":
                open_conditions.append(result)
            node_id = node["on"][result["status"]]
        raise RuntimeError("Decision tree exceeded its maximum step count")
