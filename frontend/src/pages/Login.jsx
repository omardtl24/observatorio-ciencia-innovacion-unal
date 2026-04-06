import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Loading from "../components/Loading";
import { startLogin, saveTokensFromPayload } from "../services/authService";

const ERROR_MESSAGES = {
  session_expired: "Tu sesión ha expirado. Por favor, inicia sesión nuevamente.",
};

export default function Login() {
  const location = useLocation();
  const navigate = useNavigate();
  const [errorMessage, setErrorMessage] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(location.search);

    // Handle callback from Auth0/backend
    if (params.has("access_token")) {
      const payload = Object.fromEntries(params);
      const success = saveTokensFromPayload(payload);
      if (success) {
        navigate("/dashboard");
        return;
      }
    }

    // Handle error from callback
    if (params.has("error_code")) {
      const errorCode = params.get("error_code");
      const message = params.get("message");
      setErrorMessage(message || `Error: ${errorCode}`);
      return;
    }

    // Handle session expired
    const error = params.get("error");
    if (error === "session_expired") {
      setErrorMessage(ERROR_MESSAGES.session_expired);
    }
  }, [location, navigate]);

  const handleLogin = async () => {
    setLoading(true);
    setErrorMessage(null);
    
    // Get the origin from query params, default to "/"
    const params = new URLSearchParams(location.search);
    const origin = params.get("origin") || "/";
    
    try {
      await startLogin(origin);
    } catch (error) {
      if (error.message.includes("closed by user")) {
        setErrorMessage("La ventana de autenticacion fue cerrada. Intenta nuevamente.");
      } else {
        setErrorMessage(error.message || "No fue posible completar el inicio de sesion.");
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Loading message="Redirigiendo a Google..." />;

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-lg border border-blue-200 p-8 space-y-6">

        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-semibold text-primary-cyan-strong">
            ¡Interactúa con nuestros visores!
          </h1>
          <p className="text-sm text-gray-600">
            Los visores son una herramienta esencial para investigadores,
            estudiantes y personal administrativo.
          </p>
        </div>

        {/* Section title */}
        <div className="flex items-center gap-2 text-blue-600 font-medium">
          <span className="inline-block w-2 h-2 rounded-full bg-blue-500" />
          Producción científica
        </div>

        {/* Error */}
        {errorMessage && (
          <div className="text-sm text-red-700 bg-red-100 border border-red-200 px-4 py-2 font-sans rounded">
            {errorMessage}
          </div>
        )}

        {/* Google login */}
        <button
          onClick={handleLogin}
          className="
            w-full flex items-center justify-center gap-3
            px-4 py-3 rounded-md
            border border-blue-300
            text-blue-700 font-medium
            hover:bg-blue-50
            transition
          "
        >
          <img
            src="https://developers.google.com/identity/images/g-logo.png"
            alt="Google logo"
            className="w-5 h-5"
          />
          Iniciar sesión con Google
        </button>

        {/* Footer */}
        <p className="text-xs text-center text-gray-500">
          Al continuar, aceptas los términos y condiciones.
        </p>
      </div>
    </div>
  );
}