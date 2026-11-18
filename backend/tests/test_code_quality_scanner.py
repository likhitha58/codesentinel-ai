
import tempfile
import unittest
from pathlib import Path

from app.scanners.code_quality_scanner import (
    scan_file,
    scan_repository
)


class TestCodeQualityScanner(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def scan_source(self, source):
        file_path = self.root / "sample.py"
        file_path.write_text(source, encoding="utf-8")
        return scan_file(file_path, self.root)

    def test_detects_todo(self):
        findings = self.scan_source("# TODO: complete validation")

        self.assertIn(
            "CG001",
            [f["rule_id"] for f in findings]
        )

    def test_detects_fixme(self):
        findings = self.scan_source("# FIXME: handle edge case")

        self.assertIn(
            "CG001",
            [f["rule_id"] for f in findings]
        )

    def test_detects_not_implemented(self):
        findings = self.scan_source(
            "raise NotImplementedError"
        )

        self.assertIn(
            "CG002",
            [f["rule_id"] for f in findings]
        )

    def test_detects_pass_statement(self):
        findings = self.scan_source(
           "def unfinished_function():\n    pass"
 )

        self.assertIn(
            "CG003",
            [f["rule_id"] for f in findings]
        )

    def test_detects_missing_test_files(self):
        (self.root / "app.py").write_text(
            "def add(a, b): return a + b",
            encoding="utf-8"
        )

        result = scan_repository(self.root)

        self.assertIn(
            "CG004",
            [f["rule_id"] for f in result["findings"]]
        )

    def test_ignores_todo_inside_string_literal(self):
        findings = self.scan_source(
            'message = "TODO: this is only a string"'
        )

        rule_ids = [f["rule_id"] for f in findings]
        self.assertNotIn("CG001", rule_ids)

    def test_ignores_pass_inside_exception_handler(self):
        findings = self.scan_source(
            """
try:
    risky_operation()
except Exception:
    pass
"""
        )

        rule_ids = [f["rule_id"] for f in findings]
        self.assertNotIn("CG003", rule_ids)
    def test_ignores_code_examples_inside_string_literals(self):
        findings = self.scan_source(
            '''
example = """
raise NotImplementedError
pass
"""
'''
        )

        rule_ids = [f["rule_id"] for f in findings]

        self.assertNotIn("CG002", rule_ids)
        self.assertNotIn("CG003", rule_ids)

if __name__ == "__main__":
    unittest.main()
