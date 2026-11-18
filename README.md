
# CodeSentinel AI

**Architecture-Agnostic Repository Security, Code Quality & Completeness Auditor**

CodeSentinel AI is a read-only repository auditing tool developed for the Mycrobo Hackathon (17–18 November 2026). It analyzes software repositories to identify potentially unsafe coding patterns, incomplete implementations, code-quality issues, and development gaps.

It combines repository intelligence, heuristic static analysis, a unified audit engine, and a LangGraph-based workflow to prioritize findings and generate remediation recommendations.

> **Current status:** Core scanning, audit orchestration, agent workflow, and JSON/Markdown reporting are implemented and tested. FastAPI integration, the React dashboard, and LLM-powered reasoning are not yet implemented.

## 1. Problem Statement

Software repositories can accumulate security weaknesses, unfinished implementations, inconsistent coding practices, and technical debt. These issues become harder to identify across projects that use different languages, frameworks, and architectures.

CodeSentinel AI aims to provide a unified auditing workflow that helps developers discover, understand, and prioritize these issues without executing the target repository's code.

## 2. Key Features

### Repository Intelligence
- Detects programming languages using file extensions.
- Identifies selected frameworks and dependency manifests.
- Counts files, directories, and repository size.
- Excludes common generated, dependency, and environment directories.
- Produces structured repository metadata.

### Security Analysis

The heuristic security scanner currently implements eight rules:

| Rule | Detection | Severity |
|---|---|---|
| SEC001 | Possible hardcoded credentials | HIGH |
| SEC002 | Possible SQL injection | HIGH |
| SEC003 | Unsafe dynamic evaluation | HIGH |
| SEC004 | Potential command injection | HIGH |
| SEC005 | Weak cryptographic hashing | MEDIUM |
| SEC006 | Unsafe deserialization | HIGH |
| SEC007 | Debug mode enabled | LOW |
| SEC008 | Potentially unsafe CORS configuration | MEDIUM |

Credential-like evidence is redacted in reported findings.

### Code Quality and Completeness Analysis

| Rule | Detection |
|---|---|
| CG001 | TODO, FIXME, XXX, and HACK markers |
| CG002 | Explicit NotImplementedError |
| CG003 | Possible empty implementations |
| CG004 | No recognizable test files found |

Python structural checks use AST analysis. Other supported languages primarily use pattern-based detection.

### Unified Audit Engine
- Coordinates repository analysis and both scanners.
- Normalizes findings into a consolidated report.
- Preserves source, category, severity, location, and evidence.
- Calculates severity summaries.
- Maintains read-only analysis.

### LangGraph Audit Agent

The current deterministic LangGraph workflow:
1. Assigns priorities to findings.
2. Generates rule-specific remediation guidance.
3. Groups recommendations by rule.
4. Identifies affected file locations.
5. Generates an executive summary.

Priority mapping:

| Severity | Priority |
|---|---|
| CRITICAL | P0 |
| HIGH | P1 |
| MEDIUM | P2 |
| LOW | P3 |
| INFO | P4 |

**AI integration status:** The current workflow uses deterministic logic and predefined remediation guidance. LLM-powered reasoning is a future enhancement.

### Report Generation
- Exports consolidated reports as JSON.
- Exports readable Markdown reports.
- Includes repository metadata, scanner findings, severity summaries, agent priorities, and recommendations.
- Supports exporting selected formats.

## 3. Architecture

```text
                 Target Repository
                         |
                         v
               Repository Intelligence
                         |
             +-----------+-----------+
             |                       |
             v                       v
       Security Scanner       Code Quality Scanner
             |                       |
             +-----------+-----------+
                         |
                         v
                 Unified Audit Engine
                         |
                         v
                  Normalized Report
                         |
                         v
                  LangGraph Agent
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
          Priority   Recommendations  Summary
             |           |           |
             +-----------+-----------+
                         |
                         v
                  Report Exporter
                         |
                 +-------+-------+
                 |               |
                 v               v
                JSON          Markdown
```

## 4. Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.12 |
| API framework | FastAPI (installed; integration pending) |
| Agent orchestration | LangGraph |
| Structural analysis | Python AST |
| Pattern analysis | Python regular expressions |
| Data representation | Python dictionaries and JSON |
| Report generation | JSON and Markdown |
| Frontend | React + Vite (planned) |
| LLM integration | Google GenAI (planned) |

## 5. Project Structure

```text
codesentinel-ai/
|
|-- backend/
|   |-- app/
|   |   |-- analyzers/
|   |   |   |-- project_detector.py
|   |   |
|   |   |-- scanners/
|   |   |   |-- security_scanner.py
|   |   |   |-- code_quality_scanner.py
|   |   |
|   |   |-- services/
|   |   |   |-- audit_service.py
|   |   |   |-- report_exporter.py
|   |   |
|   |   |-- agents/
|   |       |-- audit_agent.py
|   |
|   |-- tests/
|   |   |-- sample_vulnerable.py
|   |   |-- test_security_scanner.py
|   |   |-- test_code_quality_scanner.py
|   |   |-- test_audit_service.py
|   |   |-- test_report_exporter.py
|   |   |-- test_audit_agent.py
|   |
|   |-- requirements.txt
|
|-- docs/
|   |-- architecture.md
|   |-- IMPLEMENTATION_STATUS.md
|   |-- ai-transcripts/
|       |-- 01_development_sessions.md
|
|-- reports/
|-- .gitignore
|-- README.MD
|-- AI_LOG.MD
```

