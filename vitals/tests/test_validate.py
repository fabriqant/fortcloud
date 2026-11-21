import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

import yaml

from fortcloud_vitals import core, validate

TODAY = date(2026, 11, 21)


def copy_model(destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    for filename, _ in core.FILES.values():
        shutil.copy(core.DEFAULT_MODEL / filename, destination / filename)
    return destination


def rewrite(directory: Path, filename: str, key: str, transform) -> None:
    path = directory / filename
    document = core.load_yaml(path)
    transform(document[key])
    path.write_text(
        yaml.safe_dump(document, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )


class ValidateTests(unittest.TestCase):
    def test_example_model_is_valid_with_warnings(self):
        model, errors, warnings = validate.collect(core.DEFAULT_MODEL, today=TODAY)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 7)
        self.assertTrue(any("80% of the error budget" in warning for warning in warnings))
        self.assertTrue(any("129 days old" in warning for warning in warnings))

    def test_alert_not_tighter_than_target_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(objectives):
                objectives[0]["alert_threshold"] = 99.9

            rewrite(model_dir, "objectives.yaml", "objectives", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("is not tighter" in error for error in errors))

    def test_signal_kind_mismatch_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(objectives):
                objectives[0]["kind"] = "latency"
                objectives[0]["target"] = "300ms"
                objectives[0]["alert_threshold"] = "240ms"

            rewrite(model_dir, "objectives.yaml", "objectives", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("does not match" in error for error in errors))

    def test_p0_without_data_quality_objective_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(objectives):
                objectives[:] = [
                    item
                    for item in objectives
                    if not (
                        item["service"] == "checkout"
                        and item["kind"] in core.DATA_QUALITY_KINDS
                    )
                ]

            rewrite(model_dir, "objectives.yaml", "objectives", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("no data-quality objective" in error for error in errors))

    def test_p0_check_without_runbook_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(checks):
                checks[0]["runbook"] = ""

            rewrite(model_dir, "checks.yaml", "checks", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("no runbook" in error for error in errors))

    def test_failed_p0_check_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(checks):
                checks[0]["result"] = "failed"

            rewrite(model_dir, "checks.yaml", "checks", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("failed check on a P0" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
