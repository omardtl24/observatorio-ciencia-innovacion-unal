import { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

export default function AuthCallback() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);

    // If backend returned an error, redirect to login with it
    const error = params.get("error");
    if (error) {
      navigate(`/login?error=${encodeURIComponent(error)}`);
      return;
    }

    // Save all params to localStorage
    for (const [key, value] of params.entries()) {
      localStorage.setItem(key, value);
    }

    // Check access_token exists
    if (!params.get("access_token")) {
      navigate("/login?error=missing_access_token");
      return;
    }

    navigate("/dashboard");
  }, [location, navigate]);

  return <p>Processing login...</p>;
}