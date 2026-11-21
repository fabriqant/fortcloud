import unittest
from datetime import date

from fortcloud_custodian import core

TODAY = date(2026, 11, 21)


class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = core.load_model(core.DEFAULT_MODEL)

    def test_load_model_counts(self):
        self.assertEqual(len(core.env_map(self.model)), 3)
        self.assertEqual(len(core.principal_map(self.model)), 6)
        self.assertEqual(len(core.grant_map(self.model)), 9)
        self.assertEqual(len(core.secret_map(self.model)), 6)
        self.assertEqual(len(core.pipeline_map(self.model)), 4)
        self.assertEqual(len(core.sink_map(self.model)), 2)
        self.assertEqual(len(core.operation_map(self.model)), 5)

    def test_dates_and_ages(self):
        self.assertEqual(core.age_days("2026-11-18", TODAY), 3)
        self.assertEqual(core.days_until("2027-06-30", TODAY), 221)
        self.assertIsNone(core.parse_date("not-a-date"))

    def test_environment_helpers(self):
        self.assertTrue(core.is_restricted(self.model, "prod"))
        self.assertFalse(core.is_restricted(self.model, "staging"))
        self.assertEqual(len(core.grants_for_environment(self.model, "prod")), 3)
        self.assertEqual(len(core.secrets_for_environment(self.model, "prod")), 3)
        self.assertEqual(len(core.pipelines_for_environment(self.model, "prod")), 3)

    def test_least_privilege_helpers(self):
        self.assertTrue(core.is_wildcard("*:*"))
        self.assertFalse(core.is_wildcard("read:logs"))
        self.assertTrue(core.is_elevated("admin"))
        self.assertFalse(core.is_elevated("deployer"))
        self.assertTrue(core.crosses_environment("proj/dev/*", "prod", ["dev"]))
        self.assertFalse(core.crosses_environment("proj/prod/checkout/*", "prod", ["dev"]))

    def test_principal_grant_and_audit_helpers(self):
        self.assertEqual(len(core.grants_for_principal(self.model, "alice")), 4)
        self.assertEqual(len(core.operations_for_kind(self.model, "deploy")), 1)
        self.assertEqual(len(core.operations_for_kind(self.model, "grant_change")), 1)
        self.assertEqual(core.evidence_age_days({"last_evidence": "2026-11-19"}, TODAY), 2)

    def test_rotation_and_rollback_helpers(self):
        secrets = core.secret_map(self.model)
        self.assertEqual(
            core.secret_age_days(secrets["sec-reporting-export-key"], TODAY), 265
        )
        pipelines = core.pipeline_map(self.model)
        self.assertEqual(
            core.rollback_age_days(pipelines["pipe-reporting-prod"], TODAY), 324
        )


if __name__ == "__main__":
    unittest.main()
