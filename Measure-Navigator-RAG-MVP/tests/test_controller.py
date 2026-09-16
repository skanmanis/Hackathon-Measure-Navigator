from controller import classify_intent, fallback_facts, next_missing_fact, normalize_fact_response


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


def test_single_reading_sets_single_reading_context():
    facts = fallback_facts("115/79")
    assert facts["reading_dates"] == "single reading"


def test_unknown_setting_routes_to_pos_code():
    facts = {"_scenario_mode": True, "reading_values": ["115/79"], "reading_dates": "single reading", "care_setting": "UNKNOWN"}
    assert next_missing_fact("reading_selection", facts, [], True) == "pos_code"


def test_unrelated_text_does_not_satisfy_date_question():
    valid, value, _ = normalize_fact_response("reading_dates", "the above is systolic and diastolic")
    assert not valid
    assert value is None


def test_not_sure_is_recorded_as_unknown():
    valid, value, _ = normalize_fact_response("care_setting", "not sure")
    assert valid
    assert value == "UNKNOWN"
