import unittest
from datetime import date

from fortcloud_ark import core


class CoreTests(unittest.TestCase):
    def test_parse_duration(self):
        self.assertEqual(core.parse_duration("0"), 0)
        self.assertEqual(core.parse_duration("30s"), 30)
        self.assertEqual(core.parse_duration("1h30m"), 5400)
        self.assertEqual(core.parse_duration("24h"), 86400)
        self.assertIsNone(core.parse_duration("daily"))

    def test_format_duration_is_reusable_as_input(self):
        for seconds in (0, 30, 150, 3600, 5400, 132, 86400):
            text = core.format_duration(seconds)
            self.assertEqual(core.parse_duration(text), seconds)

    def test_load_model_counts(self):
        model = core.load_model(core.DEFAULT_MODEL)
        self.assertEqual(len(model["assets"]), 8)
        self.assertEqual(len(model["backups"]), 8)
        self.assertEqual(len(model["restores"]), 7)
        self.assertEqual(len(model["services"]), 4)

    def test_targets_for_asset_use_tightest_service(self):
        model = core.load_model(core.DEFAULT_MODEL)
        self.assertEqual(core.targets_for_asset(model, "pg-core"), (1800, 300))
        self.assertEqual(core.targets_for_asset(model, "vault-secrets"), (900, 0))

    def test_helpers(self):
        model = core.load_model(core.DEFAULT_MODEL)
        self.assertEqual(len(core.backups_for_asset(model, "pg-core")), 1)
        self.assertEqual(len(core.restores_for_asset(model, "pg-core")), 2)
        self.assertEqual(len(core.services_using_asset(model, "obj-lake")), 1)
        self.assertIn("pg-core", core.covered_assets(model))

    def test_age_days(self):
        self.assertEqual(core.age_days("2026-11-05", date(2026, 11, 21)), 16)
        self.assertIsNone(core.age_days("nope", date(2026, 11, 21)))


if __name__ == "__main__":
    unittest.main()
