import { Navigate, Route, Routes } from "react-router-dom";
import { getStoredToken, setAuthToken } from "./api";
import ProtectedRoute from "./components/ProtectedRoute";
import AnalysisPage from "./pages/AnalysisPage";
import LoginPage from "./pages/LoginPage";

const token = getStoredToken();
if (token) {
  setAuthToken(token);
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/analysis"
        element={
          <ProtectedRoute>
            <AnalysisPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/analysis" replace />} />
    </Routes>
  );
}
