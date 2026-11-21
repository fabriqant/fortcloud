import unittest

from fortcloud_ballast import core


class CoreTests(unittest.TestCase):
    def test_parse_duration_milliseconds(self):
        self.assertEqual(core.parse_duration("0"), 0)
        self.assertEqual(core.parse_duration("150ms"), 150)
        self.assertEqual(core.parse_duration("2s"), 2000)
        self.assertEqual(core.parse_duration("1m30s"), 90_000)
        self.assertIsNone(core.parse_duration("soon"))

    def test_format_duration_is_reusable_as_input(self):
        for milliseconds in (0, 150, 1234, 2000, 90_000, 3_600_000, 86_400_000):
            text = core.format_duration(milliseconds)
            self.assertEqual(core.parse_duration(text), milliseconds)

    def test_load_model_counts(self):
        model = core.load_model(core.DEFAULT_MODEL)
        self.assertEqual(len(model["services"]), 4)
        self.assertEqual(len(model["dependencies"]), 7)
        self.assertEqual(len(model["policies"]), 7)
        self.assertEqual(len(model["flows"]), 4)

    def test_worst_case_includes_retries_and_backoff(self):
        policy = {
            "timeout": "300ms",
            "retries": 3,
            "backoff": "40ms",
            "backoff_multiplier": 2,
        }
        # 300 * 4 + (40 + 80 + 160)
        self.assertEqual(core.worst_case_ms(policy), 1480)

    def test_flow_totals_and_budgets(self):
        model = core.load_model(core.DEFAULT_MODEL)
        flows = core.flow_map(model)
        self.assertEqual(core.flow_total_ms(model, flows["flow-checkout"]), 1500)
        self.assertEqual(core.flow_total_ms(model, flows["flow-browse"]), 1730)
        self.assertEqual(core.budget_ms(model, flows["flow-checkout"]), 3000)
        self.assertAlmostEqual(core.utilization(model, flows["flow-browse"]), 0.865, places=2)

    def test_dominant_step(self):
        model = core.load_model(core.DEFAULT_MODEL)
        dominant = core.dominant_step(model, core.flow_map(model)["flow-browse"])
        self.assertEqual(dominant[0]["dependency"], "dep-catalog")
        self.assertGreater(dominant[1], 0.7)


if __name__ == "__main__":
    unittest.main()