## 6. Local Setup

### Prerequisites
- Python 3.12 or compatible version
- Git
- Windows, macOS, or Linux

### Backend setup (Windows PowerShell)

```powershell
git clone https://github.com/likhitha58/codesentinel-ai.git
cd codesentinel-ai
cd backend

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
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

### Run automated tests

From the backend directory:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

### Start the FastAPI server

From the backend directory:

```powershell
python -m uvicorn app.main:app --reload
```

Open the interactive API documentation:

`http://127.0.0.1:8000/docs`

Available endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Application information |
| GET | `/health` | Health check |
| POST | `/api/audit` | Audit a repository inside `backend/scan_targets/` |

Example audit request:

```json
{
  "repository": "demo-repo"
}
```

The API returns repository metadata, normalized findings, severity summaries, and deterministic LangGraph analysis.

### Run a unified audit with the agent

```powershell
python -c "from app.services.audit_service import build_audit_report; from app.agents.audit_agent import run_audit_agent; report=build_audit_report('..'); enhanced=run_audit_agent(report); print(enhanced['agent_analysis']['executive_summary'])"
```

### Export JSON and Markdown reports

```powershell
python -c "from app.services.audit_service import build_audit_report; from app.agents.audit_agent import run_audit_agent; from app.services.report_exporter import export_audit_report; report=build_audit_report('..'); enhanced=run_audit_agent(report); print(export_audit_report(enhanced, output_dir='../reports'))"
```

Generated reports are stored in the root `reports/` directory.

## 7. Validation Results

Latest verified automated test run:

**38 tests passed.**

| Test area | Tests |
|---|---:|
| API | 10 |
| Security scanner | 5 |
| Code-quality scanner | 8 |
| Unified audit service | 5 |
| Report exporter | 5 |
| LangGraph agent | 5 |
| **Total** | **38** |

Additional API validation:
- Root and health endpoints return successful responses.
- Invalid request payloads are rejected.
- Absolute paths and directory traversal are rejected.
- Missing repositories return HTTP 404.
- Repository file-count and total-size limits return HTTP 413.
- Unexpected audit processing failures return a controlled HTTP 500 response.
- A successful API request runs the unified audit and LangGraph workflow.

The deliberately vulnerable scanner fixture has previously produced seven known security indicators. A separate API demonstration repository produced six findings during end-to-end validation.

JSON and Markdown report generation, including agent analysis, was verified.

The intentionally vulnerable fixture is scanner input only. Its source code must never be executed.

## 8. Limitations

- Findings are heuristic indicators, not confirmed vulnerabilities or defects.
- Manual validation is required before treating a finding as a real issue.
- Python AST analysis is currently limited to Python files.
- Other supported languages primarily use pattern-based analysis.
- Framework detection currently checks selected root-level manifests.
- Missing-test detection relies on recognizable test naming conventions.
- The current LangGraph agent uses deterministic rules, not an LLM.
- The API currently scans repositories placed inside the configured `backend/scan_targets/` directory.
- API preflight limits are currently 5,000 files and 100 MB per repository.
- Advanced tools such as Semgrep, Gitleaks, and OSV-Scanner are not yet integrated.
- The React + Vite dashboard is not yet implemented.

## 9. Development Roadmap

- [x] Initialize repository and development environment.
- [x] Implement repository intelligence.
- [x] Implement heuristic security scanner.
- [x] Add multiline SQL injection detection.
- [x] Implement code-quality and coding-gap analysis.
- [x] Add automated regression tests.
- [x] Build unified audit service.
- [x] Export JSON and Markdown reports.
- [x] Implement LangGraph audit workflow.
- [x] Add finding prioritization and remediation recommendations.
- [x] Include agent analysis in Markdown reports.
- [x] Build FastAPI application and endpoints.
- [x] Restrict API repository paths to the configured scan directory.
- [x] Add repository file-count and total-size limits.
- [x] Add API error handling and automated tests.
- [ ] Build React + Vite dashboard.
- [ ] Add LLM-powered reasoning.
- [ ] Integrate advanced security analysis tools.
- [ ] Perform final end-to-end testing and prepare demonstration.

## 10. Security Considerations

CodeSentinel AI is designed to inspect repositories without executing their source code.

Implemented API safeguards:
- Restrict repository paths to the configured `backend/scan_targets/` directory.
- Reject absolute paths and directory traversal.
- Resolve paths to prevent symbolic-link escapes at repository selection.
- Exclude symbolic links during resource-limit traversal.
- Enforce a maximum of 5,000 files and 100 MB per repository.
- Return controlled errors without exposing internal exception details in API responses.
- Redact credential-like evidence in security findings.

Further safeguards are required before production deployment:
- Isolate any future external scanner execution.
- Add authentication and authorization if the API is exposed to untrusted users.
- Review resource limits and concurrency controls for deployment.
- Never commit API keys, credentials, or real secrets.

## 11. AI Development Transparency

AI assistance was used for project planning, implementation guidance, debugging, test design, and documentation.

The developer executed commands, reviewed generated code, applied changes, and verified implementation results.

Detailed development records are maintained in:
- `AI_LOG.MD`
- `docs/ai-transcripts/01_development_sessions.md`

## 12. Hackathon

**Event:** Mycrobo Hackathon
**Dates:** 17–18 November 2026
**Project:** CodeSentinel AI
**Repository:** https://github.com/likhitha58/codesentinel-ai
