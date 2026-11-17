# CodeSentinel AI

**Architecture-Agnostic Security, Code Quality & Completeness Auditing Agent**

CodeSentinel AI is an AI-assisted developer security and code-quality auditing project developed for the Mycrobo Hackathon (17–18 November 2026).

The project aims to identify security vulnerabilities, code slop, incomplete implementations, coding gaps, and technical debt across software repositories, regardless of their underlying architecture.

> **Development status:** Work in progress. Repository analysis and an initial heuristic security scanner are implemented. AI reasoning, advanced scanning, API integration, and the frontend are planned.

## Problem Statement

Modern software projects often contain security vulnerabilities, inconsistent coding practices, incomplete features, and technical debt. These problems become harder to identify as repositories grow and incorporate multiple languages and frameworks.

CodeSentinel AI aims to provide a unified auditing workflow that helps developers identify and prioritize these issues.

## Planned Capabilities

- **Repository Intelligence:** Discover source files, programming languages, and frameworks.
- **Security Analysis:** Detect potentially unsafe coding patterns and security vulnerabilities.
- **Code Slop Detection:** Identify duplicated, unnecessarily complex, and low-quality code.
- **Coding Gap Detection:** Identify TODOs, placeholders, incomplete implementations, and missing safeguards.
- **AI Reasoning:** Analyze and prioritize findings using an LLM-powered agent.
- **Audit Dashboard:** Present actionable findings and repository health metrics.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Agent orchestration | LangGraph |
| AI integration | Google GenAI (planned) |
| Frontend | React + Vite (planned) |
| Initial scanning | Python regex-based heuristics |
| Advanced scanning | Semgrep, Gitleaks (planned) |

## Current Implementation

### 1. Repository Intelligence Engine

File: `backend/app/analyzers/project_detector.py`

Implemented capabilities:

- Detect programming languages using file extensions.
- Identify selected frameworks from root-level dependency manifests.
- Count files and directories.
- Identify important configuration files.
- Exclude common generated and dependency directories.
- Produce structured JSON output.

### 2. Security Scanner

File: `backend/app/scanners/security_scanner.py`

Current heuristic checks:

| Rule | Detection |
|---|---|
| SEC001 | Possible hardcoded credentials |
| SEC002 | Possible SQL injection |
| SEC003 | Unsafe dynamic evaluation |
| SEC004 | Potential command injection |
| SEC005 | Weak cryptographic hashing |
| SEC006 | Unsafe deserialization |
| SEC007 | Debug mode enabled |
| SEC008 | Potentially unsafe CORS configuration |

**Important:** Findings are heuristic indicators requiring review, not confirmed vulnerabilities.

## Local Setup

### Prerequisites

- Python 3.12 or compatible version
- Git
- Node.js for the planned frontend

### Backend setup (Windows PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install fastapi uvicorn pydantic python-dotenv langgraph
```

### Run repository analysis

From the `backend` directory:

```powershell
python -m app.analyzers.project_detector ..
```

### Run security analysis

```powershell
python -m app.scanners.security_scanner ..
```

The scanner inspects repository source files without executing the target code.

## Validation Results

Initial manual validation was performed using `backend/tests/sample_vulnerable.py`.

- Source files scanned: 5
- Findings detected: 6
- High severity: 4
- Medium severity: 1
- Low severity: 1
- Hardcoded credential evidence was redacted.

### Known Limitation

The SQL injection test was not detected because the initial scanner uses line-by-line regular expressions and the sample query spans multiple lines.

Additional false-positive testing, automated regression tests, and stronger static analysis are required.

## Planned Architecture

```text
Repository Input
       |
Repository Intelligence
       |
Security & Quality Scanners
       |
Finding Normalization
       |
AI Reasoning Agent
       |
Prioritized Audit Report
       |
Dashboard / CLI
```

## Development Roadmap

- [x] Initialize project structure.
- [x] Implement repository intelligence engine.
- [x] Implement initial security scanner.
- [x] Perform initial manual security scanning validation.
- [ ] Fix missed SQL injection test.
- [ ] Add automated regression tests.
- [ ] Build code-quality and completeness analyzers.
- [ ] Integrate advanced security scanning.
- [ ] Implement LangGraph reasoning workflow.
- [ ] Integrate Gemini.
- [ ] Build FastAPI endpoints.
- [ ] Build React dashboard.
- [ ] Complete end-to-end testing and demonstration.

## Security Considerations

CodeSentinel is intended to analyze untrusted source code without executing it. Future repository ingestion and external scanner integrations must enforce resource limits, safe path handling, and isolated execution where appropriate.

Never commit API keys, credentials, or real secrets.

## AI Development Transparency

AI-assisted planning, implementation, debugging, and validation are documented in `AI_LOG.md`.

Supporting development session records are maintained in `docs/ai-transcripts/`.

## Hackathon

**Event:** Mycrobo Hackathon  
**Dates:** 17–18 November 2026  
**Submission:** Public GitHub repository link

## License

License to be selected before public release.