import { useState, useEffect } from "react";
import {
  Shield,
  Server,
  Info,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Sliders,
  AlertTriangle,
  Code2,
} from "lucide-react";
import { checkHealth } from "../services/api";

const SECURITY_RULES = [
  { id: "SEC001", name: "Hardcoded Credential", severity: "HIGH", desc: "API keys, passwords, and tokens hardcoded in source." },
  { id: "SEC002", name: "SQL Injection", severity: "HIGH", desc: "Dynamic SQL constructed via string concatenation or interpolation." },
  { id: "SEC003", name: "Dynamic Evaluation", severity: "HIGH", desc: "Use of eval() executing untrusted expressions." },
  { id: "SEC004", name: "Command Injection", severity: "HIGH", desc: "Shell execution via os.system or subprocess shell=True." },
  { id: "SEC005", name: "Weak Cryptographic Hash", severity: "MEDIUM", desc: "Insecure MD5 or SHA-1 hashes used in security contexts." },
  { id: "SEC006", name: "Unsafe Deserialization", severity: "HIGH", desc: "Use of pickle.loads or unsafe yaml.load." },
  { id: "SEC007", name: "Debug Mode Enabled", severity: "LOW", desc: "Debug flags left active exposing sensitive diagnostics." },
  { id: "SEC008", name: "Wildcard CORS", severity: "MEDIUM", desc: "Overly permissive CORS allow_origins='*'." },
];

const QUALITY_RULES = [
  { id: "CG001", name: "Unresolved Work Marker", severity: "LOW/MED", desc: "TODO, FIXME, XXX, and HACK comment markers." },
  { id: "CG002", name: "Unimplemented Functionality", severity: "MEDIUM", desc: "Explicit NotImplementedError raises in code." },
  { id: "CG003", name: "Empty Pass Statement", severity: "LOW", desc: "Standalone pass statements representing hollow stubs." },
  { id: "CG004", name: "Missing Test Suite", severity: "MEDIUM", desc: "Repository has source code but no recognized test files." },
];

