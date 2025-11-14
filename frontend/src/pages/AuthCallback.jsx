import { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { saveTokensFromUrlParams } from "../services/authService";
import Loading from "../components/Loading";

export default function AuthCallback() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);

    const error = params.get("error");
    if (error) {
      navigate(`/login?error=${encodeURIComponent(error)}`);
      return;
    }

    const success = saveTokensFromUrlParams(params);
    if (!success) {
      navigate("/login?error=missing_access_token");
      return;
    }

    navigate("/dashboard");
  }, [location, navigate]);

  return <Loading message="Processing login..." />;
}