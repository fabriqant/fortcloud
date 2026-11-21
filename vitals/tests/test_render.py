import json
import unittest
from datetime import date

from fortcloud_vitals import core, render

TODAY = date(2026, 11, 21)


class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = core.load_model(core.DEFAULT_MODEL)

    def test_dashboard_reports_error_budget(self):
        document = render.build_dashboard(self.model, TODAY)
        self.assertIn("43m12s", document)
        self.assertIn("80% used at alert", document)
        self.assertIn("AT RISK", document)
        self.assertIn("`slo-checkout-avail`", document)

    def test_signal_catalog_lists_sources_and_objectives(self):
        document = render.build_signals(self.model, TODAY)
        self.assertIn("sig-auth-availability", document)
        self.assertIn("Datadog", document)
        self.assertIn("SQL query", document)

    def test_plan_contains_gaps_and_definition_of_done(self):
        document = render.build_plan(self.model, TODAY)
        self.assertIn("## objective:slo-auth-completeness", document)
        self.assertIn("No runbook", document)
        self.assertIn("## Definition of done", document)

    def test_status_json_is_machine_readable(self):
        payload = json.loads(render.build_status(self.model, TODAY))
        self.assertEqual(payload["tool"], "fortcloud-vitals")
        self.assertEqual(payload["summary"]["objectives"], 7)
        self.assertEqual(payload["summary"]["signals"], 7)
        self.assertEqual(payload["errors"], [])
        self.assertEqual(len(payload["warnings"]), 7)
        available = next(
            item for item in payload["objectives"] if item["id"] == "slo-checkout-avail"
        )
        self.assertEqual(available["error_budget_ms"], 2_592_000)
        self.assertEqual(available["status"], "OK")


if __name__ == "__main__":
    unittest.main()
