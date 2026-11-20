import unittest
from datetime import date
from pathlib import Path

from fortcloud_atlas import core

EXAMPLE_MODEL = Path(__file__).resolve().parents[1] / "examples" / "hybrid-multicloud" / "model"


class CoreTests(unittest.TestCase):
    def test_load_example_model(self):
        model = core.load_model(EXAMPLE_MODEL)
        self.assertEqual(len(model["components"]), 12)
        self.assertEqual(len(model["dependencies"]), 20)
        self.assertEqual(len(model["flows"]), 4)
        self.assertEqual(len(model["risks"]), 8)

    def test_spof_detection(self):
        model = core.load_model(EXAMPLE_MODEL)
        components = {item["id"]: item for item in model["components"]}
        self.assertTrue(core.is_spof(components["dns-global"]))
        self.assertFalse(core.is_spof(components["pg-core"]))
        self.assertTrue(core.is_single_region_p0(components["kafka-bus"]))
        self.assertFalse(core.is_single_region_p0(components["obj-lake"]))

    def test_risk_scoring(self):
        self.assertEqual(core.risk_score({"likelihood": 4, "impact": 4}), 16)
        self.assertEqual(core.severity(16), "critique")
        self.assertEqual(core.severity(10), "élevé")
        self.assertEqual(core.severity(3), "faible")

    def test_restore_test_age(self):
        today = date(2026, 11, 20)
        self.assertEqual(core.test_age_days("2026-11-18", today), 2)
        self.assertIsNone(core.test_age_days(None, today))
        self.assertIsNone(core.test_age_days("not-a-date", today))


if __name__ == "__main__":
    unittest.main()
