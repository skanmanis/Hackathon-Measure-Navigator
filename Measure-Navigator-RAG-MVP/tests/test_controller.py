from controller import classify_intent, fallback_facts, next_missing_fact


def test_multiple_readings_are_extracted():
    intent, confidence = classify_intent("Two BP readings on the same day were 142/72 and 128/84")
    facts = fallback_facts("Two BP readings on the same day were 142/72 and 128/84")
    assert intent == "reading_selection"
    assert confidence > 0.7
    assert facts["reading_values"] == ["142/72", "128/84"]
    assert facts["reading_dates"] == "same date"


def test_controller_selects_only_missing_fact():
    missing = next_missing_fact(
        "reading_selection", {"_scenario_mode": True, "reading_values": ["142/72", "128/84"], "reading_dates": "same date"}, [], True
    )
    assert missing == "care_setting"


def test_direct_spec_question_does_not_force_follow_up():
    assert next_missing_fact("data_source", {}, [], True) is None


def test_generic_reading_rule_question_does_not_force_scenario_facts():
    assert next_missing_fact("reading_selection", {}, [], True) is None
