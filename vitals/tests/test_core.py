import unittest
from datetime import date

from fortcloud_vitals import core


class CoreTests(unittest.TestCase):
    def test_parse_duration(self):
        self.assertEqual(core.parse_duration("0"), 0)
        self.assertEqual(core.parse_duration("150ms"), 150)
        self.assertEqual(core.parse_duration("1m30s"), 90_000)
        self.assertEqual(core.parse_duration("30d"), 2_592_000_000)
        self.assertIsNone(core.parse_duration("monthly"))

    def test_format_duration_roundtrip(self):
        for milliseconds in (0, 150, 1234, 90_000, 2_592_000):
            self.assertEqual(
                core.parse_duration(core.format_duration(milliseconds)), milliseconds
            )

    def test_format_duration_rounded(self):
        self.assertEqual(core.format_duration_rounded(259_200), "4m19s")
        self.assertEqual(core.format_duration_rounded(1_209_600), "20m10s")

    def test_load_model_counts(self):
        model = core.load_model(core.DEFAULT_MODEL)
        self.assertEqual(len(model["services"]), 4)
        self.assertEqual(len(model["signals"]), 7)
        self.assertEqual(len(model["objectives"]), 7)
        self.assertEqual(len(model["checks"]), 7)

    def test_percent_metrics(self):
        model = core.load_model(core.DEFAULT_MODEL)
        metrics = core.objective_metrics(
            model, core.objective_map(model)["slo-checkout-avail"]
        )
        # 99.9% over 30 days = 43m12s; alert at 99.95% uses half of it.
        self.assertEqual(metrics["budget_ms"], 2_592_000)
        self.assertEqual(metrics["budget_used"], 0.5)
        self.assertEqual(metrics["max_interval_ms"], 259_200)

    def test_duration_metrics_and_helpers(self):
        model = core.load_model(core.DEFAULT_MODEL)
        objectives = core.objective_map(model)
        metrics = core.objective_metrics(model, objectives["slo-checkout-latency"])
        self.assertEqual(metrics["margin_ms"], 60)
        self.assertEqual(metrics["margin_ratio"], 0.2)
        self.assertEqual(len(core.objectives_for_service(model, "checkout")), 3)
        self.assertEqual(len(core.objectives_for_signal(model, "sig-auth-availability")), 1)
        self.assertEqual(
            core.age_days("2026-07-15", date(2026, 11, 21)), 129
        )
        self.assertEqual(core.format_percent(99.0), "99")


if __name__ == "__main__":
    unittest.main()
