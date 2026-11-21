import json
import unittest

from fortcloud_ballast import core, render


class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = core.load_model(core.DEFAULT_MODEL)

    def test_budget_reports_headroom_and_at_risk(self):
        document = render.build_budget(self.model)
        self.assertIn("`flow-checkout`", document)
        self.assertIn("1s500ms", document)
        self.assertIn("AT RISK", document)
        self.assertIn("**Largest step:** `dep-catalog`", document)

    def test_policy_matrix_lists_guards(self):
        document = render.build_policies(self.model)
        self.assertIn("`pol-payment`", document)
        self.assertIn("payment-pool", document)
        self.assertIn("**none**", document)
        self.assertIn("retries without jitter", document)

    def test_plan_contains_gaps_and_definition_of_done(self):
        document = render.build_plan(self.model)
        self.assertIn("## flow:flow-browse", document)
        self.assertIn("## policy:pol-pricing", document)
        self.assertIn("## Definition of done", document)

    def test_status_json_is_machine_readable(self):
        payload = json.loads(render.build_status(self.model))
        self.assertEqual(payload["tool"], "fortcloud-ballast")
        self.assertEqual(payload["summary"]["flows"], 4)
        self.assertEqual(payload["summary"]["policies"], 7)
        self.assertEqual(payload["errors"], [])
        self.assertEqual(len(payload["warnings"]), 7)
        checkout = next(item for item in payload["flows"] if item["id"] == "flow-checkout")
        self.assertEqual(checkout["worst_case_ms"], 1500)
        self.assertEqual(checkout["status"], "OK")


if __name__ == "__main__":
    unittest.main()
