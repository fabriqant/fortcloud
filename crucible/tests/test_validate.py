import copy
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

import yaml

from fortcloud_crucible import core, validate

TODAY = date(2026, 11, 21)

FILES = (
    "environments.yaml",
    "scenarios.yaml",
    "communication.yaml",
    "verification.yaml",
)


def copy_model(destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    for filename in FILES:
        shutil.copy(core.DEFAULT_MODEL / filename, destination / filename)
    return destination


def rewrite(directory: Path, filename: str, root_key: str | None, transform) -> None:
    path = directory / filename
    document = core.load_yaml(path)
    target = document if root_key is None else document[root_key]
    transform(target)
    path.write_text(
        yaml.safe_dump(document, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )


class ValidateTests(unittest.TestCase):
    def test_example_model_is_valid_with_warnings(self):
        model, errors, warnings = validate.collect(core.DEFAULT_MODEL, today=TODAY)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 6)
        self.assertTrue(any("exercise window 6h exceeds 4h" in w for w in warnings))
        self.assertTrue(any("exercise failed" in w for w in warnings))
        self.assertTrue(any("status updates every 30m" in w for w in warnings))

    def test_prod_scenario_needs_controlled_rehearsal(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(scenarios):
                for scenario in scenarios:
                    if scenario["id"] == "ex-recovery-sandbox":
                        scenario["status"] = "failed"

            rewrite(model_dir, "scenarios.yaml", "scenarios", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(
                any(
                    "no passed 'recovery' exercise in a controlled environment" in error
                    for error in errors
                )
            )

    def test_missing_role_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(scenarios):
                for scenario in scenarios:
                    if scenario["id"] == "ex-failover-prod":
                        scenario["assignments"] = [
                            item
                            for item in scenario["assignments"]
                            if item["role"] != "verifier"
                        ]

            rewrite(model_dir, "scenarios.yaml", "scenarios", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("no 'verifier' assigned" in error for error in errors))

    def test_unknown_participant_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(scenarios):
                scenarios[0]["assignments"][0]["person"] = "ghost"

            rewrite(model_dir, "scenarios.yaml", "scenarios", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("participant 'ghost' not found" in error for error in errors))

    def test_invalid_duration_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change(scenarios):
                scenarios[0]["duration"] = "two weeks"

            rewrite(model_dir, "scenarios.yaml", "scenarios", change)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("invalid duration" in error for error in errors))

    def test_passed_exercise_needs_both_checks_and_signoff(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def remove_check(checks):
                checks[:] = [
                    item
                    for item in checks
                    if item["id"] != "chk-failover-data"
                ]

            def remove_signoff(signoffs):
                signoffs[:] = [
                    item
                    for item in signoffs
                    if item["scenario"] != "ex-failover-staging"
                ]

            rewrite(model_dir, "verification.yaml", "checks", remove_check)
            rewrite(model_dir, "verification.yaml", "signoffs", remove_signoff)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(
                any("no passed 'data' verification" in error for error in errors)
            )
            self.assertTrue(
                any("no approved verifier sign-off" in error for error in errors)
            )

    def test_failed_check_and_unknown_channel(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change_checks(checks):
                for check in checks:
                    if check["id"] == "chk-failover-service":
                        check["result"] = "failed"

            def change_scenarios(scenarios):
                for scenario in scenarios:
                    if scenario["id"] == "ex-failover-prod":
                        scenario["channel"] = "ghost"

            rewrite(model_dir, "verification.yaml", "checks", change_checks)
            rewrite(model_dir, "scenarios.yaml", "scenarios", change_scenarios)
            _, errors, _ = validate.collect(model_dir, today=TODAY)
            self.assertTrue(any("verification failed on" in error for error in errors))
            self.assertTrue(any("channel 'ghost' not found" in error for error in errors))

    def test_communication_coverage_and_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = copy_model(Path(directory) / "model")

            def change_stakeholders(stakeholders):
                for stakeholder in stakeholders:
                    stakeholder["notify"] = [
                        item for item in stakeholder["notify"] if item != "start"
                    ]

            def change_scenarios(scenarios):
                scenarios.append(copy.deepcopy(scenarios[0]))

            rewrite(model_dir, "communication.yaml", "stakeholders", change_stakeholders)
            rewrite(model_dir, "scenarios.yaml", "scenarios", change_scenarios)
            _, errors, warnings = validate.collect(model_dir, today=TODAY)
            self.assertTrue(
                any("no stakeholder is notified at 'start'" in w for w in warnings)
            )
            self.assertTrue(any("used 2 times" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
