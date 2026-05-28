import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, clearSession } from "../api";

const SOURCE_TYPES = [
  { value: "sap", label: "SAP (semicolon CSV)" },
  { value: "utility", label: "Utility (CSV)" },
  { value: "travel", label: "Travel (JSON)" },
];

export default function AnalysisPage() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "null");

  const [sources, setSources] = useState([]);
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [uploadMsg, setUploadMsg] = useState("");

  const [uploadForm, setUploadForm] = useState({
    source_type: "sap",
    client_name: "Acme Corp",
    name: "",
    file: null,
  });

  async function loadData() {
    setError("");
    try {
      const [sourcesRes, entriesRes] = await Promise.all([
        api.get("/sources"),
        api.get("/entries"),
      ]);
      setSources(sourcesRes.data);
      setEntries(entriesRes.data);
    } catch (requestError) {
      if (requestError.response?.status === 401) {
        clearSession();
        navigate("/login");
        return;
      }
      setError("Failed to load data");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, [navigate]);

  async function handleUpload(event) {
    event.preventDefault();
    if (!uploadForm.file) {
      setUploadMsg("Pick a file first");
      return;
    }
    setUploadMsg("Uploading...");
    const body = new FormData();
    body.append("source_type", uploadForm.source_type);
    body.append("client_name", uploadForm.client_name);
    if (uploadForm.name) body.append("name", uploadForm.name);
    body.append("file", uploadForm.file);

    try {
      // Do NOT set Content-Type — browser must add multipart boundary
      const res = await api.post("/sources/upload", body);
      setUploadMsg(`Imported ${res.data.created} entries (${res.data.errors?.length || 0} parse warnings)`);
      setUploadForm({ ...uploadForm, file: null, name: "" });
      event.target.reset();
      await loadData();
    } catch (requestError) {
      const data = requestError.response?.data;
      const msg =
        data?.detail ||
        (typeof data === "object" ? JSON.stringify(data) : null) ||
        requestError.message ||
        "Upload failed";
      setUploadMsg(msg);
      console.error("Upload error:", data || requestError);
    }
  }

  async function updateStatus(entryId, status) {
    await api.patch(`/entries/${entryId}`, { status });
    await loadData();
  }

  async function deleteEntry(entryId) {
    if (!window.confirm("Delete this entry?")) return;
    await api.delete(`/entries/${entryId}`);
    await loadData();
  }

  function logout() {
    clearSession();
    navigate("/login");
  }

  const suspiciousCount = entries.filter((e) => e.is_suspicious).length;

  return (
    <div className="container wide">
      <div className="header-row">
        <h1>Review dashboard</h1>
        <button onClick={logout}>Logout</button>
      </div>
      <p className="hint">
        Logged in as <strong>{user?.username}</strong> — {entries.length} entries,{" "}
        {suspiciousCount} suspicious
      </p>

      {error && <p className="error">{error}</p>}

      <section className="card">
        <h2>Ingest data (upload)</h2>
        <form className="inline-form" onSubmit={handleUpload}>
          <select
            value={uploadForm.source_type}
            onChange={(e) =>
              setUploadForm({ ...uploadForm, source_type: e.target.value })
            }
          >
            {SOURCE_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
          <input
            placeholder="Client name"
            value={uploadForm.client_name}
            onChange={(e) =>
              setUploadForm({ ...uploadForm, client_name: e.target.value })
            }
            required
          />
          <input
            placeholder="Batch name (optional)"
            value={uploadForm.name}
            onChange={(e) => setUploadForm({ ...uploadForm, name: e.target.value })}
          />
          <input
            type="file"
            accept=".csv,.txt,.json"
            onChange={(e) =>
              setUploadForm({ ...uploadForm, file: e.target.files?.[0] || null })
            }
            required
          />
          <button type="submit">Upload & ingest</button>
        </form>
        {uploadMsg && <p className="hint">{uploadMsg}</p>}
        <p className="hint">
          Samples in repo: <code>backend/sample_files/</code>
        </p>
      </section>

      <section className="card">
        <h2>Sources ({sources.length})</h2>
        {sources.length === 0 ? (
          <p className="hint">No sources yet — upload a file or run seed_demo on deploy.</p>
        ) : (
          <ul className="compact-list">
            {sources.map((s) => (
              <li key={s.id}>
                <strong>{s.name}</strong> — {s.source_type} — {s.client_name || "—"} —{" "}
                {s.entry_count} entries — {s.filename || "manual"}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="card">
        <h2>Entries</h2>
        {loading ? (
          <p>Loading...</p>
        ) : entries.length === 0 ? (
          <p className="hint">No entries yet.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Label</th>
                  <th>Client</th>
                  <th>Scope</th>
                  <th>Activity</th>
                  <th>Qty</th>
                  <th>CO2e (kg)</th>
                  <th>Status</th>
                  <th>Flagged by</th>
                  <th>Approved by</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((entry) => (
                  <tr
                    key={entry.id}
                    className={entry.is_suspicious ? "row-suspicious" : ""}
                  >
                    <td>
                      {entry.label}
                      {entry.is_suspicious && (
                        <div className="warn">{entry.suspicion_reason}</div>
                      )}
                    </td>
                    <td>{entry.client_name || "—"}</td>
                    <td>{entry.scope}</td>
                    <td>{entry.activity_type}</td>
                    <td>
                      {entry.normalized_quantity} {entry.normalized_unit}
                    </td>
                    <td>{entry.emissions_kg_co2e ?? "—"}</td>
                    <td>
                      <span className={`status status-${entry.status}`}>
                        {entry.status}
                      </span>
                    </td>
                    <td>{entry.flagged_by_username || "—"}</td>
                    <td>{entry.approved_by_username || "—"}</td>
                    <td className="actions">
                      {entry.status !== "flagged" && (
                        <button onClick={() => updateStatus(entry.id, "flagged")}>
                          Flag
                        </button>
                      )}
                      {entry.status !== "approved" && (
                        <button onClick={() => updateStatus(entry.id, "approved")}>
                          Approve
                        </button>
                      )}
                      <button className="danger" onClick={() => deleteEntry(entry.id)}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
