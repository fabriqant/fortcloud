import json
import unittest
from datetime import date

from fortcloud_crucible import core, render

TODAY = date(2026, 11, 21)


class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = core.load_model(core.DEFAULT_MODEL)

    def test_scenario_plan_proves_controlled_first(self):
        document = render.build_scenarios(self.model, TODAY)
        self.assertIn("ex-restore-sandbox", document)
        self.assertIn("ex-restore-prod", document)
        self.assertIn("Controlled", document)
        self.assertIn("AT RISK", document)
        self.assertIn("30m", document)

    def test_roles_matrix_names_the_four_roles(self):
        document = render.build_roles(self.model, TODAY)
        self.assertIn("Coordinator", document)
        self.assertIn("Operator", document)
        self.assertIn("Communicator", document)
        self.assertIn("Verifier", document)
        self.assertIn("Alice Martin", document)

    def test_communication_plan_reports_gaps(self):
        document = render.build_communication(self.model, TODAY)
        self.assertIn("30m", document)
        self.assertIn("war-room", document)
        self.assertIn("exec-bridge", document)
        self.assertIn("Gap", document)

    def test_verification_and_status_are_machine_readable(self):
        verification = render.build_verification(self.model, TODAY)
        self.assertIn("chk-failover-data", verification)
        self.assertIn("VERIFIED", verification)
        self.assertIn("PENDING", verification)
        payload = json.loads(render.build_status(self.model, TODAY))
        self.assertEqual(payload["tool"], "fortcloud-crucible")
        self.assertEqual(payload["summary"]["scenarios"], 6)
        self.assertEqual(payload["summary"]["controlled_environments"], 2)
        self.assertEqual(payload["errors"], [])
        self.assertEqual(len(payload["warnings"]), 6)


if __name__ == "__main__":
    unittest.main()
