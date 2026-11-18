
import ast
import os
import re
from pathlib import Path


IGNORED_DIRS = {
    ".git", ".venv", "venv", "env",
    "node_modules", "__pycache__",
    ".pytest_cache", ".mypy_cache",
    "dist", "build", "coverage"
}

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".php", ".go", ".rb",
    ".cs", ".cpp", ".c", ".sql",
    ".html", ".css", ".scss", ".sh"
}

TEST_FILE_PATTERN = re.compile(
    r"(^test_.*|.*_test|.*\.test|.*\.spec)\."
    r"(py|js|jsx|ts|tsx|java|go)$",
    re.IGNORECASE
)

RULES = [
    {
        "id": "CG001",
        "name": "Unresolved work marker",
        "pattern": re.compile(
            r"(?:^|\s)(?:#|//|/\*|\*|--)\s*.*?"
            r"\b(TODO|FIXME|XXX|HACK)\b",
            re.IGNORECASE
        )
    },
    {
        "id": "CG002",
        "name": "Unimplemented functionality",
        "pattern": re.compile(r"\bNotImplementedError\b")
    },
    {
        "id": "CG003",
        "name": "Possible empty implementation",
        "pattern": re.compile(r"^\s*pass\s*(?:#.*)?$")
    }
]


def get_exception_pass_lines(content):
    """Identify pass statements inside exception handlers."""

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return set()

    parents = {}

    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent

    ignored_lines = set()

    for node in ast.walk(tree):

        if not isinstance(node, ast.Pass):
            continue

        ancestor = parents.get(node)

        while ancestor is not None:

            if isinstance(ancestor, ast.ExceptHandler):
                ignored_lines.add(node.lineno)
                break

            # Do not cross function or class boundaries.
            if isinstance(
                ancestor,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.Lambda,
                    ast.ClassDef
                )
            ):
                break

            ancestor = parents.get(ancestor)

    return ignored_lines


def get_python_structural_lines(content):
    """Find actual unimplemented raises and pass statements in Python."""

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return set(), set()

    unimplemented_lines = set()
    pass_lines = set()

    ignored_pass_lines = get_exception_pass_lines(content)

    for node in ast.walk(tree):

        if isinstance(node, ast.Raise) and node.exc:

            exception = node.exc

            if (
                isinstance(exception, ast.Name)
                and exception.id == "NotImplementedError"
            ):
                unimplemented_lines.add(node.lineno)

            elif (
                isinstance(exception, ast.Call)
                and isinstance(exception.func, ast.Name)
                and exception.func.id == "NotImplementedError"
            ):
                unimplemented_lines.add(node.lineno)

        elif isinstance(node, ast.Pass):
            if node.lineno not in ignored_pass_lines:
                pass_lines.add(node.lineno)

    return unimplemented_lines, pass_lines



def scan_file(file_path, root):
    """Find possible unfinished code in one source file."""

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

    is_python = file_path.suffix.lower() == ".py"

    python_unimplemented_lines = set()
    python_pass_lines = set()

    if is_python:
        (
            python_unimplemented_lines,
            python_pass_lines
        ) = get_python_structural_lines(content)

    for line_number, line in enumerate(lines, start=1):

        for rule in RULES:

            rule_id = rule["id"]

            # Python structural rules are handled using AST below.
            if is_python and rule_id in {"CG002", "CG003"}:
                continue

            if not rule["pattern"].search(line):
                continue

            if rule_id == "CG001":

                marker = rule["pattern"].search(line).group(1)

                severity = (
                    "MEDIUM"
                    if marker.upper() in {"FIXME", "XXX"}
                    else "LOW"
                )

                description = (
                    f"Code contains a {marker.upper()} marker "
                    "that may represent unresolved work."
                )

            elif rule_id == "CG002":

                severity = "MEDIUM"
                description = (
                    "This code may contain functionality "
                    "that has not been implemented."
                )

            else:

                severity = "LOW"
                description = (
                    "A standalone pass statement may indicate "
                    "an empty or unfinished implementation."
                )

            findings.append({
                "rule_id": rule_id,
                "title": rule["name"],
                "severity": severity,
                "file": relative_path,
                "line": line_number,
                "description": description,
                "evidence": line.strip()[:200],
                "confidence": "LOW",
                "status": "NEEDS_REVIEW"
            })

    # Add AST-based Python findings.
    if is_python:

        structural_rules = {
            rule["id"]: rule for rule in RULES
            if rule["id"] in {"CG002", "CG003"}
        }

        for rule_id, detected_lines in [
            ("CG002", python_unimplemented_lines),
            ("CG003", python_pass_lines)
        ]:

            rule = structural_rules[rule_id]

            for line_number in sorted(detected_lines):

                line = lines[line_number - 1]

                if rule_id == "CG002":
                    severity = "MEDIUM"
                    description = (
                        "This code explicitly raises "
                        "NotImplementedError."
                    )
                else:
                    severity = "LOW"
                    description = (
                        "A standalone pass statement may indicate "
                        "an empty or unfinished implementation."
                    )

                findings.append({
                    "rule_id": rule_id,
                    "title": rule["name"],
                    "severity": severity,
                    "file": relative_path,
                    "line": line_number,
                    "description": description,
                    "evidence": line.strip()[:200],
                    "confidence": "LOW",
                    "status": "NEEDS_REVIEW"
                })

    return findings


def scan_repository(repository_path):
    """Scan a repository for possible coding gaps."""

    root = Path(repository_path).resolve()

    if not root.exists() or not root.is_dir():
        raise ValueError("Invalid repository directory.")

    findings = []
    scanned_files = 0
    source_files = []
    test_files = []

    for current_path, directories, files in os.walk(
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
                if file_path.stat().st_size > 5 * 1024 * 1024:
                    continue
            except OSError:
                continue

            scanned_files += 1
            source_files.append(file_path)

            if TEST_FILE_PATTERN.match(filename):
                test_files.append(file_path)

            findings.extend(scan_file(file_path, root))

    if source_files and not test_files:
        findings.append({
            "rule_id": "CG004",
            "title": "No recognizable test files found",
            "severity": "MEDIUM",
            "file": ".",
            "line": 0,
            "description": (
                "No files matching common test naming conventions "
                "were found. Tests may still exist under other names."
            ),
            "evidence": "No recognizable test file names detected.",
            "confidence": "LOW",
            "status": "NEEDS_REVIEW"
        })

    severity_summary = {
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
        "severity_summary": severity_summary,
        "findings": findings,
        "notice": (
            "Code-quality findings are heuristic indicators. "
            "Manual review is required."
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
        print(json.dumps({"error": str(error)}, indent=4))
        sys.exit(1)
