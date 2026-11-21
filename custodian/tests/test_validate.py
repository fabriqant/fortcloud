import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

import yaml

from fortcloud_custodian import core, validate

TODAY = date(2026, 11, 21)

FILES = ("access.yaml", "secrets.yaml", "changes.yaml", "audit.yaml")


def copy_model(destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    for filename in FILES:
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
        self.assertTrue(any("CI principal spans" in warning for warning in warnings))
        self.assertTrue(any("9 permissions exceed" in warning for warning in warnings))

    def test_wildcard_permission_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(grants):
                grants[0]["permissions"] = ["read:code", "*:*"]

            rewrite(model_dir, "access.yaml", "grants", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("wildcard permission" in error for error in errors))

    def test_cross_environment_resource_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(grants):
                grants[2]["resources"] = ["proj/dev/checkout/*"]

            rewrite(model_dir, "access.yaml", "grants", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("targets another environment" in error for error in errors))

    def test_expired_grant_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(grants):
                grants[0]["expires"] = "2026-01-01"

            rewrite(model_dir, "access.yaml", "grants", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("expired" in error for error in errors))

    def test_secret_shared_with_prod_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(secrets):
                secrets[2]["environments"] = ["staging", "prod"]

            rewrite(model_dir, "secrets.yaml", "secrets", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("shared across 2 environments" in error for error in errors))

    def test_prod_pipeline_without_controls_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(pipelines):
                pipelines[0]["review"] = {"required": False, "approvers": 0}
                pipelines[0]["tests"] = ["unit"]
                pipelines[0]["rollback"] = {"enabled": False}

            rewrite(model_dir, "changes.yaml", "pipelines", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("review is not required" in error for error in errors))
            self.assertTrue(any("missing mandatory test" in error for error in errors))
            self.assertTrue(any("rollback is not enabled" in error for error in errors))

    def test_unlogged_operation_and_missing_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(operations):
                operations[2]["logged"] = False

            rewrite(model_dir, "audit.yaml", "operations", change)
            _, errors, warnings = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("is not logged" in error for error in errors))
            self.assertTrue(any("no audited operation for sensitive kind 'deploy'" in warning for warning in warnings))


if __name__ == "__main__":
    unittest.main()
