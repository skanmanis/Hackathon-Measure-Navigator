import tempfile
import unittest
from pathlib import Path

from engine import CheckEvaluator, DecisionTreeEngine
from navigator import NavigatorService, PHIRedactor
from app import app

ROOT=Path(__file__).resolve().parents[1]

class EngineTests(unittest.TestCase):
    def test_value_set_and_threshold_checks(self):
        evaluator=CheckEvaluator(ROOT)
        self.assertEqual(evaluator.evaluate("CHK-READING-SETTING",{"pos_code":"23"})["status"],"NOT_MET")
        self.assertEqual(evaluator.evaluate("CHK-BP-CONTROLLED",{"systolic":138,"diastolic":88})["status"],"MET")

    def test_unknown_is_open_condition(self):
        result=CheckEvaluator(ROOT).evaluate("CHK-READING-SETTING",{"pos_code":"UNKNOWN"})
        self.assertEqual(result["status"],"OPEN_CONDITION")

    def test_frailty_exclusion_has_explicit_age_gate(self):
        evaluator=CheckEvaluator(ROOT)
        self.assertEqual(evaluator.evaluate("CHK-AGE-66-PLUS",{"age":65})["status"],"NOT_MET")
        self.assertEqual(evaluator.evaluate("CHK-AGE-66-PLUS",{"age":66})["status"],"MET")

    def test_unknown_exclusion_continues_and_is_carried(self):
        tree=DecisionTreeEngine(ROOT)
        result=tree.advance("check_esrd_dx",{
            "diagnosis_code":"UNKNOWN", "code_system":"ICD-10-CM",
            "procedure_code":"ZZZ", "procedure_or_pos_code":"ZZZ",
            "pos_code":"ZZZ", "age":65
        },[])
        self.assertEqual(result["status"],"COMPLETE")
        self.assertEqual(result["conclusion"]["result"],"NO_EXCLUSION_FOUND")
        self.assertEqual(result["open_conditions"][0]["check_id"],"CHK-ESRD-DX")

    def test_tree_asks_only_required_facts(self):
        result=DecisionTreeEngine(ROOT).advance("check_reading_setting",{},[])
        self.assertEqual(result["status"],"NEEDS_MORE_INFO")
        self.assertEqual([x["name"] for x in result["required_facts"]],["pos_code"])

    def test_phi_is_masked_and_called_out(self):
        safe,types=PHIRedactor().redact("member ID ABC-123 and jane@example.com")
        self.assertNotIn("ABC-123",safe); self.assertNotIn("jane@example.com",safe)
        self.assertEqual(set(types),{"MEMBER_ID","EMAIL"})

    def test_silence_defaults_to_no_confirmation(self):
        service=NavigatorService(ROOT)
        result=service.start("Does an inpatient BP reading count?")
        with service.store.connect() as db:
            state=db.execute("SELECT outcome_state FROM sessions WHERE id=?",(result["session_id"],)).fetchone()[0]
        self.assertEqual(state,"NO_CONFIRMATION")

    def test_faq_library_and_downloads(self):
        client=app.test_client()
        self.assertEqual(client.get("/faqs").status_code,200)
        csv_response=client.get("/api/faqs/download?format=csv")
        self.assertEqual(csv_response.status_code,200)
        self.assertIn("text/csv",csv_response.content_type)
        csv_response.close()

    def test_home_loads_versioned_assets_and_faq_panel(self):
        response=app.test_client().get("/")
        html=response.get_data(as_text=True)
        self.assertIn("Relevant FAQs",html)
        self.assertIn("styles.css?v=3",html)
        self.assertIn('id="side-rail" hidden',html)
        self.assertIn('id="trace-dialog"',html)
        self.assertIn('id="trace-button"',html)

    def test_style_prototypes_and_synchronized_faq_theme(self):
        client=app.test_client()
        self.assertEqual(client.get("/style-lab").status_code,200)
        for theme in ("clinical","enterprise","calm","coastal","indigo","sand","slate","navy"):
            self.assertEqual(client.get(f"/prototype/{theme}").status_code,200)
        faq_html=client.get("/faqs").get_data(as_text=True)
        self.assertIn("theme-v2.css",faq_html)
        self.assertIn("v=4",faq_html)

    def test_package_year_is_mandatory_and_validated(self):
        service=NavigatorService(ROOT)
        self.assertTrue(service.packages.resolve("SYN-CBP",2026).exists())
        with self.assertRaises(ValueError): service.packages.resolve("SYN-CBP",2027)

    def test_trace_and_governed_intent_are_returned(self):
        result=NavigatorService(ROOT).start("Does an inpatient BP reading count?",measure_id="SYN-CBP",measurement_year=2026)
        self.assertEqual(result["answer_trace"]["intent"]["intent"],"NUMERATOR_READING")
        self.assertEqual(result["answer_trace"]["source_precedence"][0],"SPECIFICATION")

    def test_source_conflict_creates_escalation(self):
        service=NavigatorService(ROOT)
        result=service.report_conflict(None,"SQL","SQL threshold differs from specification")
        self.assertEqual(result["authoritative_source"],"SPECIFICATION")
        self.assertEqual(result["status"],"OPEN")

    def test_specific_same_day_reading_question_bypasses_unrelated_faq(self):
        result=NavigatorService(ROOT).start("There are two readings on the same day: 142/86 and 136/92. Is the member compliant?")
        self.assertEqual(result["stage"],"DOCUMENT_CLARIFICATION")
        self.assertEqual(result["faqs"],[])
        self.assertEqual(result["conclusion"]["result"],"NUMERATOR_COMPLIANT")
        self.assertEqual(result["trace"][0]["selected"],{"systolic":136,"diastolic":86})

    def test_generic_faq_overlap_does_not_count_as_close_match(self):
        service=NavigatorService(ROOT)
        matches=service.search_faqs("two readings on the same day lowest value")
        self.assertEqual(matches,[])

if __name__=="__main__": unittest.main()
