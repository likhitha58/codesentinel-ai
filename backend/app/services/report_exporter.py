import json
import re
from pathlib import Path


def _safe_filename(value):
    """Convert a repository name into a safe filename."""
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", str(value))
    return cleaned.strip("_") or "repository"


def _markdown_cell(value):
    """Keep values safe inside Markdown table cells."""
    return (
        str(value if value is not None else "")
        .replace("|", "\\|")
        .replace("\n", " ")
    )


def generate_markdown_report(report):
    """Convert a consolidated audit report into readable Markdown."""

    repository = report.get("repository", {})
    summary = report.get("scan_summary", {})
    findings = report.get("findings", [])
    severity = summary.get("severity_summary", {})

    lines = [
        "# CodeSentinel AI — Audit Report",
        "",
        f"**Repository:** {repository.get('repository', 'Unknown')}",
        f"**Audit status:** {report.get('audit_status', 'Unknown')}",
        f"**Generated at:** {report.get('generated_at', 'Unknown')}",
        f"**Read-only audit:** {report.get('read_only', False)}",
        "",
        "## 1. Repository Overview",
        "",
        f"- Total files: {repository.get('total_files', 0)}",
        f"- Total directories: {repository.get('total_directories', 0)}",
        f"- Languages: {', '.join(repository.get('languages', {}).keys()) or 'Not detected'}",
        f"- Frameworks: {', '.join(repository.get('frameworks', [])) or 'Not detected'}",
        "",
        "## 2. Scan Summary",
        "",
        f"- Files scanned by security scanner: {summary.get('security_scanned_files', 0)}",
        f"- Files scanned by quality scanner: {summary.get('quality_scanned_files', 0)}",
        f"- Security findings: {summary.get('security_findings', 0)}",
        f"- Code-quality findings: {summary.get('quality_findings', 0)}",
        f"- Total findings: {summary.get('total_findings', 0)}",
        "",
        "| Severity | Count |",
        "|---|---:|",
    ]

    for level in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"):
        lines.append(f"| {level} | {severity.get(level, 0)} |")

    # Original scanner findings
    lines.extend([
        "",
        "## 3. Findings",
        "",
    ])

    if findings:
        lines.extend([
            "| Severity | Category | Rule | File | Line | Title |",
            "|---|---|---|---|---:|---|",
        ])

        for finding in findings:
            lines.append(
                "| "
                + " | ".join([
                    _markdown_cell(finding.get("severity")),
                    _markdown_cell(finding.get("category")),
                    _markdown_cell(finding.get("rule_id")),
                    _markdown_cell(finding.get("file")),
                    _markdown_cell(finding.get("line")),
                    _markdown_cell(finding.get("title")),
                ])
                + " |"
            )

        for index, finding in enumerate(findings, start=1):
            lines.extend([
                "",
                f"### Finding {index}: {finding.get('title', 'Untitled')}",
                "",
                f"- **Rule:** {finding.get('rule_id', 'N/A')}",
                f"- **Category:** {finding.get('category', 'N/A')}",
                f"- **Severity:** {finding.get('severity', 'N/A')}",
                f"- **Location:** {finding.get('file', 'N/A')}:{finding.get('line', 'N/A')}",
                f"- **Confidence:** {finding.get('confidence', 'N/A')}",
                f"- **Status:** {finding.get('status', 'N/A')}",
                f"- **Source:** {finding.get('source', 'N/A')}",
                f"- **Description:** {finding.get('description', 'N/A')}",
                f"- **Evidence:** `{_markdown_cell(finding.get('evidence', 'N/A'))}`",
            ])
    else:
        lines.append("No findings were reported by the configured scanners.")

    # LangGraph agent analysis
    agent_analysis = report.get("agent_analysis")

    if agent_analysis:
        lines.extend([
            "",
            "## 4. Agent Analysis",
            "",
            f"**Agent type:** {agent_analysis.get('agent_type', 'N/A')}",
            "",
            "### Executive Summary",
            "",
            agent_analysis.get("executive_summary", "Not available."),
            "",
            "### Prioritized Findings",
            "",
            "| Priority | Severity | Rule | File | Line |",
            "|---|---|---|---|---:|",
        ])

        for finding in agent_analysis.get("prioritized_findings", []):
            lines.append(
                "| "
                + " | ".join([
                    _markdown_cell(finding.get("priority")),
                    _markdown_cell(finding.get("severity")),
                    _markdown_cell(finding.get("rule_id")),
                    _markdown_cell(finding.get("file")),
                    _markdown_cell(finding.get("line")),
                ])
                + " |"
            )

        lines.extend([
            "",
            "### Remediation Recommendations",
            "",
        ])

        for recommendation in agent_analysis.get("recommendations", []):
            lines.extend([
                f"#### {recommendation.get('rule_id')} — "
                f"{recommendation.get('title')}",
                "",
                f"- **Priority:** {recommendation.get('priority')}",
                f"- **Occurrences:** {recommendation.get('occurrences')}",
                f"- **Action:** {_markdown_cell(recommendation.get('recommended_action'))}",
                "",
            ])

    # Scanner notices
    lines.extend([
        "",
        "## 5. Scanner Notices",
        "",
    ])

    for scanner, notice in report.get("notices", {}).items():
        if notice:
            lines.append(f"- **{scanner}:** {notice}")

    # Disclaimer
    lines.extend([
        "",
        "## 6. Important Disclaimer",
        "",
        "CodeSentinel AI findings are automated indicators and require manual validation. "
        "A reported finding is not necessarily a confirmed vulnerability or defect.",
        "",
    ])

    return "\n".join(lines)


def export_audit_report(report, output_dir="reports", formats=None):
    """
    Export an audit report as JSON and/or Markdown.

    Returns the paths of the files created.
    """

    if formats is None:
        formats = ("json", "markdown")

    allowed_formats = {"json", "markdown"}
    requested_formats = set(formats)

    invalid_formats = requested_formats - allowed_formats

    if invalid_formats:
        raise ValueError(
            f"Unsupported report formats: {sorted(invalid_formats)}"
        )

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    repository_name = _safe_filename(
        report.get("repository", {}).get("repository", "repository")
    )

    generated_at = (
        report.get("generated_at", "audit")
        .replace(":", "-")
        .replace("+", "_")
    )

    base_name = f"{repository_name}_audit_{generated_at}"

    created_files = {}

    if "json" in requested_formats:
        json_path = output_path / f"{base_name}.json"

        json_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        created_files["json"] = str(json_path.resolve())

    if "markdown" in requested_formats:
        markdown_path = output_path / f"{base_name}.md"

        markdown_path.write_text(
            generate_markdown_report(report),
            encoding="utf-8",
        )

        created_files["markdown"] = str(markdown_path.resolve())

    return created_files