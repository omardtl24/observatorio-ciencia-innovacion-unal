import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

const ERROR_MESSAGES = {
  unauthorized: "You are not authorized to access this application.",
  session_expired: "Your session has expired. Please log in again.",
  domain_not_allowed: "Please use your institutional email to login."
};

export default function Login() {
  const [searchParams] = useSearchParams();
  const [errorMessage, setErrorMessage] = useState(null);

  useEffect(() => {
    const error = searchParams.get("error");
    if (error) {
      // Map the backend error code to a user-friendly message
      setErrorMessage(ERROR_MESSAGES[error] || error);
    }
  }, [searchParams]);

  return (
    <div className="login-page">
      <h1>Login</h1>

      {errorMessage && (
        <div style={{ color: "red", marginBottom: "1rem" }}>
          {errorMessage}
        </div>
      )}

      <a href={`${import.meta.env.VITE_API_URL}/auth/login`}>
        <button>Login with Google</button>
      </a>
    </div>
  );
}
