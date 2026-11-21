import tempfile
import unittest
from pathlib import Path

from fortcloud_crucible import cli


class CliTests(unittest.TestCase):
    def test_check_generates_five_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            exit_code = cli.main(["check", "--out", directory])
            self.assertEqual(exit_code, 0)
            names = sorted(path.name for path in Path(directory).iterdir())
            self.assertEqual(
                names,
                [
                    "communication-plan.md",
                    "crucible-status.json",
                    "roles-matrix.md",
                    "scenario-plan.md",
                    "verification-report.md",
                ],
            )

    def test_single_writer_and_strict_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            exit_code = cli.main(["roles", "--out", directory])
            self.assertEqual(exit_code, 0)
            self.assertEqual(
                [path.name for path in Path(directory).iterdir()], ["roles-matrix.md"]
            )
        with tempfile.TemporaryDirectory() as directory:
            exit_code = cli.main(["check", "--strict", "--out", directory])
            self.assertEqual(exit_code, 1)
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
