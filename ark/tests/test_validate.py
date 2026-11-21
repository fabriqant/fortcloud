import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

import yaml

from fortcloud_ark import core, validate

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
    path.write_text(yaml.safe_dump(document, sort_keys=False, allow_unicode=True), encoding="utf-8")


class ValidateTests(unittest.TestCase):
    def test_example_model_is_valid_with_warnings(self):
        model, errors, warnings = validate.collect(core.DEFAULT_MODEL, today=TODAY)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 7)
        self.assertTrue(any("129 days old" in warning for warning in warnings))
        self.assertTrue(any("ransomware" in warning for warning in warnings))

    def test_missing_reference_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(services):
                services[0]["assets"].append("ghost-asset")

            rewrite(model_dir, "services.yaml", "services", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("ghost-asset" in error for error in errors))

    def test_p0_asset_without_backup_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(backups):
                backups[:] = [item for item in backups if item["asset"] != "pg-core"]

            rewrite(model_dir, "backups.yaml", "backups", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("no backup policy" in error for error in errors))

    def test_p0_backup_must_be_immutable(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(backups):
                backups[0]["immutable"] = False

            rewrite(model_dir, "backups.yaml", "backups", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("not immutable" in error for error in errors))

    def test_schedule_longer_than_rpo_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(backups):
                backups[0]["schedule"] = "1h"
                backups[0]["type"] = "snapshot"

            rewrite(model_dir, "backups.yaml", "backups", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("cannot satisfy RPO" in error for error in errors))

    def test_measured_rto_over_target_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(restores):
                restores[0]["measured_rto"] = "45m"

            rewrite(model_dir, "restores.yaml", "restores", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("measured RTO" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
