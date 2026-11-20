import tempfile
import unittest
from datetime import date
from pathlib import Path

from fortcloud_atlas import core, render

EXAMPLE_MODEL = Path(__file__).resolve().parents[1] / "examples" / "hybrid-multicloud" / "model"


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.model = core.load_model(EXAMPLE_MODEL)

    def test_graph_document(self):
        document = render.build_graph_document(self.model)
        self.assertIn("flowchart LR", document)
        self.assertIn("A depends on B", document)
        self.assertIn("dns-global", document)
        self.assertIn("Most depended-upon nodes", document)

    def test_report_document(self):
        report = render.build_report(self.model, today=date(2026, 11, 20))
        self.assertIn("RTO / RPO matrix", report)
        self.assertIn("Single points of failure", report)
        self.assertIn("R-007", report)
        self.assertIn("98 d (stale)", report)

    def test_write_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            graph_path = render.write_graph(self.model, directory)
            report_path = render.write_report(self.model, directory, today=date(2026, 11, 20))
            self.assertTrue(graph_path.exists())
            self.assertTrue(report_path.exists())
            self.assertIn("flowchart", graph_path.read_text(encoding="utf-8"))
            self.assertIn("RTO / RPO", report_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
