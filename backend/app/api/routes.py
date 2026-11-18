
import logging
import os
import stat
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.audit_service import build_audit_report
from app.agents.audit_agent import run_audit_agent


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Repository Audit"])

# Only repositories inside this directory can be scanned.
SCAN_ROOT = Path(__file__).resolve().parents[2] / "scan_targets"

# Initial resource limits.
MAX_REPOSITORY_FILES = 5000
MAX_REPOSITORY_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".next",
    "dist",
    "build",
    "coverage",
    ".idea",
    ".vscode",
}


class AuditRequest(BaseModel):
    repository: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Repository directory relative to the configured scan root.",
        examples=["demo-repo"],
    )


def resolve_repository_path(repository: str) -> Path:
    """Resolve a repository without allowing access outside SCAN_ROOT."""

    requested_path = repository.strip()

    if not requested_path or "\x00" in requested_path:
        raise HTTPException(
            status_code=400,
            detail="A valid repository path is required.",
        )

    relative_path = Path(requested_path)

    if (
        relative_path.is_absolute()
        or relative_path.drive
        or relative_path.root
        or ".." in relative_path.parts
        or not relative_path.parts
    ):
        raise HTTPException(
            status_code=400,
            detail="Only relative repository paths are allowed.",
        )

    try:
        scan_root = SCAN_ROOT.resolve()
        target_path = (scan_root / relative_path).resolve()

        # Prevent symbolic links from escaping the permitted directory.
        target_path.relative_to(scan_root)

    except (ValueError, OSError, RuntimeError):
        raise HTTPException(
            status_code=400,
            detail="Repository path is outside the permitted scan directory.",
        )

    if not target_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Repository directory was not found.",
        )

    if not target_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail="The requested repository path must be a directory.",
        )

    return target_path


def validate_repository_limits(repository_path: Path) -> None:
    """
    Check repository size and file count before running the scanners.

    Generated directories and symbolic links are excluded.
    """

    file_count = 0
    total_size = 0

    def handle_walk_error(error):
        raise error

    try:
        for current_root, directories, filenames in os.walk(
            repository_path,
            topdown=True,
            followlinks=False,
            onerror=handle_walk_error,
        ):
            current_path = Path(current_root)

            # Do not traverse generated directories or directory symlinks.
            directories[:] = [
                directory
                for directory in directories
                if directory not in IGNORED_DIRECTORIES
                and not (current_path / directory).is_symlink()
            ]

            for filename in filenames:
                file_path = current_path / filename

                # Do not follow symbolic links.
                if file_path.is_symlink():
                    continue

                file_stat = file_path.stat(follow_symlinks=False)

                # Count regular files only.
                if not stat.S_ISREG(file_stat.st_mode):
                    continue

                file_count += 1
                total_size += file_stat.st_size

                if file_count > MAX_REPOSITORY_FILES:
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            f"Repository exceeds the maximum of "
                            f"{MAX_REPOSITORY_FILES} files."
                        ),
                    )

                if total_size > MAX_REPOSITORY_SIZE_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            "Repository exceeds the configured maximum size "
                            f"of {MAX_REPOSITORY_SIZE_BYTES / (1024 * 1024):g} MB."
                        ),
                    )

    except HTTPException:
        raise

    except OSError:
        logger.exception("Unable to inspect repository files.")
        raise HTTPException(
            status_code=400,
            detail="The repository contains files that cannot be inspected.",
        )


@router.post(
    "/audit",
    summary="Audit a software repository",
    response_description="Consolidated audit report with agent analysis.",
)
def audit_repository(request: AuditRequest):
    """
    Run repository discovery, security analysis,
    code-quality analysis, and LangGraph prioritization.
    """

    repository_path = resolve_repository_path(request.repository)

    validate_repository_limits(repository_path)

    try:
        audit_report = build_audit_report(str(repository_path))
        enhanced_report = run_audit_agent(audit_report)

        return enhanced_report

    except Exception:
        logger.exception(
            "Audit processing failed for repository: %s",
            request.repository,
        )

        raise HTTPException(
            status_code=500,
            detail="The repository audit failed due to an internal processing error.",
        )
