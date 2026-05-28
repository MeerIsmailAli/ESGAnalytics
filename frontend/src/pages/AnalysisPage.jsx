import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, clearSession } from "../api";

export default function AnalysisPage() {
  const navigate = useNavigate();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const user = JSON.parse(localStorage.getItem("user") || "null");

  useEffect(() => {
    async function loadRecords() {
      try {
        const response = await api.get("/analysis");
        setRecords(response.data.results || []);
      } catch (error) {
        if (error.response?.status === 401) {
          clearSession();
          navigate("/login");
          return;
        }
      } finally {
        setLoading(false);
      }
    }

    loadRecords();
  }, [navigate]);

  function logout() {
    clearSession();
    navigate("/login");
  }

  return (
    <div className="container">
      <div className="header-row">
        <h1>Analysis</h1>
        <button onClick={logout}>Logout</button>
      </div>
      <p className="hint">
        Logged in as <strong>{user?.username}</strong> | Tenant:{" "}
        <strong>{user?.tenant?.name || "-"}</strong>
      </p>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="card">
          {records.length === 0 ? (
            <p>No records found for your tenant.</p>
          ) : (
            <ul>
              {records.map((record) => (
                <li key={record.id}>
                  <strong>{record.title}</strong> - {record.status}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
