from __future__ import annotations

import re
import uuid
from dataclasses import asdict
from typing import Any

from config import Settings
from controller import FACT_QUESTIONS, classify_intent, fallback_facts, next_missing_fact
from ingestion import IngestionService
from llm import LLMAdapter
from models import Evidence, SessionState
from retrieval import KnowledgeStore


class NavigatorService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = LLMAdapter(settings)
        self.store = KnowledgeStore(settings, self.llm)
        self.ingestion = IngestionService(settings, self.llm, self.store)
        self.sessions: dict[str, SessionState] = {}

    def packages(self) -> list[dict]:
        ready = self.store.count() > 0
        return [
            {"measure_id": measure, "display_name": measure, "measurement_year": 2026, "status": "ready" if ready else "index_required"}
            for measure in self.settings.measures
        ]

    def start(self, question: str, measure_id: str, measurement_year: int) -> dict:
        question = question.strip()
        if not question:
            raise ValueError("Enter a question.")
        self._validate_scope(measure_id, measurement_year)
        masked, phi_masked = self._mask(question)
        deterministic_intent, confidence = classify_intent(masked)
        extracted_fallback = fallback_facts(masked)
        understood = self.llm.structured(
            "Classify a MY2026 measure question and extract only explicitly supplied non-identifying facts. Return JSON with intent, confidence, facts. Allowed intents: specification_clarification, eligibility, exclusion, compliance, reading_selection, value_set, medication, data_source, sql_implementation.",
            masked,
            {"intent": deterministic_intent, "confidence": confidence, "facts": extracted_fallback},
        )
        intent = understood.get("intent") if understood.get("intent") in {
            "specification_clarification", "eligibility", "exclusion", "compliance", "reading_selection",
            "value_set", "medication", "data_source", "sql_implementation"
        } else deterministic_intent
        facts = extracted_fallback | (understood.get("facts") or {})
        session = SessionState(
            session_id=str(uuid.uuid4()), measure_id=measure_id, measurement_year=measurement_year,
            original_question=masked, intent=intent, intent_confidence=float(understood.get("confidence", confidence)),
            facts=facts, turns=[{"role": "user", "content": masked}]
        )
        self.sessions[session.session_id] = session
        return self._advance(session, phi_masked=phi_masked, masked_question=masked)

    def respond(self, session_id: str, response: str) -> dict:
        session = self._session(session_id)
        response = response.strip()
        if not response:
            raise ValueError("Enter a response.")
        masked, phi_masked = self._mask(response)
        session.turns.append({"role": "user", "content": masked})
        pending = session.asked_facts[-1] if session.asked_facts else None
        if pending:
            extracted = fallback_facts(masked)
            session.facts[pending] = extracted.get(pending, masked)
            session.facts.update(extracted)
        return self._advance(session, phi_masked=phi_masked, masked_question=masked)

    def _advance(self, session: SessionState, phi_masked: bool, masked_question: str) -> dict:
        query = self._retrieval_query(session)
        evidence = self.store.search(query, session.measure_id, session.measurement_year, self.settings.top_k)
        eligible = [item for item in evidence if item.score >= self.settings.document_threshold]
        faq_threshold = 0.52 if self.llm.mode == "local-fallback" else self.settings.faq_threshold
        faq_matches = [item for item in eligible if item.source_type == "faq" and item.score >= faq_threshold]
        documents = [item for item in eligible if item.source_type != "faq"]
        session.evidence_ids = [item.chunk_id for item in eligible]

        missing = next_missing_fact(session.intent, session.facts, session.asked_facts, bool(documents or faq_matches))
        if missing:
            session.asked_facts.append(missing)
            fallback = FACT_QUESTIONS[missing]
            follow_up = self.llm.text(
                "Phrase exactly one concise follow-up question for the specified missing fact. Do not ask for names, IDs, dates of birth, addresses, or any new fact.",
                f"Missing fact: {missing}\nKnown facts: {session.facts}\nConversation: {session.turns[-3:]}", fallback
            )
            session.turns.append({"role": "assistant", "content": follow_up})
            return self._response(session, "FOLLOW_UP", follow_up, faq_matches, documents, phi_masked, masked_question, missing)

        if not documents and not faq_matches:
            message = "I could not find sufficiently relevant MY2026 evidence for this question. Add the applicable source documents to the measure folder and rebuild the index, or refine the question."
            session.status = "INSUFFICIENT_EVIDENCE"
            return self._response(session, session.status, message, [], [], phi_masked, masked_question)

        evidence_for_answer = sorted(documents or faq_matches, key=lambda item: (item.authority, -item.score))[:5]
        conflict = self._detect_conflict(evidence_for_answer)
        answer = self._compose_answer(session, evidence_for_answer, conflict)
        session.status = "ANSWERED"
        session.turns.append({"role": "assistant", "content": answer})
        return self._response(session, "ANSWERED", answer, faq_matches, documents, phi_masked, masked_question, conflict=conflict)

    def _compose_answer(self, session: SessionState, evidence: list[Evidence], conflict: str | None) -> str:
        bundle = "\n\n".join(
            f"SOURCE {index + 1} [{item.source_type}; authority {item.authority}; {item.citation}]\n{item.text}"
            for index, item in enumerate(evidence)
        )
        fallback = self._fallback_answer(session, evidence, conflict)
        return self.llm.text(
            "You are Measure Navigator. Answer only from the supplied MY2026 evidence and explicit user facts. Give the direct answer first. Be concise. Preserve qualifications. The specification outranks VSD/MLD, SQL explanations, and FAQs. Cite sources inline using [1], [2]. Never claim SQL was executed or member data was queried. If evidence is incomplete, say what cannot be determined.",
            f"Measure: {session.measure_id}\nIntent: {session.intent}\nQuestion: {session.original_question}\nFacts: {session.facts}\nConflict: {conflict or 'none'}\n\n{bundle}",
            fallback,
        )

    @staticmethod
    def _fallback_answer(session: SessionState, evidence: list[Evidence], conflict: str | None) -> str:
        primary = evidence[0]
        if "\nAnswer:" in primary.text:
            lead = primary.text.split("\nAnswer:", 1)[1].strip()[:900]
        elif primary.text.startswith("English explanation:"):
            lead = primary.text.split("Original T-SQL:", 1)[0].replace("English explanation:", "").strip()[:900]
        else:
            sentences = [part.strip(" #\n") for part in re.split(r"(?<=[.!?])\s+|\n+", primary.text) if len(part.strip()) > 20]
            terms = set(re.findall(r"[a-z0-9]+", session.original_question.lower())) - {"when", "which", "what", "does", "from", "with", "this", "that", "member", "cbp"}
            ranked = sorted(sentences, key=lambda sentence: len(terms & set(re.findall(r"[a-z0-9]+", sentence.lower()))), reverse=True)
            lead = " ".join(ranked[:3])[:900]

        readings = session.facts.get("reading_values") or []
        setting = str(session.facts.get("care_setting", "")).lower()
        source_text = " ".join(item.text.lower() for item in evidence)
        if readings and "lowest systolic" in source_text and "lowest diastolic" in source_text:
            pairs = [(int(value.split("/")[0]), int(value.split("/")[1])) for value in readings if re.fullmatch(r"\d{2,3}/\d{2,3}", value)]
            if pairs:
                systolic, diastolic = min(value[0] for value in pairs), min(value[1] for value in pairs)
                if setting in {"inpatient", "emergency", "emergency department", "ed"} and "not accepted" in source_text:
                    lead = f"No. The supplied {setting} setting is not accepted as numerator evidence in the retrieved rule, so these readings should not be used for this scenario."
                elif "below 140" in source_text and "below 90" in source_text:
                    controlled = systolic < 140 and diastolic < 90
                    lead = (
                        f"{'Yes' if controlled else 'No'}. For the supplied same-date readings, the lowest systolic is {systolic} and the lowest diastolic is {diastolic}. "
                        f"Those representative values {'are' if controlled else 'are not'} within the retrieved control thresholds."
                    )
        answer = f"{lead} [1]"
        if conflict:
            answer += f"\n\nPotential implementation difference: {conflict}"
        answer += "\n\nThis explanation is based on retrieved documents and supplied facts; no member database or stored procedure was executed."
        return answer

    @staticmethod
    def _detect_conflict(evidence: list[Evidence]) -> str | None:
        types = {item.source_type for item in evidence}
        if "specification" not in types or not ({"sql", "sql_explanation"} & types):
            return None
        # This lightweight gate flags explicit contradiction language; semantic adjudication remains future work.
        combined = " ".join(item.text.lower() for item in evidence)
        if any(term in combined for term in ("conflict", "differs from", "not permitted", "contrary to")):
            return "The retrieved implementation material may differ from the specification. Follow the specification and review the SQL implementation."
        return None

    def _response(
        self, session: SessionState, status: str, message: str, faqs: list[Evidence], documents: list[Evidence],
        phi_masked: bool, masked_question: str, missing: str | None = None, conflict: str | None = None
    ) -> dict:
        trace_sources = sorted(documents or faqs, key=lambda item: (item.authority, -item.score))[:6]
        return {
            "session_id": session.session_id,
            "status": status,
            "message": message,
            "measure_id": session.measure_id,
            "measurement_year": session.measurement_year,
            "intent": {"name": session.intent, "confidence": session.intent_confidence},
            "facts": {key: value for key, value in session.facts.items() if not key.startswith("_")},
            "missing_fact": missing,
            "faqs": [self._evidence_dict(item) for item in faqs[:3]],
            "sources": [self._evidence_dict(item) for item in trace_sources],
            "phi_masked": phi_masked,
            "masked_question": masked_question,
            "privacy_notice": "Possible identifiers were masked. Do not enter further PHI." if phi_masked else "",
            "trace": {
                "intent": session.intent,
                "facts_used": {key: value for key, value in session.facts.items() if not key.startswith("_")},
                "open_condition": missing,
                "source_priority": "Specification > VSD/MLD > T-SQL > SQL-English > FAQ",
                "conflict": conflict,
                "llm_mode": self.llm.mode,
                "retrieval_backend": self.store.backend,
                "citations": [item.citation for item in trace_sources],
            },
        }

    @staticmethod
    def _evidence_dict(item: Evidence) -> dict:
        return {
            "id": item.chunk_id, "title": item.title or item.source_name, "text": item.text,
            "source_type": item.source_type, "source_name": item.source_name,
            "locator": item.locator, "score": round(item.score, 3), "citation": item.citation,
        }

    def _retrieval_query(self, session: SessionState) -> str:
        recent = " ".join(turn["content"] for turn in session.turns[-4:] if turn["role"] == "user")
        return f"{session.intent} {session.original_question} {recent} {session.facts}"

    def _validate_scope(self, measure_id: str, year: int) -> None:
        if measure_id not in self.settings.measures:
            raise ValueError("Unsupported measure.")
        if year != 2026:
            raise ValueError("This hackathon index supports MY2026 only.")

    def _session(self, session_id: str) -> SessionState:
        if session_id not in self.sessions:
            raise ValueError("Session not found.")
        return self.sessions[session_id]

    @staticmethod
    def _mask(text: str) -> tuple[str, bool]:
        patterns = [
            (r"(?i)\b(?:member|patient)\s*(?:id|#|number)\s*[:=-]?\s*[A-Z0-9-]{6,}\b", "[MASKED MEMBER IDENTIFIER]"),
            (r"\b\d{3}-\d{2}-\d{4}\b", "[MASKED IDENTIFIER]"),
            (r"(?i)\b(?:mrn|ssn)\s*[:=-]?\s*[A-Z0-9-]{5,}\b", "[MASKED IDENTIFIER]"),
            (r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[MASKED EMAIL]"),
            (r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b", "[MASKED PHONE]"),
        ]
        masked = text
        for pattern, replacement in patterns:
            masked = re.sub(pattern, replacement, masked)
        return masked, masked != text
