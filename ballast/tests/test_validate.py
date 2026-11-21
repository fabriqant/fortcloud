import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from fortcloud_ballast import core, validate


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
        model, errors, warnings = validate.collect(core.DEFAULT_MODEL)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 7)
        self.assertTrue(any("thundering herd" in warning for warning in warnings))
        self.assertTrue(any("74% of the latency budget" in warning for warning in warnings))

    def test_dangling_reference_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(flows):
                flows[0]["steps"][0]["dependency"] = "ghost-dependency"

            rewrite(model_dir, "flows.yaml", "flows", change)
            _, errors, _ = validate.collect(model_dir)
            self.assertTrue(any("ghost-dependency" in error for error in errors))

    def test_worst_case_over_budget_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(services):
                services[0]["latency_budget"] = "1s"

            rewrite(model_dir, "services.yaml", "services", change)
            _, errors, _ = validate.collect(model_dir)
            self.assertTrue(any("exceeds the 1s latency budget" in error for error in errors))

    def test_retry_on_non_idempotent_write_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(policies):
                for policy in policies:
                    if policy["id"] == "pol-payment":
                        policy["retries"] = 2

            rewrite(model_dir, "policies.yaml", "policies", change)
            _, errors, _ = validate.collect(model_dir)
            self.assertTrue(any("non-idempotent write" in error for error in errors))

    def test_p0_dependency_without_breaker_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(policies):
                for policy in policies:
                    if policy["id"] == "pol-auth":
                        policy["circuit_breaker"] = False

            rewrite(model_dir, "policies.yaml", "policies", change)
            _, errors, _ = validate.collect(model_dir)
            self.assertTrue(any("no circuit breaker on a P0" in error for error in errors))

    def test_policy_target_must_match_step_dependency(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(flows):
                flows[0]["steps"][1]["policy"] = "pol-auth"

            rewrite(model_dir, "flows.yaml", "flows", change)
            _, errors, _ = validate.collect(model_dir)
            self.assertTrue(any("targets" in error and "but the step uses" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
