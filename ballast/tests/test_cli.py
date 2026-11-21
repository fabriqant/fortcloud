import tempfile
import unittest
from pathlib import Path

from fortcloud_ballast import cli


class CliTests(unittest.TestCase):
    def test_check_generates_four_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            exit_code = cli.main(["check", "--out", directory])
            self.assertEqual(exit_code, 0)
            names = sorted(path.name for path in Path(directory).iterdir())
            self.assertEqual(
                names,
                [
                    "ballast-status.json",
                    "policy-matrix.md",
                    "resilience-plan.md",
                    "timeout-budget.md",
                ],
            )

    def test_strict_mode_fails_on_warnings(self):
        with tempfile.TemporaryDirectory() as directory:
            exit_code = cli.main(["check", "--strict", "--out", directory])
            self.assertEqual(exit_code, 1)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_validate_accepts_example_with_warnings(self):
        self.assertEqual(cli.main(["validate"]), 0)


if __name__ == "__main__":
    unittest.main()
