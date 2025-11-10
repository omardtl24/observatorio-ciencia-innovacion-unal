import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import AuthCallback from "./pages/AuthCallback";
import Dashboard from "./pages/Dashboard";

function isTokenValid() {
  const token = localStorage.getItem("access_token");
  if (!token) return false;

  try {
    const payload = JSON.parse(atob(token.split(".")[1])); // decode JWT payload
    const exp = payload.exp * 1000;
    return Date.now() < exp;
  } catch {
    return false;
  }
}

function ProtectedRoute({ children }) {
  if (!isTokenValid()) {
    localStorage.clear();
    return <Navigate to="/login?error=session_expired" replace />;
  }

  return children;
}

export default function App() {
  return (
    <Router>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<Login />} />
        <Route path="/auth/callback" element={<AuthCallback />} />

        {/* Protected */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Catch all → redirect */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}