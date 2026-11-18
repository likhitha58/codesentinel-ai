
# CodeSentinel AI — System Architecture

**Version:** 1.0
**Last updated:** 18 November 2026

## 1. Overview

CodeSentinel AI is a modular, read-only repository auditing system.

Its architecture separates repository discovery, static analysis, audit orchestration, agent-based prioritization, and report generation.

The design is intended to support repositories using different programming languages and frameworks without requiring knowledge of their application architecture.

## 2. High-Level Architecture

```text
                  Repository Input
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
                 Unified Audit Service
                         |
                         v
                 Normalized Findings
                         |
                         v
                   LangGraph Agent
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
         Prioritize  Recommendations Summary
             |           |           |
             +-----------+-----------+
                         |
                         v
                   Report Exporter
                         |
                  +------+------+
                  |             |
                  v             v
                 JSON        Markdown
```

## 3. Module Responsibilities

### 3.1 Repository Intelligence

**File:** `backend/app/analyzers/project_detector.py`

Responsibilities:
- Validate the repository directory.
- Traverse repository files.
- Detect programming languages using extensions.
- Identify selected frameworks and dependency manifests.
- Count files, directories, and total size.
- Exclude common generated and dependency directories.
- Avoid following symbolic links.
- Skip oversized files.

Output includes:
- Repository name and path.
- File and directory counts.
- Language distribution.
- Detected frameworks.
- Important files.
- Discovered file paths.
- Excluded directory names.

Framework detection currently checks selected root-level manifests.

### 3.2 Security Scanner

**File:** `backend/app/scanners/security_scanner.py`

The security scanner performs read-only pattern-based analysis.

It currently includes eight heuristic rules:

| Rule | Purpose |
|---|---|
| SEC001 | Possible hardcoded credentials |
| SEC002 | Possible SQL injection |
| SEC003 | Unsafe dynamic evaluation |
| SEC004 | Potential command injection |
| SEC005 | Weak cryptographic hashing |
| SEC006 | Unsafe deserialization |
| SEC007 | Debug mode enabled |
| SEC008 | Potentially unsafe CORS configuration |

Each finding contains:
- Rule ID.
- Title.
- Severity.
- Relative file path.
- Line number.
- Description.
- Redacted evidence where applicable.
- Confidence.
- Review status.

The scanner does not prove exploitability. Findings require manual review.

### 3.3 Code Quality Scanner

**File:** `backend/app/scanners/code_quality_scanner.py`

The scanner identifies possible incomplete implementations and coding gaps.

| Rule | Purpose |
|---|---|
| CG001 | Unresolved work markers |
| CG002 | Explicit NotImplementedError |
| CG003 | Possible empty implementation |
| CG004 | Missing recognizable test files |

Python AST analysis is used for structural checks. Pattern-based checks are used for other supported languages.

### 3.4 Unified Audit Service

**File:** `backend/app/services/audit_service.py`

The audit service coordinates the repository analyzer and both scanners.

Processing steps:
1. Resolve and validate the repository path.
2. Analyze repository metadata.
3. Run the security scanner.
4. Run the code-quality scanner.
5. Normalize and combine findings.
6. Add finding categories and scanner sources.
7. Sort findings by severity.
8. Calculate consolidated severity counts.
9. Construct the final audit report.

The report contains:
- Audit status and generation timestamp.
- Repository metadata.
- Scan summary.
- Consolidated findings.
- Scanner notices.
- Read-only indicator.

### 3.5 LangGraph Audit Agent

**File:** `backend/app/agents/audit_agent.py`

The LangGraph workflow consists of three sequential nodes.

**Node 1 — Prioritize Findings**
- Maps severity levels to operational priorities.
- Adds predefined remediation guidance.
- Sorts findings by priority.

**Node 2 — Generate Recommendations**
- Groups findings by rule ID.
- Counts repeated occurrences.
- Records affected file locations.
- Produces consolidated remediation actions.

**Node 3 — Generate Executive Summary**
- Uses verified audit counts.
- Reports security and code-quality findings.
- Highlights P0/P1 findings.
- Includes a manual-validation disclaimer.

Current implementation is deterministic and does not call an LLM.

### 3.6 Report Exporter

**File:** `backend/app/services/report_exporter.py`

Supports:
- JSON serialization of the complete report.
- Markdown formatting of repository metadata.
- Finding tables and detailed evidence.
- Agent priorities and recommendations.
- Scanner notices and disclaimers.

Supported formats:
- `.json`
- `.md`

### 3.7 API and Presentation Layer

Planned components:
- FastAPI REST endpoints.
- React + Vite dashboard.
- Repository submission interface.
- Findings visualization.
- Report access and download.

These components are not yet implemented.

## 4. Data Flow

The repository analyzer and scanners operate independently.

The unified audit service combines their outputs into a common finding collection.

A normalized finding contains fields such as:

```json
{
  "rule_id": "SEC001",
  "title": "Possible hardcoded credential",
  "severity": "HIGH",
  "file": "config.py",
  "line": 10,
  "category": "SECURITY",
  "source": "security_scanner",
  "confidence": "LOW",
  "status": "NEEDS_REVIEW"
}
```

The agent adds priority and remediation information without modifying the original report's findings.

The exporter serializes the enhanced report into JSON and Markdown.

## 5. Design Decisions

### Read-only analysis
The system does not automatically modify target source files.

### Modular scanners
Security and code-quality analysis are maintained as independent modules.

### Normalized findings
A common finding structure allows future analyzers to integrate without redesigning the reporting layer.

### Architecture-agnostic discovery
Repository metadata is inferred from files and manifests rather than assuming a specific application architecture.

### Deterministic initial agent
The current LangGraph workflow provides reproducible prioritization and recommendations without requiring an external LLM service.

### Human validation
Automated findings are indicators, not confirmed defects. Developers remain responsible for validating and fixing them.

## 6. Current Limitations

- Security detection relies primarily on regular expressions.
- Python structural analysis does not extend to every language.
- Framework detection is limited to selected root-level manifests.
- Test discovery depends on naming conventions.
- Prioritization and remediation guidance are rule-based.
- No LLM reasoning is integrated.
- API and frontend layers remain pending.
- External scanning engines are not integrated.

## 7. Future Architecture Extensions

Potential enhancements include:
- LLM-based finding validation and explanation.
- Semgrep integration.
- Gitleaks integration.
- OSV-Scanner dependency analysis.
- Multi-language AST or parser support.
- FastAPI service layer.
- React dashboard.
- Repository upload and isolated scanning.
- Audit history and comparison between runs.
