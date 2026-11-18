import { useMemo, useState, useEffect } from "react";
import {
  Search,
  ShieldAlert,
  ChevronDown,
  AlertCircle,
  ScanSearch,
} from "lucide-react";

const severityOrder = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"];

function SecurityFindings({ auditData, initialSearch = "", onStartAudit }) {
  const [search, setSearch] = useState(initialSearch);
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [categoryFilter, setCategoryFilter] = useState("ALL");

  useEffect(() => {
    if (initialSearch) {
      setSearch(initialSearch);
    }
  }, [initialSearch]);

  const findings = auditData?.findings || [];

  const recommendations =
    auditData?.agent_analysis?.recommendations || [];

  const prioritizedFindings =
    auditData?.agent_analysis?.prioritized_findings || [];

  const filteredFindings = useMemo(() => {
    return findings
      .filter((finding) => {
        const query = search.toLowerCase();

        const matchesSearch =
          !query ||
          finding.title?.toLowerCase().includes(query) ||
          finding.rule_id?.toLowerCase().includes(query) ||
          finding.file?.toLowerCase().includes(query) ||
          finding.description?.toLowerCase().includes(query);

        const matchesSeverity =
          severityFilter === "ALL" ||
          finding.severity === severityFilter;

        const matchesCategory =
          categoryFilter === "ALL" ||
          finding.category === categoryFilter;

        return matchesSearch && matchesSeverity && matchesCategory;
      })
      .sort(
        (a, b) =>
          severityOrder.indexOf(a.severity) -
          severityOrder.indexOf(b.severity)
      );
  }, [findings, search, severityFilter, categoryFilter]);

  const getRecommendation = (ruleId) =>
    recommendations.find((item) => item.rule_id === ruleId);

  const getPriority = (ruleId) =>
    prioritizedFindings.find((item) => item.rule_id === ruleId);

  if (!auditData) {
    return (
      <div className="dashboard-content">
        <section className="welcome-section">
          <div>
            <div className="eyebrow">SECURITY INTELLIGENCE</div>
            <h1>Security Findings</h1>
            <p>Inspect security and code-quality observations.</p>
          </div>
        </section>

        <div className="empty-findings" style={{ padding: "60px 20px" }}>
          <ShieldAlert size={40} style={{ color: "#60a5fa", marginBottom: "16px" }} />
          <strong style={{ fontSize: "16px", color: "#f8fafc" }}>No audit results available</strong>
          <span style={{ maxWidth: "420px", marginBottom: "20px" }}>
            Run a repository audit to inspect vulnerability findings, code smells, and remediation guidance.
          </span>
          {onStartAudit && (
            <button className="primary-button" onClick={onStartAudit}>
              <ScanSearch size={16} />
              Start an audit now
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-content">
      <section className="welcome-section">
        <div>
          <div className="eyebrow">
            <span className="eyebrow-dot" />
            SECURITY INTELLIGENCE
          </div>
          <h1>Security Findings</h1>
          <p>
            Review detected indicators, inspect evidence, and
            understand recommended remediation.
          </p>
        </div>

        {onStartAudit && (
          <button className="secondary-action-button" onClick={onStartAudit}>
            <ScanSearch size={16} />
            Scan another repo
          </button>
        )}
      </section>

      <section className="findings-summary">
        <div>
          <span>Total findings</span>
          <strong>{findings.length}</strong>
        </div>
        <div>
          <span>Security</span>
          <strong>
            {findings.filter((f) => f.category === "SECURITY").length}
          </strong>
        </div>
        <div>
          <span>Code quality</span>
          <strong>
            {findings.filter((f) => f.category === "CODE_QUALITY").length}
          </strong>
        </div>
        <div>
          <span>Needs review</span>
          <strong>
            {findings.filter((f) => f.status === "NEEDS_REVIEW").length}
          </strong>
        </div>
      </section>

      <section className="panel findings-page-panel">
        <div className="panel-heading">
          <div>
            <h3>Detected Findings</h3>
            <p>
              Repository: {auditData.repository?.repository || "Unknown"}
            </p>
          </div>
          <span className="findings-count">
            {filteredFindings.length} results
          </span>
        </div>

        <div className="findings-filters">
          <div className="findings-search">
            <Search size={17} />
            <input
              type="search"
              placeholder="Search rule, finding or file..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
          >
            <option value="ALL">All severities</option>
            {severityOrder.map((severity) => (
              <option key={severity} value={severity}>
                {severity}
              </option>
            ))}
          </select>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            <option value="ALL">All categories</option>
            <option value="SECURITY">Security</option>
            <option value="CODE_QUALITY">Code quality</option>
          </select>
        </div>

        {filteredFindings.length === 0 ? (
          <div className="empty-findings">
            <Search size={25} />
            <strong>No matching findings</strong>
            <span>Try changing your search or filters.</span>
          </div>
        ) : (
          <div className="security-findings-list">
            {filteredFindings.map((finding, index) => {
              const recommendation = getRecommendation(finding.rule_id);
              const priority = getPriority(finding.rule_id);

              return (
                <details
                  className="security-finding"
                  key={`${finding.rule_id}-${index}`}
                >
                  <summary>
                    <div className="finding-main">
                      <span
                        className={`severity-badge ${finding.severity?.toLowerCase()}`}
                      >
                        {finding.severity}
                      </span>

                      <div className="finding-summary-text">
                        <strong>{finding.title}</strong>
                        <span>
                          {finding.rule_id} · {finding.file}
                          {finding.line > 0 ? `:${finding.line}` : ""}
                        </span>
                      </div>
                    </div>

                    <div className="finding-summary-right">
                      <span className="priority-label">
                        {priority?.priority || recommendation?.priority || "—"}
                      </span>
                      <ChevronDown size={18} />
                    </div>
                  </summary>

                  <div className="finding-expanded">
                    <div className="finding-description">
                      <h4>Description</h4>
                      <p>{finding.description}</p>
                    </div>

                    <div className="finding-metadata">
                      <div>
                        <span>Category</span>
                        <strong>
                          {finding.category?.replace("_", " ")}
                        </strong>
                      </div>
                      <div>
                        <span>Confidence</span>
                        <strong>{finding.confidence || "Not specified"}</strong>
                      </div>
                      <div>
                        <span>Status</span>
                        <strong>{finding.status || "Not specified"}</strong>
                      </div>
                      <div>
                        <span>Agent priority</span>
                        <strong>
                          {priority?.priority ||
                            recommendation?.priority ||
                            "Not available"}
                        </strong>
                      </div>
                    </div>

                    {finding.evidence && (
                      <div className="finding-evidence">
                        <h4>Evidence</h4>
                        <pre>{finding.evidence}</pre>
                      </div>
                    )}

                    <div className="finding-remediation">
                      <h4>
                        <AlertCircle size={16} />
                        Recommended remediation
                      </h4>
                      <p>
                        {recommendation?.recommended_action ||
                          priority?.recommended_action ||
                          priority?.action ||
                          "No specific remediation recommendation was returned by the agent."}
                      </p>
                    </div>

                    <div className="finding-review-note">
                      Automated finding — manual validation is required
                      before treating this as a confirmed issue.
                    </div>
                  </div>
                </details>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}

export default SecurityFindings;
