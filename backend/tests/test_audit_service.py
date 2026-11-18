
import unittest
from pathlib import Path

from app.services.audit_service import build_audit_report


class TestAuditService(unittest.TestCase):

    def setUp(self):
        self.repository_path = Path(__file__).parent

    def test_report_contains_all_sections(self):
        report = build_audit_report(self.repository_path)

        self.assertEqual(report["audit_status"], "COMPLETED")
        self.assertIn("repository", report)
        self.assertIn("scan_summary", report)
        self.assertIn("findings", report)
        self.assertIn("notices", report)
        self.assertTrue(report["read_only"])

    def test_security_findings_are_included(self):
        report = build_audit_report(self.repository_path)

        security_findings = [
            finding
            for finding in report["findings"]
            if finding["category"] == "SECURITY"
        ]

        self.assertGreater(len(security_findings), 0)
        self.assertTrue(
            all(
                finding["source"] == "security_scanner"
                for finding in security_findings
            )
        )

    def test_finding_counts_are_consistent(self):
        report = build_audit_report(self.repository_path)

        summary = report["scan_summary"]

        self.assertEqual(
            summary["total_findings"],
            len(report["findings"])
        )

        self.assertEqual(
            summary["security_findings"]
            + summary["quality_findings"],
            summary["total_findings"]
        )

    def test_severity_summary_is_consistent(self):
        report = build_audit_report(self.repository_path)

        calculated_total = sum(
            report["scan_summary"]["severity_summary"].values()
        )

        self.assertEqual(
            calculated_total,
            report["scan_summary"]["total_findings"]
        )

    def test_invalid_repository_path(self):
        with self.assertRaises(FileNotFoundError):
            build_audit_report(
                self.repository_path / "does_not_exist"
            )


if __name__ == "__main__":
    unittest.main()
