from config import Settings
from models import Evidence, SessionState
from service import NavigatorService


def test_phi_masking():
    masked, changed = NavigatorService._mask("Member ID ABC12345 has a question")
    assert changed
    assert "ABC12345" not in masked


def test_measure_language_is_not_mistaken_for_identifier():
    masked, changed = NavigatorService._mask("Is the member compliant?")
    assert not changed
    assert masked == "Is the member compliant?"


def test_response_text_ends_with_punctuation():
    assert NavigatorService._ensure_punctuation("Grounded answer [1]") == "Grounded answer [1]."
    assert NavigatorService._ensure_punctuation("Already complete.") == "Already complete."


def test_single_reading_hides_multiple_readings_evidence():
    session = SessionState(
        session_id="test", measure_id="CBP", measurement_year=2026,
        original_question="Why is the member not compliant?", intent="compliance",
        facts={"reading_values": ["115/79"]},
    )
    evidence = [
        Evidence("one", "Details", "CBP", 2026, "specification", "spec.md", "Document", 1, 0.9, "Multiple blood pressure readings on the same date"),
        Evidence("two", "Details", "CBP", 2026, "specification", "spec.md", "Document", 1, 0.8, "Evidence needed"),
    ]
    filtered = NavigatorService._filter_relevant_evidence(session, evidence)
    assert [item.chunk_id for item in filtered] == ["two"]


def test_my2026_only(tmp_path):
    custom = Settings(root=tmp_path)
    service = NavigatorService(custom)
    service._validate_scope("CBP", 2026)
    try:
        service._validate_scope("CBP", 2027)
        assert False, "Expected MY2027 to be rejected"
    except ValueError:
        pass


def test_deterministic_reading_summary_uses_lowest_values():
    session = SessionState(
        session_id="test", measure_id="CBP", measurement_year=2026,
        original_question="Are these readings compliant?", intent="reading_selection",
        facts={"reading_values": ["142/72", "128/84"], "reading_dates": "same date", "care_setting": "outpatient"}
    )
    evidence = [Evidence(
        chunk_id="spec-1", text="Use the lowest systolic and lowest diastolic. Controlled is below 140 and below 90.",
        measure_id="CBP", measurement_year=2026, source_type="specification", source_name="spec.pdf",
        locator="Page 1", authority=1, score=0.9
    )]
    answer = NavigatorService._fallback_answer(session, evidence, None)
    assert "lowest systolic is 128" in answer
    assert "lowest diastolic is 72" in answer
    assert answer.startswith("Yes")
