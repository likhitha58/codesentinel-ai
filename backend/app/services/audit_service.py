
from datetime import datetime, timezone
from pathlib import Path

from app.analyzers.project_detector import analyze_repository
from app.scanners.security_scanner import scan_repository as scan_security
from app.scanners.code_quality_scanner import scan_repository as scan_code_quality


SEVERITY_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
    "INFO": 4,
}


def build_audit_report(repository_path):
    """
    Run all CodeSentinel analysis modules against a repository
    and return one consolidated, read-only audit report.
    """

    root = Path(repository_path).expanduser().resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Repository path does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Expected a repository directory: {root}"
        )

    # 1. Collect repository metadata.
    repository_info = analyze_repository(str(root))

    # 2. Run independent analysis modules.
    security_result = scan_security(str(root))
    quality_result = scan_code_quality(str(root))

    # 3. Normalize and combine findings.
    combined_findings = []

    for finding in security_result.get("findings", []):
        normalized = dict(finding)
        normalized["category"] = "SECURITY"
        normalized["source"] = "security_scanner"
        combined_findings.append(normalized)

    for finding in quality_result.get("findings", []):
        normalized = dict(finding)
        normalized["category"] = "CODE_QUALITY"
        normalized["source"] = "code_quality_scanner"
        combined_findings.append(normalized)

    # 4. Sort findings by severity, then file and line.
    combined_findings.sort(
        key=lambda item: (
            SEVERITY_ORDER.get(
                item.get("severity", "INFO").upper(), 99
            ),
            item.get("file", ""),
            item.get("line", 0) or 0,
        )
    )

    # 5. Calculate the consolidated severity summary.
    severity_summary = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
        "INFO": 0,
    }

    for finding in combined_findings:
        severity = finding.get("severity", "INFO").upper()
        severity_summary[severity] = (
            severity_summary.get(severity, 0) + 1
        )

    # 6. Build the final report.
    report = {
        "audit_status": "COMPLETED",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": repository_info,
        "scan_summary": {
            "repository_files": repository_info["total_files"],
            "security_scanned_files": security_result["scanned_files"],
            "quality_scanned_files": quality_result["scanned_files"],
            "security_findings": security_result["total_findings"],
            "quality_findings": quality_result["total_findings"],
            "total_findings": len(combined_findings),
            "severity_summary": severity_summary,
        },
        "findings": combined_findings,
        "notices": {
            "security": security_result.get("notice"),
            "code_quality": quality_result.get("notice"),
        },
        "read_only": True,
    }

    return report
