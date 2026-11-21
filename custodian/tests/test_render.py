import json
import unittest
from datetime import date

from fortcloud_custodian import core, render

TODAY = date(2026, 11, 21)


class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = core.load_model(core.DEFAULT_MODEL)

    def test_access_matrix_reports_least_privilege(self):
        document = render.build_access(self.model, TODAY)
        self.assertIn("grant-alice-overprivileged", document)
        self.assertIn("AT RISK", document)
        self.assertIn("## Environments", document)
        self.assertIn("admin", document)

    def test_secret_inventory_uses_references(self):
        document = render.build_secrets(self.model, TODAY)
        self.assertIn("vault://prod/checkout/db", document)
        self.assertIn("265d", document)
        self.assertIn("Kubernetes Secret", document)

    def test_change_control_reviews_and_rollback(self):
        document = render.build_changes(self.model, TODAY)
        self.assertIn("pipe-reporting-prod", document)
        self.assertIn("1 approver(s)", document)
        self.assertIn("manual", document)

    def test_audit_and_status_are_machine_readable(self):
        audit = render.build_audit(self.model, TODAY)
        self.assertIn("sink-siem", audit)
        self.assertIn("## Sensitive operations", audit)
        payload = json.loads(render.build_status(self.model, TODAY))
        self.assertEqual(payload["tool"], "fortcloud-custodian")
        self.assertEqual(payload["summary"]["environments"], 3)
        self.assertEqual(payload["summary"]["grants"], 9)
        self.assertEqual(payload["errors"], [])
        self.assertEqual(len(payload["warnings"]), 7)


if __name__ == "__main__":
    unittest.main()
