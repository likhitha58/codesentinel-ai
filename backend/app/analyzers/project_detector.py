
import json
import os
import sys

from collections import Counter
from pathlib import Path


# Directories that should never be included in repository analysis
IGNORED_DIRS = {
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

# Programming language identification
LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".cpp": "C++",
    ".cc": "C++",
    ".c": "C",
    ".h": "C/C++",
    ".hpp": "C++",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".sql": "SQL",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sh": "Shell",
}

IMPORTANT_FILES = {
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "Pipfile",
    "poetry.lock",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "Dockerfile",
    "docker-compose.yml",
    ".env",
    ".env.example",
    ".gitignore",
    "README.md",
}


FRAMEWORK_MAP = {
    "react": "React",
    "next": "Next.js",
    "express": "Express.js",
    "vue": "Vue.js",
    "angular": "Angular",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "streamlit": "Streamlit",
    "langchain": "LangChain",
    "langgraph": "LangGraph",
    "tensorflow": "TensorFlow",
    "torch": "PyTorch",
    "scikit-learn": "Scikit-learn",
    "mongoose": "Mongoose",
}


def detect_frameworks(root: Path) -> set:
    """Detect frameworks from project manifests."""

    detected = set()

    package_file = root / "package.json"

    if package_file.exists():
        try:
            data = json.loads(
                package_file.read_text(encoding="utf-8")
            )

            dependencies = {
                **data.get("dependencies", {}),
                **data.get("devDependencies", {}),
            }

            for dependency in dependencies:
                name = FRAMEWORK_MAP.get(dependency.lower())

                if name:
                    detected.add(name)

        except (json.JSONDecodeError, OSError):
            pass

    dependency_files = [
        root / "requirements.txt",
        root / "pyproject.toml",
        root / "Pipfile",
    ]

    for file in dependency_files:
        if not file.exists():
            continue

        try:
            content = file.read_text(
                encoding="utf-8",
                errors="ignore"
            ).lower()

            for dependency, framework in FRAMEWORK_MAP.items():
                if dependency in content:
                    detected.add(framework)

        except OSError:
            continue

    return detected


def analyze_repository(repository_path: str) -> dict:
    """Analyze a repository without executing source code."""

    root = Path(repository_path).resolve()

    if not root.exists() or not root.is_dir():
        raise ValueError("Invalid repository directory.")

    language_count = Counter()
    important_files = []
    analyzed_files = []
    directory_count = 0
    total_size = 0

    for current_path, directories, files in os.walk(
        root,
        followlinks=False
    ):

        directories[:] = sorted(
            directory
            for directory in directories
            if directory not in IGNORED_DIRS
            and not (Path(current_path) / directory).is_symlink()
        )

        current = Path(current_path)

        if current != root:
            directory_count += 1

        for filename in files:
            file_path = current / filename

            if file_path.is_symlink():
                continue

            try:
                relative_path = file_path.relative_to(root).as_posix()
                file_size = file_path.stat().st_size
            except OSError:
                continue

            # Avoid unexpectedly large files
            if file_size > 5 * 1024 * 1024:
                continue

            analyzed_files.append(relative_path)
            total_size += file_size

            extension = file_path.suffix.lower()

            if extension in LANGUAGE_MAP:
                language_count[LANGUAGE_MAP[extension]] += 1

            if filename in IMPORTANT_FILES:
                important_files.append(relative_path)

    frameworks = sorted(detect_frameworks(root))

    return {
        "repository": root.name,
        "repository_path": str(root),
        "total_files": len(analyzed_files),
        "total_directories": directory_count,
        "total_size_bytes": total_size,
        "languages": dict(language_count.most_common()),
        "frameworks": frameworks,
        "important_files": sorted(important_files),
        "files": sorted(analyzed_files),
        "excluded_directories": sorted(IGNORED_DIRS),
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."

    try:
        result = analyze_repository(target)
        print(json.dumps(result, indent=4))

    except ValueError as error:
        print(f"Error: {error}")
        sys.exit(1)
