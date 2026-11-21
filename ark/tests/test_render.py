import json
import unittest
from datetime import date

from fortcloud_ark import core, render

TODAY = date(2026, 11, 21)


class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = core.load_model(core.DEFAULT_MODEL)

    def test_coverage_reports_proven_and_at_risk(self):
        document = render.build_coverage(self.model, TODAY)
        self.assertIn("**3/4** P0 assets fully proven", document)
        self.assertIn("PROVEN", document)
        self.assertIn("AT RISK", document)
        self.assertIn("`vault-secrets`", document)

    def test_evidence_compares_measured_with_targets(self):
        document = render.build_evidence(self.model, TODAY)
        self.assertIn("| `rst-pg` | `pg-core` |", document)
        self.assertIn("26m", document)
        self.assertIn("**129 d (stale)**", document)

    def test_plan_contains_gaps_and_definition_of_done(self):
        document = render.build_plan(self.model, TODAY)
        self.assertIn("## vault-secrets", document)
        self.assertIn("no ransomware or deletion restore scenario", document)
        self.assertIn("## Definition of done", document)

    def test_status_json_is_machine_readable(self):
        payload = json.loads(render.build_status(self.model, TODAY))
        self.assertEqual(payload["tool"], "fortcloud-ark")
        self.assertEqual(payload["summary"]["assets"], 8)
        self.assertEqual(payload["summary"]["restores"], 7)
        self.assertEqual(payload["errors"], [])
        self.assertEqual(len(payload["warnings"]), 7)


if __name__ == "__main__":
    unittest.main()
