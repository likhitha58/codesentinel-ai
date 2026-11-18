
import unittest

from app.agents.audit_agent import run_audit_agent


class TestAuditAgent(unittest.TestCase):

    def setUp(self):
        self.sample_report = {
            "audit_status": "COMPLETED",
            "repository": {"repository": "sample-project"},
            "scan_summary": {
                "total_findings": 2,
                "security_findings": 2,
                "quality_findings": 0,
            },
            "findings": [
                {
                    "rule_id": "SEC001",
                    "title": "Possible hardcoded credential",
                    "severity": "HIGH",
                    "category": "SECURITY",
                    "file": "config.py",
                    "line": 10,
                },
                {
                    "rule_id": "SEC003",
                    "title": "Unsafe dynamic evaluation",
                    "severity": "HIGH",
                    "category": "SECURITY",
                    "file": "utils.py",
                    "line": 20,
                },
            ],
        }

    def test_agent_returns_enhanced_report(self):
        result = run_audit_agent(self.sample_report)

        self.assertIn("agent_analysis", result)
        self.assertIn(
            "executive_summary",
            result["agent_analysis"],
        )

    def test_prioritizes_high_severity_findings(self):
        result = run_audit_agent(self.sample_report)

        findings = result["agent_analysis"]["prioritized_findings"]

        self.assertEqual(len(findings), 2)
        self.assertTrue(
            all(item["priority"] == "P1" for item in findings)
        )

    def test_generates_remediation_recommendations(self):
        result = run_audit_agent(self.sample_report)

        recommendations = result["agent_analysis"]["recommendations"]

        self.assertEqual(len(recommendations), 2)
        self.assertTrue(
            all(item["recommended_action"] for item in recommendations)
        )

    def test_groups_duplicate_rules(self):
        report = {
            **self.sample_report,
            "scan_summary": {
                "total_findings": 2,
                "security_findings": 2,
                "quality_findings": 0,
            },
            "findings": [
                {
                    "rule_id": "SEC001",
                    "title": "Possible hardcoded credential",
                    "severity": "HIGH",
                    "category": "SECURITY",
                    "file": "config.py",
                    "line": 10,
                },
                {
                    "rule_id": "SEC001",
                    "title": "Possible hardcoded credential",
                    "severity": "HIGH",
                    "category": "SECURITY",
                    "file": "settings.py",
                    "line": 15,
                },
            ],
        }

        result = run_audit_agent(report)
        recommendations = result["agent_analysis"]["recommendations"]

        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]["occurrences"], 2)

    def test_does_not_modify_original_report(self):
        original_findings = [
            dict(item) for item in self.sample_report["findings"]
        ]

        run_audit_agent(self.sample_report)

        self.assertEqual(
            self.sample_report["findings"],
            original_findings,
        )
        self.assertNotIn("agent_analysis", self.sample_report)


if __name__ == "__main__":
    unittest.main()
