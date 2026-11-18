import { useState } from "react";
import {
  FileText,
  FileJson,
  Download,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Clock3,
  ScanSearch,
} from "lucide-react";
import { exportJsonReport, exportMarkdownReport, downloadBlob } from "../services/api";

function Reports({ auditData, onStartAudit }) {
  const [jsonLoading, setJsonLoading] = useState(false);
  const [markdownLoading, setMarkdownLoading] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState("");
  const [error, setError] = useState("");

  const repository = auditData?.repository;
  const summary = auditData?.scan_summary;
  const severitySummary = summary?.severity_summary || {};
  const repoName = repository?.repository || "";

  const formatDate = (date) => {
    if (!date) return "Not available";
    return new Date(date).toLocaleString();
  };

  const handleJsonDownload = async () => {
    setJsonLoading(true);
    setError("");
    setDownloadSuccess("");
    try {
      const { blob, filename } = await exportJsonReport(repoName);
      downloadBlob(blob, filename);
      setDownloadSuccess(`Downloaded ${filename} successfully!`);
    } catch (err) {
      setError(err.message || "Failed to download JSON report.");
    } finally {
      setJsonLoading(false);
    }
  };

  const handleMarkdownDownload = async () => {
    setMarkdownLoading(true);
    setError("");
    setDownloadSuccess("");
    try {
      const { blob, filename } = await exportMarkdownReport(repoName);
      downloadBlob(blob, filename);
      setDownloadSuccess(`Downloaded ${filename} successfully!`);
    } catch (err) {
      setError(err.message || "Failed to download Markdown report.");
    } finally {
      setMarkdownLoading(false);
    }
  };

  if (!auditData) {
    return (
      <div className="dashboard-content">
        <section className="welcome-section">
          <div>
            <div className="eyebrow">AUDIT REPORTS</div>
            <h1>Reports & Exports</h1>
            <p>Download comprehensive audit reports in JSON or Markdown format.</p>
          </div>
        </section>

        <div className="empty-findings" style={{ padding: "60px 20px" }}>
          <FileText size={40} style={{ color: "#60a5fa", marginBottom: "16px" }} />
          <strong style={{ fontSize: "16px", color: "#f8fafc" }}>No audit report available yet</strong>
          <span style={{ maxWidth: "420px", marginBottom: "20px" }}>
            Run an audit against a repository in your scan target directory to generate downloadable security reports.
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
            AUDIT REPORTS
          </div>
          <h1>Reports & Exports</h1>
          <p>
            Download the audit report for{" "}
            <strong>{repoName}</strong> in your preferred format.
          </p>
        </div>

        {onStartAudit && (
          <button className="secondary-action-button" onClick={onStartAudit}>
            <ScanSearch size={16} />
            Scan another repo
          </button>
        )}
      </section>

      {error && (
        <div className="audit-error" role="alert">
          <AlertCircle size={16} style={{ marginRight: 8, verticalAlign: "text-bottom" }} />
          {error}
        </div>
      )}

      {downloadSuccess && (
        <div className="audit-success" role="status">
          <CheckCircle2 size={16} style={{ marginRight: 8, verticalAlign: "text-bottom" }} />
          {downloadSuccess}
        </div>
      )}

      {/* Summary Stat Cards */}
      <section className="findings-summary">
        <div>
          <span>Audit Status</span>
          <strong className="audit-status" style={{ fontSize: "18px", marginTop: "4px" }}>
            <span className="status-dot connected" />
            {auditData.audit_status}
          </strong>
        </div>
        <div>
          <span>Total Findings</span>
          <strong>{summary?.total_findings  |  0}</strong>
        </div>
        <div>
          <span>Security Indicators</span>
          <strong>{summary?.security_findings  |  0}</strong>
        </div>
        <div>
          <span>Code Quality Gaps</span>
          <strong>{summary?.quality_findings  |  0}</strong>
        </div>
      </section>

      {/* Report metadata panel */}
      <section className="panel" style={{ marginBottom: 24 }}>
        <div className="panel-heading">
          <div>
            <h3>Audit Snapshot</h3>
            <p>Metadata from the latest analysis run</p>
          </div>
          <Clock3 size={18} className="muted-icon" />
        </div>

        <div className="audit-details">
          <div className="audit-detail-row">
            <span className="detail-label">Target Repository</span>
            <strong>{repoName}</strong>
          </div>
          <div className="audit-detail-row">
            <span className="detail-label">Audit Timestamp</span>
            <strong>{formatDate(auditData.generated_at)}</strong>
          </div>
          <div className="audit-detail-row">
            <span className="detail-label">Detected Languages</span>
            <strong>
              {Object.keys(repository?.languages || {}).join(", ") || "None detected"}
            </strong>
          </div>
          <div className="audit-detail-row">
            <span className="detail-label">Files Analyzed</span>
            <strong>{summary?.repository_files  |  0} files</strong>
          </div>
          <div className="audit-detail-row">
            <span className="detail-label">Severity Breakdown</span>
            <strong>
              {Object.entries(severitySummary)
                .filter(([, count]) => count > 0)
                .map(([sev, count]) => `${sev}: ${count}`)
                .join(" · ") || "0 findings"}
            </strong>
          </div>
          <div className="audit-detail-row">
            <span className="detail-label">Agent Processing</span>
            <strong>
              {auditData.agent_analysis?.agent_type || "LangGraph deterministic workflow"}
            </strong>
          </div>
          <div className="audit-detail-row">
            <span className="detail-label">Execution Mode</span>
            <strong>
              {auditData.read_only ? "Strict Read-Only (Safe)" : "Unverified"}
            </strong>
          </div>
        </div>
      </section>

      {/* Download action cards */}
      <section className="dashboard-grid">
        <div className="panel report-download-card">
          <div className="report-download-icon">
            <FileJson size={32} />
          </div>
          <h3>Structured JSON Export</h3>
          <p>
            Complete raw dataset including repository discovery metadata, normalized security and quality findings with confidence ratings, LangGraph prioritization, and recommended actions. Ideal for CI/CD ingestion.
          </p>
          <button
            className="primary-button"
            onClick={handleJsonDownload}
            disabled={jsonLoading || markdownLoading}
            style={{ width: "100%", justifyContent: "center" }}
          >
            {jsonLoading ? (
              <>
                <Loader2 size={16} className="spin-icon" />
                Generating JSON...
              </>
            ) : (
              <>
                <Download size={16} />
                Download JSON Report
              </>
            )}
          </button>
        </div>

        <div className="panel report-download-card">
          <div className="report-download-icon">
            <FileText size={32} />
          </div>
          <h3>Formatted Markdown Report</h3>
          <p>
            Human-readable security audit report complete with executive summary, prioritized findings tables, remediation guidance, scanner notices, and audit disclaimers. Ready for stakeholder review.
          </p>
          <button
            className="primary-button"
            onClick={handleMarkdownDownload}
            disabled={jsonLoading || markdownLoading}
            style={{ width: "100%", justifyContent: "center" }}
          >
            {markdownLoading ? (
              <>
                <Loader2 size={16} className="spin-icon" />
                Generating Markdown...
              </>
            ) : (
              <>
                <Download size={16} />
                Download Markdown Report
              </>
            )}
          </button>
        </div>
      </section>
    </div>
  );
}

export default Reports;
