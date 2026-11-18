
const API_BASE_URL = "/api";

export async function auditRepository(repository) {
  const response = await fetch(`${API_BASE_URL}/audit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ repository }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || `Audit failed with status ${response.status}`
    );
  }

  return data;
}

export async function checkHealth() {
  try {
    const response = await fetch("/health");
    if (!response.ok) return { status: "unreachable" };
    return await response.json();
  } catch {
    return { status: "unreachable" };
  }
}

export async function exportJsonReport(repository) {
  const response = await fetch(`${API_BASE_URL}/audit/export/json`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ repository }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(
      errorData?.detail || `Export failed with status ${response.status}`
    );
  }

  const blob = await response.blob();
  const disposition = response.headers.get("content-disposition") || "";
  const filenameMatch = disposition.match(/filename="?([^"]+)"?/);
  const filename = filenameMatch ? filenameMatch[1] : "audit_report.json";

  return { blob, filename };
}

export async function exportMarkdownReport(repository) {
  const response = await fetch(`${API_BASE_URL}/audit/export/markdown`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ repository }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(
      errorData?.detail || `Export failed with status ${response.status}`
    );
  }

  const blob = await response.blob();
  const disposition = response.headers.get("content-disposition") || "";
  const filenameMatch = disposition.match(/filename="?([^"]+)"?/);
  const filename = filenameMatch ? filenameMatch[1] : "audit_report.md";

  return { blob, filename };
}

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