function Settings() {
  const [health, setHealth] = useState(null);
  const [checking, setChecking] = useState(true);

  const fetchHealth = async () => {
    setChecking(true);
    const result = await checkHealth();
    setHealth(result);
    setChecking(false);
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const isHealthy = health?.status === "healthy";

  return (
    <div className="dashboard-content">
      <section className="welcome-section">
        <div>
          <div className="eyebrow">
            <span className="eyebrow-dot" />
            SYSTEM CONFIGURATION
          </div>
          <h1>Platform Settings & Diagnostics</h1>
          <p>Inspect backend health status, active scanners, and detection rule catalogs.</p>
        </div>

        <button
          className="secondary-action-button"
          onClick={fetchHealth}
          disabled={checking}
          title="Re-query API health endpoint"
        >
          <RefreshCw size={15} className={checking ? "spin-icon" : ""} />
          {checking ? "Checking..." : "Refresh Status"}
        </button>
      </section>

      {/* API Health */}
      <section className="panel" style={{ marginBottom: 24 }}>
        <div className="panel-heading">
          <div>
            <h3>API Service Status</h3>
            <p>Live health probe for the FastAPI backend service</p>
          </div>
          <Server size={18} className="muted-icon" />
        </div>

        <div className="audit-details">
          <div className="audit-detail-row">
            <span className="detail-label">Service Connectivity</span>
            <strong>
              {checking ? (
                <span style={{ color: "#94a3b8" }}>Probing /health...</span>
              ) : isHealthy ? (
                <span className="audit-status">
                  <CheckCircle2 size={14} /> Healthy (Connected)
                </span>
              ) : (
                <span style={{ color: "#f87171", display: "flex", alignItems: "center", gap: 6 }}>
                  <XCircle size={14} /> Unreachable
                </span>
              )}
            </strong>
          </div>
          <div className="audit-detail-row">
            <span className="detail-label">Service Name</span>
            <strong>{health?.service || "CodeSentinel AI API"}</strong>
          </div>
          <div className="audit-detail-row">
            <span className="detail-label">OpenAPI Documentation</span>
            <strong>
              <a
                href="http://127.0.0.1:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "#60a5fa", textDecoration: "underline" }}
              >
                http://127.0.0.1:8000/docs (Swagger UI)
              </a>
            </strong>
          </div>
          <div className="audit-detail-row">
            <span className="detail-label">ReDoc Explorer</span>
            <strong>
              <a
                href="http://127.0.0.1:8000/redoc"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "#60a5fa", textDecoration: "underline" }}
              >
                http://127.0.0.1:8000/redoc
              </a>
            </strong>
          </div>
        </div>
      </section>

      {/* Scanner Engines */}
      <section className="panel" style={{ marginBottom: 24 }}>
        <div className="panel-heading">
          <div>
            <h3>Analysis Engines & Scanners</h3>
            <p>Active and planned static analysis integrations</p>
          </div>
          <Shield size={18} className="muted-icon" />
        </div>

        <div className="audit-details">
          <div className="audit-detail-row">
            <span className="detail-label">Security Scanner</span>
            <strong>
              <span className="audit-status">
                <CheckCircle2 size={14} /> Active (8 rules, heuristic regex & multiline)
              </span>
            </strong>
          </div>
          <div className="audit-detail-row">
            <span className="detail-label">Code Quality Scanner</span>
            <strong>
              <span className="audit-status">
                <CheckCircle2 size={14} /> Active (Python AST structural & pattern checks)
              </span>
            </strong>
          </div>
          <div className="audit-detail-row">
            <span className="detail-label">LangGraph Agent</span>
            <strong>
              <span className="audit-status">
                <CheckCircle2 size={14} /> Active (Deterministic workflow: P0–P4 priority & remediation)
              </span>
            </strong>
          </div>
          <div className="audit-detail-row">
            <span className="detail-label">Semgrep / Gitleaks / OSV</span>
            <strong style={{ color: "#64748b" }}>
              Planned external integrations (Heuristic scanners active as fallback)
            </strong>
          </div>
        </div>
      </section>

      {/* Rules Catalog */}
      <section className="panel" style={{ marginBottom: 24 }}>
        <div className="panel-heading">
          <div>
            <h3>Active Detection Rules</h3>
            <p>Built-in security and code gap rules</p>
          </div>
          <Sliders size={18} className="muted-icon" />
        </div>

        <div style={{ marginTop: 16 }}>
          <h4 style={{ color: "#93c5fd", fontSize: 13, marginBottom: 12, display: "flex", alignItems: "center", gap: 6 }}>
            <AlertTriangle size={15} /> Security Rules (SEC001–SEC008)
          </h4>
          <div className="findings-table-wrapper" style={{ marginBottom: 20 }}>
            <table className="findings-table">
              <thead>
                <tr>
                  <th style={{ width: 80 }}>Rule ID</th>
                  <th style={{ width: 180 }}>Name</th>
                  <th style={{ width: 90 }}>Severity</th>
                  <th>Detection Description</th>
                </tr>
              </thead>
              <tbody>
                {SECURITY_RULES.map((r) => (
                  <tr key={r.id}>
                    <td className="rule-id">{r.id}</td>
                    <td style={{ color: "#f1f5f9", fontWeight: 500 }}>{r.name}</td>
                    <td>
                      <span className={`severity-badge ${r.severity.toLowerCase()}`}>
                        {r.severity}
                      </span>
                    </td>
                    <td style={{ color: "#94a3b8" }}>{r.desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h4 style={{ color: "#86efac", fontSize: 13, marginBottom: 12, display: "flex", alignItems: "center", gap: 6 }}>
            <Code2 size={15} /> Code Quality & Gap Rules (CG001–CG004)
          </h4>
          <div className="findings-table-wrapper">
            <table className="findings-table">
              <thead>
                <tr>
                  <th style={{ width: 80 }}>Rule ID</th>
                  <th style={{ width: 180 }}>Name</th>
                  <th style={{ width: 90 }}>Severity</th>
                  <th>Detection Description</th>
                </tr>
              </thead>
              <tbody>
                {QUALITY_RULES.map((r) => (
                  <tr key={r.id}>
                    <td className="rule-id">{r.id}</td>
                    <td style={{ color: "#f1f5f9", fontWeight: 500 }}>{r.name}</td>
                    <td>
                      <span className="severity-badge medium">
                        {r.severity}
                      </span>
                    </td>
                    <td style={{ color: "#94a3b8" }}>{r.desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Architecture & Engineering Constraints */}
      <section className="panel">
        <div className="panel-heading">
          <div>
            <h3>Security Architecture & Hardening</h3>
            <p>Engineered guardrails and system parameters</p>
          </div>
          <Info size={18} className="muted-icon" />
        </div>

        <div className="audit-details">
          <div className="audit-detail-row">
            <span className="detail-label">Execution Model</span>
            <strong>Strict Read-Only — target source code is never executed or imported</strong>
          </div>
          <div className="audit-detail-row">
            <span className="detail-label">Path Traversal Defense</span>
            <strong>Path resolution resolves symlinks and strictly validates targets inside SCAN_ROOT</strong>
          </div>
          <div className="audit-detail-row">
            <span className="detail-label">Safety Resource Quotas</span>
            <strong>Max 5,000 files · Max 100 MB repo size · Max 5 MB per individual file</strong>
          </div>
          <div className="audit-detail-row">
            <span className="detail-label">Credential Redaction</span>
            <strong>Auto-redaction masks credential values in reported evidence</strong>
          </div>
          <div className="audit-detail-row">
            <span className="detail-label">Report Export Endpoints</span>
            <strong>POST /api/audit/export/json · POST /api/audit/export/markdown</strong>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Settings;
