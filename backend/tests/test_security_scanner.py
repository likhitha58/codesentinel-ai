
import tempfile
import unittest
from pathlib import Path

from app.scanners.security_scanner import scan_file


class TestSecurityScanner(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def scan_source(self, source):
        file_path = self.root / "sample.py"
        file_path.write_text(source, encoding="utf-8")
        return scan_file(file_path, self.root)

    def test_detects_hardcoded_credential(self):
        findings = self.scan_source(
            "pass" + 'word = "demo-secret-value-123"'
        )

        rule_ids = [f["rule_id"] for f in findings]

        self.assertIn("SEC001", rule_ids)

        # Secret values must not appear in evidence.
        credential_finding = next(
            f for f in findings if f["rule_id"] == "SEC001"
        )
        self.assertNotIn(
            "pass" + 'word = "demo-secret-value-123"',
            credential_finding["evidence"]
        )

    def test_detects_multiline_sql_injection_pattern(self):
        findings = self.scan_source(
            (
    "def get_user(cursor, user_id):\n"
    "    cursor.exec" + "ute(\n"
    '        "SELECT * FROM users WHERE id = " + user_id\n'
    "    )\n"
)
        )

        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("SEC002", rule_ids)

    def test_detects_unsafe_eval(self):
        findings = self.scan_source(
            "result = ev" + "al(user_input)"
        )

        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("SEC003", rule_ids)

    def test_detects_unsafe_deserialization(self):
        findings = self.scan_source(
            "data = pick" + "le.loads(payload)"
        )

        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("SEC006", rule_ids)

    def test_clean_code_returns_no_findings(self):
        findings = self.scan_source(
            '''
def add_numbers(a, b):
    return a + b
'''
        )

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
