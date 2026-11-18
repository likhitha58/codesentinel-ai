
import json
import tempfile
import unittest
from pathlib import Path

from app.services.audit_service import build_audit_report
from app.services.report_exporter import (
    export_audit_report,
    generate_markdown_report,
)


class TestReportExporter(unittest.TestCase):

    def setUp(self):
        self.report = build_audit_report(
            Path(__file__).parent
        )

    def test_generates_markdown(self):
        markdown = generate_markdown_report(self.report)

        self.assertIn("# CodeSentinel AI", markdown)
        self.assertIn("## 2. Scan Summary", markdown)
        self.assertIn("## 3. Findings", markdown)

    def test_exports_json_and_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            files = export_audit_report(
                self.report,
                output_dir=temp_dir,
            )

            self.assertIn("json", files)
            self.assertIn("markdown", files)

            json_path = Path(files["json"])
            markdown_path = Path(files["markdown"])

            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())

            with json_path.open(encoding="utf-8") as file:
                saved_report = json.load(file)

            self.assertEqual(
                saved_report["scan_summary"]["total_findings"],
                self.report["scan_summary"]["total_findings"],
            )

    def test_exports_only_requested_format(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            files = export_audit_report(
                self.report,
                output_dir=temp_dir,
                formats=("json",),
            )

            self.assertEqual(list(files.keys()), ["json"])

    def test_rejects_unsupported_format(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ValueError):
                export_audit_report(
                    self.report,
                    output_dir=temp_dir,
                    formats=("pdf",),
                )

    def test_markdown_includes_agent_analysis(self):
        from app.agents.audit_agent import run_audit_agent

        enhanced_report = run_audit_agent(self.report)
        markdown = generate_markdown_report(enhanced_report)

        self.assertIn("## 4. Agent Analysis", markdown)
        self.assertIn("Executive Summary", markdown)
        self.assertIn("Remediation Recommendations", markdown)


if __name__ == "__main__":
    unittest.main()
