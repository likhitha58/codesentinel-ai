
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.api import routes


client = TestClient(app)


class TestExportEndpoints(unittest.TestCase):
    """Tests for the JSON and Markdown export endpoints."""

    def _create_test_repo(self):
        """Create a minimal test repository and return (temp_dir, repo_path)."""
        temp_dir = TemporaryDirectory()
        repo = Path(temp_dir.name)
        (repo / "app.py").write_text(
            'API_KEY = "test_secret_1234"\n'
            "# TODO: implement feature\n"
            "def hello():\n"
            "    return 'Hello'\n",
            encoding="utf-8",
        )
        return temp_dir, repo

    # --- JSON export ---

    def test_json_export_success(self):
        temp_dir, repo = self._create_test_repo()

        with temp_dir:
            with patch.object(routes, "SCAN_ROOT", repo.parent):
                response = client.post(
                    "/api/audit/export/json",
                    json={"repository": repo.name},
                )

        self.assertEqual(response.status_code, 200)

    def test_json_export_content_type(self):
        temp_dir, repo = self._create_test_repo()

        with temp_dir:
            with patch.object(routes, "SCAN_ROOT", repo.parent):
                response = client.post(
                    "/api/audit/export/json",
                    json={"repository": repo.name},
                )

        self.assertIn("application/json", response.headers["content-type"])

    def test_json_export_content_disposition(self):
        temp_dir, repo = self._create_test_repo()

        with temp_dir:
            with patch.object(routes, "SCAN_ROOT", repo.parent):
                response = client.post(
                    "/api/audit/export/json",
                    json={"repository": repo.name},
                )

        self.assertIn("attachment", response.headers["content-disposition"])
        self.assertIn(".json", response.headers["content-disposition"])

    def test_json_export_valid_json(self):
        temp_dir, repo = self._create_test_repo()

        with temp_dir:
            with patch.object(routes, "SCAN_ROOT", repo.parent):
                response = client.post(
                    "/api/audit/export/json",
                    json={"repository": repo.name},
                )

        data = json.loads(response.content)
        self.assertEqual(data["audit_status"], "COMPLETED")
        self.assertIn("findings", data)
        self.assertIn("agent_analysis", data)

    def test_json_export_includes_agent_analysis(self):
        temp_dir, repo = self._create_test_repo()

        with temp_dir:
            with patch.object(routes, "SCAN_ROOT", repo.parent):
                response = client.post(
                    "/api/audit/export/json",
                    json={"repository": repo.name},
                )

        data = json.loads(response.content)
        agent = data["agent_analysis"]
        self.assertIn("executive_summary", agent)
        self.assertIn("prioritized_findings", agent)
        self.assertIn("recommendations", agent)

    def test_json_export_invalid_repository(self):
        response = client.post(
            "/api/audit/export/json",
            json={"repository": "nonexistent-repo-xyz"},
        )

        self.assertEqual(response.status_code, 404)

    def test_json_export_audit_failure(self):
        temp_dir, repo = self._create_test_repo()

        with temp_dir:
            with (
                patch.object(routes, "SCAN_ROOT", repo.parent),
                patch.object(
                    routes,
                    "build_audit_report",
                    side_effect=RuntimeError("Test failure"),
                ),
            ):
                response = client.post(
                    "/api/audit/export/json",
                    json={"repository": repo.name},
                )

        self.assertEqual(response.status_code, 500)
        self.assertIn(
            "internal processing error",
            response.json()["detail"].lower(),
        )

    # --- Markdown export ---

    def test_markdown_export_success(self):
        temp_dir, repo = self._create_test_repo()

        with temp_dir:
            with patch.object(routes, "SCAN_ROOT", repo.parent):
                response = client.post(
                    "/api/audit/export/markdown",
                    json={"repository": repo.name},
                )

        self.assertEqual(response.status_code, 200)

    def test_markdown_export_content_type(self):
        temp_dir, repo = self._create_test_repo()

        with temp_dir:
            with patch.object(routes, "SCAN_ROOT", repo.parent):
                response = client.post(
                    "/api/audit/export/markdown",
                    json={"repository": repo.name},
                )

        self.assertIn("text/markdown", response.headers["content-type"])

    def test_markdown_export_content_disposition(self):
        temp_dir, repo = self._create_test_repo()

        with temp_dir:
            with patch.object(routes, "SCAN_ROOT", repo.parent):
                response = client.post(
                    "/api/audit/export/markdown",
                    json={"repository": repo.name},
                )

        self.assertIn("attachment", response.headers["content-disposition"])
        self.assertIn(".md", response.headers["content-disposition"])

    def test_markdown_export_headings_and_content(self):
        temp_dir, repo = self._create_test_repo()

        with temp_dir:
            with patch.object(routes, "SCAN_ROOT", repo.parent):
                response = client.post(
                    "/api/audit/export/markdown",
                    json={"repository": repo.name},
                )

        content = response.text
        self.assertIn("# CodeSentinel AI", content)
        self.assertIn("## 1. Repository Overview", content)
        self.assertIn("## 2. Scan Summary", content)
        self.assertIn("## 3. Findings", content)

    def test_markdown_export_includes_agent_analysis(self):
        temp_dir, repo = self._create_test_repo()

        with temp_dir:
            with patch.object(routes, "SCAN_ROOT", repo.parent):
                response = client.post(
                    "/api/audit/export/markdown",
                    json={"repository": repo.name},
                )

        content = response.text
        self.assertIn("## 4. Agent Analysis", content)
        self.assertIn("Executive Summary", content)
        self.assertIn("Remediation Recommendations", content)

    def test_markdown_export_includes_recommendations(self):
        temp_dir, repo = self._create_test_repo()

        with temp_dir:
            with patch.object(routes, "SCAN_ROOT", repo.parent):
                response = client.post(
                    "/api/audit/export/markdown",
                    json={"repository": repo.name},
                )

        content = response.text
        self.assertIn("Prioritized Findings", content)
        self.assertIn("Important Disclaimer", content)

    def test_markdown_export_invalid_repository(self):
        response = client.post(
            "/api/audit/export/markdown",
            json={"repository": "nonexistent-repo-xyz"},
        )

        self.assertEqual(response.status_code, 404)

    def test_markdown_export_audit_failure(self):
        temp_dir, repo = self._create_test_repo()

        with temp_dir:
            with (
                patch.object(routes, "SCAN_ROOT", repo.parent),
                patch.object(
                    routes,
                    "build_audit_report",
                    side_effect=RuntimeError("Test failure"),
                ),
            ):
                response = client.post(
                    "/api/audit/export/markdown",
                    json={"repository": repo.name},
                )

        self.assertEqual(response.status_code, 500)


if __name__ == "__main__":
    unittest.main()
