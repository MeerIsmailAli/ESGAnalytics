import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, clearSession } from "../api";

const SOURCE_TYPES = [
  { value: "sap", label: "SAP" },
  { value: "utility", label: "Utility" },
  { value: "travel", label: "Travel" },
];

export default function AnalysisPage() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "null");

  const [sources, setSources] = useState([]);
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [sourceForm, setSourceForm] = useState({
    name: "",
    source_type: "sap",
    client_name: "",
  });
  const [entryForm, setEntryForm] = useState({
    source: "",
    label: "",
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

  async function addSource(event) {
    event.preventDefault();
    await api.post("/sources", sourceForm);
    setSourceForm({ name: "", source_type: "sap", client_name: "" });
    await loadData();
  }

  async function addEntry(event) {
    event.preventDefault();
    await api.post("/entries", {
      source: Number(entryForm.source),
      label: entryForm.label,
    });
    setEntryForm({ source: "", label: "" });
    await loadData();
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

  return (
    <div className="container wide">
      <div className="header-row">
        <h1>Review dashboard</h1>
        <button onClick={logout}>Logout</button>
      </div>
      <p className="hint">
        Logged in as <strong>{user?.username}</strong> ({user?.role})
      </p>

      {error && <p className="error">{error}</p>}

      <section className="card">
        <h2>Add source</h2>
        <form className="inline-form" onSubmit={addSource}>
          <input
            placeholder="Source name"
            value={sourceForm.name}
            onChange={(e) => setSourceForm({ ...sourceForm, name: e.target.value })}
            required
          />
          <select
            value={sourceForm.source_type}
            onChange={(e) =>
              setSourceForm({ ...sourceForm, source_type: e.target.value })
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
            value={sourceForm.client_name}
            onChange={(e) =>
              setSourceForm({ ...sourceForm, client_name: e.target.value })
            }
          />
          <button type="submit">Add source</button>
        </form>
      </section>

      <section className="card">
        <h2>Add entry (manual row)</h2>
        <form className="inline-form" onSubmit={addEntry}>
          <select
            value={entryForm.source}
            onChange={(e) => setEntryForm({ ...entryForm, source: e.target.value })}
            required
          >
            <option value="">Pick source</option>
            {sources.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.source_type})
              </option>
            ))}
          </select>
          <input
            placeholder="Row label / description"
            value={entryForm.label}
            onChange={(e) => setEntryForm({ ...entryForm, label: e.target.value })}
            required
          />
          <button type="submit">Add entry</button>
        </form>
      </section>

      <section className="card">
        <h2>Sources ({sources.length})</h2>
        {sources.length === 0 ? (
          <p className="hint">No sources yet.</p>
        ) : (
          <ul className="compact-list">
            {sources.map((s) => (
              <li key={s.id}>
                <strong>{s.name}</strong> — {s.source_type} — {s.client_name || "—"} (
                {s.entry_count} entries) — added by {s.created_by_username || "—"}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="card">
        <h2>Entries ({entries.length})</h2>
        {loading ? (
          <p>Loading...</p>
        ) : entries.length === 0 ? (
          <p className="hint">No entries yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Label</th>
                <th>Source</th>
                <th>Client</th>
                <th>Status</th>
                <th>Created by</th>
                <th>Approved by</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <tr key={entry.id}>
                  <td>{entry.label}</td>
                  <td>
                    {entry.source_name} ({entry.source_type})
                  </td>
                  <td>{entry.client_name || "—"}</td>
                  <td>
                    <span className={`status status-${entry.status}`}>
                      {entry.status}
                    </span>
                  </td>
                  <td>{entry.created_by_username || "—"}</td>
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
        )}
      </section>
    </div>
  );
}
