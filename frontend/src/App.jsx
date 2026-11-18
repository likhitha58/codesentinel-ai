import { useState, useEffect } from "react";

import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import Dashboard from "./pages/Dashboard";
import AuditForm from "./components/AuditForm";
import SecurityFindings from "./pages/SecurityFindings";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";

import { auditRepository } from "./services/api";

import "./App.css";

const STORAGE_KEY = "codesentinel_latest_audit";

function App() {
  const [activePage, setActivePage] = useState("Overview");
  const [auditData, setAuditData] = useState(() => {
    try {
      const saved = sessionStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Persist audit data in session storage whenever it updates
  useEffect(() => {
    try {
      if (auditData) {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(auditData));
      }
    } catch (err) {
      console.warn("Could not persist audit data to sessionStorage", err);
    }
  }, [auditData]);

  const handleAudit = async (repository) => {
    setLoading(true);
    setError("");

    try {
      const result = await auditRepository(repository);
      setAuditData(result);
      setActivePage("Overview");
    } catch (err) {
      setError(err.message || "Something went wrong while auditing.");
    } finally {
      setLoading(false);
    }
  };

  const handleSearchChange = (query) => {
    setSearchQuery(query);
  };

  const handleSearchSubmit = (query) => {
    setSearchQuery(query);
    setActivePage("Security Findings");
  };

  return (
    <div className="app-layout">
      <Sidebar
        activePage={activePage}
        setActivePage={setActivePage}
      />

      <main className="main-area">
        <Header
          activePage={activePage}
          searchQuery={searchQuery}
          onSearchChange={handleSearchChange}
          onSearchSubmit={handleSearchSubmit}
          hasAuditData={Boolean(auditData)}
        />

        {activePage === "Overview" ? (
          <Dashboard
            auditData={auditData}
            loading={loading}
            onStartAudit={() => setActivePage("Repository Audit")}
            onViewFindings={() => setActivePage("Security Findings")}
            onViewReports={() => setActivePage("Reports")}
          />
        ) : activePage === "Repository Audit" ? (
          <div className="dashboard-content">
            <section className="welcome-section">
              <div>
                <div className="eyebrow">
                  <span className="eyebrow-dot" />
                  REPOSITORY AUDIT
                </div>
                <h1>Start Repository Scan</h1>
                <p>
                  Perform static security, code quality, and gap analysis on
                  targets inside the configured scan root.
                </p>
              </div>
            </section>

            <AuditForm
              onAudit={handleAudit}
              loading={loading}
            />

            {error && (
              <div className="audit-error" role="alert">
                {error}
              </div>
            )}
          </div>
        ) : activePage === "Security Findings" ? (
          <SecurityFindings
            auditData={auditData}
            initialSearch={searchQuery}
            onStartAudit={() => setActivePage("Repository Audit")}
          />
        ) : activePage === "Reports" ? (
          <Reports
            auditData={auditData}
            onStartAudit={() => setActivePage("Repository Audit")}
          />
        ) : activePage === "Settings" ? (
          <Settings />
        ) : (
          <div className="page-placeholder">
            <h2>{activePage}</h2>
            <p>This section is coming soon.</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
