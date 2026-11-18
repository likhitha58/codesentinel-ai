
import re
from pathlib import Path


IGNORED_DIRS = {
    ".git", ".venv", "venv", "env",
    "node_modules", "__pycache__",
    "dist", "build", "coverage"
}

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".php", ".go", ".rb",
    ".cs", ".cpp", ".c", ".sql"
}

MAX_FILE_SIZE = 5 * 1024 * 1024


RULES = [
    {
        "id": "SEC001",
        "name": "Possible hardcoded credential",
        "severity": "HIGH",
        "pattern": re.compile(
            r"""(?i)\b(api[_-]?key|secret[_-]?key|password|passwd|access[_-]?token)\b\s*[:=]\s*["'][^"'\n]{4,}["']"""
        ),
        "description": "A credential-like value may be hardcoded in source code."
    },
    {
        "id": "SEC002",
        "name": "Possible SQL injection",
        "severity": "HIGH",
        "pattern": re.compile(
            r"""(?is)\b(execute|executemany|query)\s*\(\s*["'][\s\S]{0,500}?(%s|\{\}|["']\s*\+|\$\{)"""
        ),
        "description": "SQL may be constructed using unsafe string interpolation or concatenation."
    },
    {
        "id": "SEC003",
        "name": "Unsafe dynamic evaluation",
        "severity": "HIGH",
        "pattern": re.compile(r"\beval\s*\("),
        "description": "Dynamic evaluation can execute untrusted expressions."
    },
    {
        "id": "SEC004",
        "name": "Potential command injection",
        "severity": "HIGH",
        "pattern": re.compile(
            r"""(?i)(os\.system\s*\(|shell\s*=\s*True)"""
        ),
        "description": "Shell execution can be dangerous when arguments contain untrusted input."
    },
    {
        "id": "SEC005",
        "name": "Weak cryptographic hash",
        "severity": "MEDIUM",
        "pattern": re.compile(
            r"""(?i)(hashlib\.(md5|sha1)\s*\(|MessageDigest\.getInstance\s*\(\s*["'](MD5|SHA-1))"""
        ),
        "description": "MD5 and SHA-1 are not suitable for security-sensitive hashing."
    },
    {
        "id": "SEC006",
        "name": "Unsafe deserialization",
        "severity": "HIGH",
        "pattern": re.compile(
            r"""(?i)(pickle\.loads?\s*\(|yaml\.load\s*\()"""
        ),
        "description": "Deserializing untrusted data can lead to code execution."
    },
    {
        "id": "SEC007",
        "name": "Debug mode enabled",
        "severity": "LOW",
        "pattern": re.compile(
            r"""(?i)\b(debug|debug_mode)\s*=\s*True\b"""
        ),
        "description": "Debug mode may expose sensitive diagnostic information."
    },
    {
        "id": "SEC008",
        "name": "Potentially unsafe CORS configuration",
        "severity": "MEDIUM",
        "pattern": re.compile(
            r"""(?i)(Access-Control-Allow-Origin|allow_origins)\s*[:=]\s*["']\*["']"""
        ),
        "description": "Wildcard CORS configuration may expose resources to unintended origins."
    }
]


def redact_evidence(line):
    """Avoid exposing potential secrets in reports."""

    return re.sub(
        r"""(?i)(api[_-]?key|secret[_-]?key|password|passwd|access[_-]?token)(["']?\s*[:=]\s*["'])[^"'\s]+""",
        r"\1\2[REDACTED]",
        line.strip()
    )[:200]


def scan_file(file_path, root):
    """Scan one source file against security rules."""

    findings = []

    try:
        content = file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    except OSError:
        return findings

    relative_path = file_path.relative_to(root).as_posix()
    lines = content.splitlines()

    # Run ordinary security rules line by line.
    for line_number, line in enumerate(lines, start=1):

        for rule in RULES:

            # SEC002 is handled separately across the full file.
            if rule["id"] == "SEC002":
                continue

            if rule["pattern"].search(line):
                findings.append({
                    "rule_id": rule["id"],
                    "title": rule["name"],
                    "severity": rule["severity"],
                    "file": relative_path,
                    "line": line_number,
                    "description": rule["description"],
                    "evidence": redact_evidence(line),
                    "confidence": "LOW",
                    "status": "NEEDS_REVIEW"
                })

    # Scan the complete file for SQL injection patterns,
    # including patterns that span multiple lines.
    sql_rule = next(
        rule for rule in RULES
        if rule["id"] == "SEC002"
    )

    for match in sql_rule["pattern"].finditer(content):

        line_number = content.count(
            "\n", 0, match.start()
        ) + 1

        evidence = " ".join(match.group(0).split())

        findings.append({
            "rule_id": sql_rule["id"],
            "title": sql_rule["name"],
            "severity": sql_rule["severity"],
            "file": relative_path,
            "line": line_number,
            "description": sql_rule["description"],
            "evidence": redact_evidence(evidence),
            "confidence": "LOW",
            "status": "NEEDS_REVIEW"
        })

    return findings


def scan_repository(repository_path):
    """Scan a repository without executing its code."""

    root = Path(repository_path).resolve()

    if not root.exists() or not root.is_dir():
        raise ValueError("Invalid repository directory.")

    findings = []
    scanned_files = 0

    for current_path, directories, files in __import__("os").walk(
        root,
        followlinks=False
    ):

        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRS
            and not (Path(current_path) / directory).is_symlink()
        ]

        for filename in files:

            file_path = Path(current_path) / filename

            if file_path.is_symlink():
                continue

            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            try:
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue

            scanned_files += 1

            findings.extend(scan_file(file_path, root))

    severity_counts = {
        severity: sum(
            1 for finding in findings
            if finding["severity"] == severity
        )
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    }

    return {
        "repository": root.name,
        "scanned_files": scanned_files,
        "total_findings": len(findings),
        "severity_summary": severity_counts,
        "findings": findings,
        "notice": (
            "Regex-based findings are heuristic indicators, "
            "not confirmed vulnerabilities. Manual validation is required."
        )
    }


if __name__ == "__main__":
    import json
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "."

    try:
        result = scan_repository(target)
        print(json.dumps(result, indent=4))

    except ValueError as error:
        print(f"Error: {error}")
        sys.exit(1)
