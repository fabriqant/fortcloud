import json
import unittest
from datetime import date

from fortcloud_failover import core, render

TODAY = date(2026, 11, 21)


class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = core.load_model(core.DEFAULT_MODEL)

    def test_matrix_reports_coverage_and_status(self):
        document = render.build_matrix(self.model, TODAY)
        self.assertIn("**8/8** P0 components covered", document)
        self.assertIn("COVERED", document)
        self.assertIn("AT RISK", document)
        self.assertIn("`fo-pg`", document)

    def test_matrix_shows_each_strategy_own_drill_age(self):
        document = render.build_matrix(self.model, TODAY)
        self.assertIn("**129 d (stale)**", document)

    def test_plan_contains_gaps_and_definition_of_done(self):
        document = render.build_plan(self.model, TODAY)
        self.assertIn("## fo-pg", document)
        self.assertIn("DNS TTL 45m exceeds RTO 30m", document)
        self.assertIn("## Definition of done", document)

    def test_drills_lists_all_strategies_and_evidence(self):
        document = render.build_drills(self.model, TODAY)
        for strategy in ("fo-idp", "fo-dns", "fo-vault", "fo-pg"):
            self.assertIn(f"## {strategy}", document)
        self.assertIn("https://ci.example.com/drills/fo-idp-42", document)

    def test_status_json_is_machine_readable(self):
        document = render.build_status(self.model, TODAY)
        payload = json.loads(document)
        self.assertEqual(payload["tool"], "fortcloud-failover")
        self.assertEqual(payload["summary"]["strategies"], 4)
        self.assertEqual(payload["summary"]["strategies_at_risk"], 3)
        self.assertEqual(payload["errors"], [])
        self.assertEqual(len(payload["warnings"]), 7)


if __name__ == "__main__":
    unittest.main()
