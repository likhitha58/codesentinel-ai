import {
  ShieldAlert,
  FolderGit2,
  AlertTriangle,
  Code2,
  ScanSearch,
  Clock3,
  CheckCircle2,
  FileText,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";

import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from "recharts";

import StatCard from "../components/StatCard";

const SEVERITY_COLORS = {
  CRITICAL: "#ef4444",
  HIGH: "#f97316",
  MEDIUM: "#eab308",
  LOW: "#3b82f6",
  INFO: "#64748b",
};

function Dashboard({ auditData, loading, onStartAudit, onViewFindings, onViewReports }) {
  const repository = auditData?.repository;
  const summary = auditData?.scan_summary;
  const severitySummary = summary?.severity_summary || {};
  const findings = auditData?.findings || [];

  const severityData = Object.entries(severitySummary).map(
    ([severity, count]) => ({
      name: severity,
      value: count,
    })
  );

  const highSeverity =
    (severitySummary.HIGH || 0) +
    (severitySummary.CRITICAL || 0);

  const formatDate = (date) => {
    if (!date) return "Not available";
    return new Date(date).toLocaleString();
  };

  return (
    <div className="dashboard-content">
      <section className="welcome-section">
        <div>
          <div className="eyebrow">
            <span className="eyebrow-dot" />
            REPOSITORY INTELLIGENCE
          </div>

          <h1>Security Overview</h1>

          <p>
            Identify vulnerabilities, inspect code quality,
            and strengthen your software repositories.
          </p>
        </div>

        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
          {auditData && (
            <button
              className="secondary-action-button"
              onClick={onViewReports}
            >
              <FileText size={16} />
              Export reports
            </button>
          )}

          <button className="primary-button" onClick={onStartAudit}>
            <ScanSearch size={17} />
            Start new audit
          </button>
        </div>
      </section>

      {loading && (
        <div className="audit-loading">
          <ScanSearch size={18} />
          Scanning repository. Please wait...
        </div>
      )}

      <section className="stats-grid">
        <StatCard
          title="Total Findings"
          value={summary ? summary.total_findings : "—"}
          description={
            summary
              ? "Findings in latest audit"
              : "Run an audit to see findings"
          }
          icon={ShieldAlert}
          tone="purple"
        />

        <StatCard
          title="Files Scanned"
          value={summary ? summary.repository_files : "—"}
          description={
            repository
              ? `${repository.total_directories} directories detected`
              : "No repository scanned yet"
          }
          icon={FolderGit2}
          tone="blue"
        />

        <StatCard
          title="High Severity"
          value={summary ? highSeverity : "—"}
          description="Critical and high findings"
          icon={AlertTriangle}
          tone="orange"
        />

        <StatCard
          title="Code Quality"
          value={summary ? summary.quality_findings : "—"}
          description="Code-quality observations"
          icon={Code2}
          tone="green"
        />
      </section>

      <section className="dashboard-grid">
        <div className="panel severity-panel">
          <div className="panel-heading">
            <div>
              <h3>Severity Distribution</h3>
              <p>Breakdown of all detected findings</p>
            </div>

            <ShieldAlert size={18} className="muted-icon" />
          </div>

          {!auditData ? (
            <div className="empty-chart">
              <div className="empty-chart-icon">
                <ShieldAlert size={30} />
              </div>
              <strong>No audit data yet</strong>
              <span>
                Severity distribution will appear after your first audit.
              </span>
            </div>
          ) : findings.length === 0 ? (
            <div className="empty-chart">
              <CheckCircle2 size={30} />
              <strong>No findings detected</strong>
              <span>The latest audit returned no findings.</span>
            </div>
          ) : (
            <div className="severity-chart">
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={severityData.filter((item) => item.value > 0)}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="45%"
                    innerRadius={65}
                    outerRadius={95}
                    paddingAngle={3}
                  >
                    {severityData
                      .filter((item) => item.value > 0)
                      .map((entry) => (
                        <Cell
                          key={entry.name}
                          fill={SEVERITY_COLORS[entry.name] || "#64748b"}
                        />
                      ))}
                  </Pie>

                  <Tooltip
                    contentStyle={{
                      background: "#111c2e",
                      border: "1px solid #334155",
                      borderRadius: "8px",
                      color: "#f8fafc",
                    }}
                  />

                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div className="panel activity-panel">
          <div className="panel-heading">
            <div>
              <h3>Latest Audit</h3>
              <p>Most recent repository analysis</p>
            </div>

            <Clock3 size={18} className="muted-icon" />
          </div>

          {!auditData ? (
            <div className="empty-activity">
              <FolderGit2 size={27} />
              <strong>No recent activity</strong>
              <span>Your audit details will appear here.</span>
            </div>
          ) : (
            <div className="audit-details">
              <div className="audit-status-row">
                <span className="detail-label">Audit status</span>
                <span className="audit-status">
                  <span className="status-dot connected" />
                  {auditData.audit_status}
                </span>
              </div>

              <div className="audit-detail-row">
                <span className="detail-label">Repository</span>
                <strong>{repository?.repository || "Unknown"}</strong>
              </div>

              <div className="audit-detail-row">
                <span className="detail-label">Languages</span>
                <strong>
                  {Object.keys(repository?.languages || {}).join(", ") || "—"}
                </strong>
              </div>

              <div className="audit-detail-row">
                <span className="detail-label">Generated</span>
                <strong>{formatDate(auditData.generated_at)}</strong>
              </div>

              <div className="audit-detail-row">
                <span className="detail-label">Execution mode</span>
                <strong>
                  {auditData.read_only ? "Read only" : "Not confirmed"}
                </strong>
              </div>
            </div>
          )}
        </div>
      </section>

      <section className="panel findings-panel">
        <div className="panel-heading">
          <div>
            <h3>Recent Findings</h3>
            <p>Security and code-quality observations</p>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <span className="findings-count">
              {findings.length} findings
            </span>
            {findings.length > 0 && (
              <button
                className="text-button"
                onClick={onViewFindings}
                style={{ cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 4 }}
              >
                <span>View all</span>
                <ArrowRight size={14} />
              </button>
            )}
          </div>
        </div>

        {!auditData ? (
          <div className="empty-findings">
            <ShieldAlert size={25} />
            <strong>No findings to display</strong>
            <span>
              Run a repository audit to populate this section.
            </span>
          </div>
        ) : findings.length === 0 ? (
          <div className="empty-findings">
            <CheckCircle2 size={25} />
            <strong>No findings detected</strong>
            <span>The latest repository audit returned no findings.</span>
          </div>
        ) : (
          <div className="findings-table-wrapper">
            <table className="findings-table">
              <thead>
                <tr>
                  <th>Rule</th>
                  <th>Finding</th>
                  <th>Category</th>
                  <th>Severity</th>
                  <th>Location</th>
                </tr>
              </thead>

              <tbody>
                {findings.slice(0, 6).map((finding, index) => (
                  <tr key={`${finding.rule_id}-${index}`}>
                    <td className="rule-id">{finding.rule_id}</td>
                    <td>
                      <div className="finding-title">
                        {finding.title}
                      </div>
                      <div className="finding-confidence">
                        {finding.status} · {finding.confidence} confidence
                      </div>
                    </td>
                    <td>{finding.category?.replace("_", " ") || "—"}</td>
                    <td>
                      <span
                        className={`severity-badge ${finding.severity?.toLowerCase()}`}
                      >
                        {finding.severity}
                      </span>
                    </td>
                    <td>
                      {finding.file}
                      {finding.line > 0 ? `:${finding.line}` : ""}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {findings.length > 6 && (
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0 0" }}>
            <p className="more-findings" style={{ margin: 0, padding: 0 }}>
              Showing 6 of {findings.length} findings.
            </p>
            <button
              className="text-button"
              onClick={onViewFindings}
              style={{ cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 4 }}
            >
              <span>Explore all findings in Security Findings tab</span>
              <ArrowRight size={14} />
            </button>
          </div>
        )}
      </section>
    </div>
  );
}

export default Dashboard;
