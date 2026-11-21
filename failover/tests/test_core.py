import unittest
from datetime import date

from fortcloud_failover import core

EXAMPLE_MODEL = core.DEFAULT_MODEL


class CoreTests(unittest.TestCase):
    def test_parse_duration(self):
        self.assertEqual(core.parse_duration("0"), 0)
        self.assertEqual(core.parse_duration("30s"), 30)
        self.assertEqual(core.parse_duration("2m"), 120)
        self.assertEqual(core.parse_duration("1h30m"), 5400)
        self.assertEqual(core.parse_duration("2m12s"), 132)
        self.assertIsNone(core.parse_duration("2 minutes"))

    def test_format_duration_is_reusable_as_input(self):
        for seconds in (0, 30, 150, 3600, 5400, 132):
            text = core.format_duration(seconds)
            self.assertEqual(core.parse_duration(text), seconds)

    def test_load_model_counts(self):
        model = core.load_model(EXAMPLE_MODEL)
        self.assertEqual(len(model["topology"]), 10)
        self.assertEqual(len(model["services"]), 3)
        self.assertEqual(len(model["strategies"]), 4)
        self.assertEqual(len(model["drills"]), 4)

    def test_switchover_and_rto_budget(self):
        model = core.load_model(EXAMPLE_MODEL)
        strategy = core.strategy_map(model)["fo-idp"]
        self.assertEqual(core.switchover_seconds(strategy), 150)
        self.assertEqual(core.rto_budget(strategy, model), 900)

    def test_covered_components(self):
        model = core.load_model(EXAMPLE_MODEL)
        covered = core.covered_components(model)
        self.assertIn("idp-oidc", covered)
        self.assertIn("pg-core-dr", covered)
        self.assertNotIn("kafka-bus", covered)

    def test_drill_age(self):
        self.assertEqual(core.drill_age_days("2026-11-05", date(2026, 11, 21)), 16)
        self.assertIsNone(core.drill_age_days("not-a-date", date(2026, 11, 21)))


if __name__ == "__main__":
    unittest.main()
