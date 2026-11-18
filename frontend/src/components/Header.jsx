import { useState, useRef, useEffect } from "react";
import { Bell, Search, Command, CheckCircle2, ShieldAlert } from "lucide-react";

function Header({ activePage, searchQuery, onSearchChange, onSearchSubmit, hasAuditData }) {
  const [showNotifications, setShowNotifications] = useState(false);
  const searchInputRef = useRef(null);
  const notificationRef = useRef(null);

  // Keyboard shortcut Ctrl+K / Cmd+K to focus search
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Close notifications on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (notificationRef.current && !notificationRef.current.contains(e.target)) {
        setShowNotifications(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && onSearchSubmit) {
      onSearchSubmit(searchQuery);
    }
  };

  return (
    <header className="topbar">
      <div className="breadcrumb">
        <span>Workspace</span>
        <span className="breadcrumb-separator">/</span>
        <strong>{activePage}</strong>
      </div>

      <div className="header-actions">
        <div className="search-box" onClick={() => searchInputRef.current?.focus()}>
          <Search size={16} />
          <input
            ref={searchInputRef}
            type="text"
            className="header-search-input"
            placeholder="Search findings (Ctrl+K)..."
            value={searchQuery || ""}
            onChange={(e) => onSearchChange(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <kbd><Command size={11} /> K</kbd>
        </div>

        <div style={{ position: "relative" }} ref={notificationRef}>
          <button
            className="icon-button"
            aria-label="Notifications"
            onClick={() => setShowNotifications(!showNotifications)}
            title="System notifications"
          >
            <Bell size={19} />
            {hasAuditData && <span className="notification-dot" />}
          </button>

          {showNotifications && (
            <div className="notification-popover">
              <div className="notification-header">
                <strong>Notifications</strong>
              </div>
              <div className="notification-body">
                {hasAuditData ? (
                  <div className="notification-item">
                    <CheckCircle2 size={16} style={{ color: "#22c55e", flexShrink: 0 }} />
                    <div>
                      <strong>Audit Completed</strong>
                      <p>Repository scan finished successfully. Review findings in the dashboard.</p>
                    </div>
                  </div>
                ) : (
                  <div className="notification-empty">
                    <ShieldAlert size={20} style={{ color: "#64748b", marginBottom: 6 }} />
                    <p>No new notifications. Run an audit to generate alerts.</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="profile">
          <div className="avatar">CS</div>
          <div className="profile-info">
            <strong>Security Analyst</strong>
            <span>Workspace Admin</span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
