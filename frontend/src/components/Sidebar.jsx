import { useState, useEffect } from "react";
import {
  LayoutDashboard,
  ShieldCheck,
  Search,
  FileText,
  Settings,
  Code2,
  ChevronLeft,
  Activity,
} from "lucide-react";
import { checkHealth } from "../services/api";

const navigation = [
  { label: "Overview", icon: LayoutDashboard },
  { label: "Repository Audit", icon: Search },
  { label: "Security Findings", icon: ShieldCheck },
  { label: "Reports", icon: FileText },
];

function Sidebar({ activePage, setActivePage }) {
  const [apiStatus, setApiStatus] = useState("checking");

  useEffect(() => {
    let cancelled = false;

    async function check() {
      const result = await checkHealth();
      if (!cancelled) {
        setApiStatus(result.status === "healthy" ? "connected" : "unreachable");
      }
    }

    check();

    // Re-check every 30 seconds.
    const interval = setInterval(check, 30000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const statusLabel =
    apiStatus === "connected"
      ? "API connected"
      : apiStatus === "unreachable"
        ? "API unreachable"
        : "Checking API...";

  const statusDotClass =
    apiStatus === "connected"
      ? "status-dot connected"
      : apiStatus === "unreachable"
        ? "status-dot error"
        : "status-dot";

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">
          <ShieldCheck size={23} />
        </div>
        <div>
          <h2>CodeSentinel</h2>
          <span>AI SECURITY PLATFORM</span>
        </div>
      </div>

      <div className="workspace-label">WORKSPACE</div>

      <nav className="sidebar-nav">
        {navigation.map(({ label, icon: Icon }) => (
          <button
            key={label}
            className={`nav-item ${
              activePage === label ? "active" : ""
            }`}
            onClick={() => setActivePage(label)}
          >
            <Icon size={19} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="system-status">
          <Activity size={17} />
          <div>
            <strong>System status</strong>
            <span>{statusLabel}</span>
          </div>
          <span className={statusDotClass} />
        </div>

        <button
          className={`nav-item ${activePage === "Settings" ? "active" : ""}`}
          onClick={() => setActivePage("Settings")}
        >
          <Settings size={19} />
          <span>Settings</span>
        </button>

        <div className="sidebar-footer">
          <Code2 size={16} />
          <span>CodeSentinel AI</span>
          <ChevronLeft size={16} />
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
