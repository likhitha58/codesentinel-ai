
import { useState } from "react";
import { ScanSearch } from "lucide-react";

function AuditForm({ onAudit, loading }) {
  const [repository, setRepository] = useState("demo-repo");

  const handleSubmit = (event) => {
    event.preventDefault();

    const trimmedRepository = repository.trim();

    if (!trimmedRepository) return;

    onAudit(trimmedRepository);
  };

  return (
    <form className="audit-form" onSubmit={handleSubmit}>
      <div className="audit-form-heading">
        <ScanSearch size={20} />
        <div>
          <h3>Scan a repository</h3>
          <p>
            Enter a repository folder located inside the backend scan_targets
            directory.
          </p>
        </div>
      </div>

      <label htmlFor="repository-path">Repository name or relative path</label>

      <div className="audit-form-input-row">
        <input
          id="repository-path"
          type="text"
          value={repository}
          onChange={(event) => setRepository(event.target.value)}
          placeholder="e.g. demo-repo"
          disabled={loading}
          required
        />

        <button
          type="submit"
          disabled={loading || !repository.trim()}
        >
          <ScanSearch size={17} />
          {loading ? "Scanning..." : "Start audit"}
        </button>
      </div>

      <span className="audit-form-hint">
        Audits are performed in read-only mode.
      </span>
    </form>
  );
}

export default AuditForm;
