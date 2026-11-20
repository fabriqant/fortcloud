import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

import yaml

from fortcloud_atlas import core, validate

EXAMPLE_MODEL = Path(__file__).resolve().parents[1] / "examples" / "hybrid-multicloud" / "model"
TODAY = date(2026, 11, 20)


class ValidateTests(unittest.TestCase):
    def test_example_model_is_valid_with_warnings(self):
        model, errors, warnings = validate.collect(EXAMPLE_MODEL, today=TODAY)
        self.assertEqual(errors, [])
        self.assertEqual(len(model["components"]), 12)
        self.assertTrue(warnings)
        self.assertTrue(any("days ago" in warning for warning in warnings))

    def test_missing_reference_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = Path(directory) / "model"
            model_dir.mkdir()
            for filename, _ in core.FILES.values():
                shutil.copy(EXAMPLE_MODEL / filename, model_dir / filename)

            dependencies_path = model_dir / "dependencies.yaml"
            dependencies = core.load_yaml(dependencies_path)
            dependencies["dependencies"][0]["to"] = "ghost-component"
            dependencies_path.write_text(
                yaml.safe_dump(dependencies, sort_keys=False, allow_unicode=True), encoding="utf-8"
            )

            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("ghost-component" in error for error in errors))

    def test_p0_single_instance_without_risk_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = Path(directory) / "model"
            model_dir.mkdir()
            for filename, _ in core.FILES.values():
                shutil.copy(EXAMPLE_MODEL / filename, model_dir / filename)

            risks_path = model_dir / "risks.yaml"
            risks = core.load_yaml(risks_path)
            risks["risks"] = [
                risk for risk in risks["risks"] if "dns-global" not in risk["components"]
            ]
            risks["risks"].append(
                {
                    "id": "R-999",
                    "title": "Remplaçant factice",
                    "components": ["obj-lake"],
                    "flows": ["order-to-cash"],
                    "failure_mode": "Mode de défaillance de test",
                    "likelihood": 1,
                    "impact": 1,
                    "status": "open",
                    "owner": "test-team",
                    "mitigations": [],
                    "action": "Action de test",
                    "target_date": "2026-12-31",
                }
            )
            risks_path.write_text(
                yaml.safe_dump(risks, sort_keys=False, allow_unicode=True), encoding="utf-8"
            )

            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("dns-global" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
