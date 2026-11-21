import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

import yaml

from fortcloud_failover import core, validate

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
        self.assertTrue(any("DNS TTL" in warning for warning in warnings))

    def test_missing_reference_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(services):
                services[0]["components"].append("ghost-component")

            rewrite(model_dir, "services.yaml", "services", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("ghost-component" in error for error in errors))

    def test_same_region_standby_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(topology):
                topology[1]["region"] = "eu-west-1"

            rewrite(model_dir, "topology.yaml", "topology", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("false redundancy" in error for error in errors))

    def test_switchover_over_rto_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(strategies):
                strategies[0]["promotion_time"] = "20m"

            rewrite(model_dir, "strategies.yaml", "strategies", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("exceeds the tightest RTO" in error for error in errors))

    def test_async_replication_with_rpo_zero_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(strategies):
                strategies[0]["replication"] = "async"

            rewrite(model_dir, "strategies.yaml", "strategies", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("RPO 0" in error for error in errors))

    def test_p0_component_without_strategy_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(strategies):
                strategies[:] = [item for item in strategies if item["id"] != "fo-dns"]

            rewrite(model_dir, "strategies.yaml", "strategies", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("dns-global" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
