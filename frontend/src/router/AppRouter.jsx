import { Routes, Route } from "react-router-dom";
import Layout from "../layout/Layout";
import Landing from "../pages/Landing";
import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard";
import AuthCallback from "../pages/AuthCallback";
import Visors from "../pages/Visors";

export default function AppRouter() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="/visors" element={<Visors />} />
      </Route>
    </Routes>
  );
}