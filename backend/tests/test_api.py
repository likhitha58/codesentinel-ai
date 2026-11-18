
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.api import routes


client = TestClient(app)


class TestCodeSentinelAPI(unittest.TestCase):

    def test_root_endpoint(self):
        response = client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "CodeSentinel AI")
        self.assertEqual(response.json()["status"], "running")

    def test_health_endpoint(self):
        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_missing_repository_returns_404(self):
        response = client.post(
            "/api/audit",
            json={"repository": "repository-that-does-not-exist"},
        )

        self.assertEqual(response.status_code, 404)

    def test_absolute_path_is_rejected(self):
        response = client.post(
            "/api/audit",
            json={"repository": str(Path.cwd())},
        )

        self.assertEqual(response.status_code, 400)

    def test_directory_traversal_is_rejected(self):
        response = client.post(
            "/api/audit",
            json={"repository": "../"},
        )

        self.assertEqual(response.status_code, 400)

    def test_invalid_request_payload_returns_422(self):
        response = client.post(
            "/api/audit",
            json={},
        )

        self.assertEqual(response.status_code, 422)

    def test_successful_repository_audit(self):
        with TemporaryDirectory() as temp_dir:
            repository = Path(temp_dir)
            (repository / "app.py").write_text(
                "def hello():\n    return 'Hello'\n",
                encoding="utf-8",
            )

            with patch.object(
                routes,
                "SCAN_ROOT",
                repository.parent,
            ):
                response = client.post(
                    "/api/audit",
                    json={"repository": repository.name},
                )

        self.assertEqual(response.status_code, 200)

        result = response.json()

        self.assertEqual(result["audit_status"], "COMPLETED")
        self.assertIn("repository", result)
        self.assertIn("scan_summary", result)
        self.assertIn("findings", result)
        self.assertIn("agent_analysis", result)

        self.assertEqual(
            result["agent_analysis"]["agent_type"],
            "LangGraph deterministic workflow",
        )

    def test_repository_file_limit_returns_413(self):
        with TemporaryDirectory() as temp_dir:
            repository = Path(temp_dir)
            (repository / "app.py").write_text(
                "print('test')",
                encoding="utf-8",
            )

            with (
                patch.object(routes, "SCAN_ROOT", repository.parent),
                patch.object(routes, "MAX_REPOSITORY_FILES", 0),
            ):
                response = client.post(
                    "/api/audit",
                    json={"repository": repository.name},
                )

        self.assertEqual(response.status_code, 413)
        self.assertIn("maximum", response.json()["detail"].lower())

    def test_repository_size_limit_returns_413(self):
        with TemporaryDirectory() as temp_dir:
            repository = Path(temp_dir)
            (repository / "app.py").write_text(
                "This file exceeds the test limit.",
                encoding="utf-8",
            )

            with (
                patch.object(routes, "SCAN_ROOT", repository.parent),
                patch.object(routes, "MAX_REPOSITORY_SIZE_BYTES", 1),
            ):
                response = client.post(
                    "/api/audit",
                    json={"repository": repository.name},
                )

        self.assertEqual(response.status_code, 413)
        self.assertIn("configured maximum size", response.json()["detail"].lower())

    def test_audit_failure_returns_controlled_500(self):
        with TemporaryDirectory() as temp_dir:
            repository = Path(temp_dir)
            (repository / "app.py").write_text(
                "def hello():\n    return 'Hello'\n",
                encoding="utf-8",
            )

            with (
                patch.object(routes, "SCAN_ROOT", repository.parent),
                patch.object(
                    routes,
                    "build_audit_report",
                    side_effect=RuntimeError("Internal test failure"),
                ),
            ):
                response = client.post(
                    "/api/audit",
                    json={"repository": repository.name},
                )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json()["detail"],
            "The repository audit failed due to an internal processing error.",
        )


if __name__ == "__main__":
    unittest.main()
