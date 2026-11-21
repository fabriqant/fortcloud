import tempfile
import unittest
from pathlib import Path

from fortcloud_custodian import cli


class CliTests(unittest.TestCase):
    def test_check_generates_five_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            exit_code = cli.main(["check", "--out", directory])
            self.assertEqual(exit_code, 0)
            names = sorted(path.name for path in Path(directory).iterdir())
            self.assertEqual(
                names,
                [
                    "access-matrix.md",
                    "audit-trail.md",
                    "change-control.md",
                    "custodian-status.json",
                    "secret-inventory.md",
                ],
            )

    def test_single_writer_generates_one_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            exit_code = cli.main(["secrets", "--out", directory])
            self.assertEqual(exit_code, 0)
            self.assertEqual(
                [path.name for path in Path(directory).iterdir()], ["secret-inventory.md"]
            )

    def test_strict_mode_fails_on_warnings(self):
        with tempfile.TemporaryDirectory() as directory:
            exit_code = cli.main(["check", "--strict", "--out", directory])
            self.assertEqual(exit_code, 1)
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
