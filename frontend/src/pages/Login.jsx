import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Loading from "../components/Loading";
import ErrorPopup from "../components/ErrorPopup";
import { startLogin, saveTokensFromPayload } from "../services/authService";
import { capitalize } from '../services/stringServices'

const ERROR_MESSAGES = {
  session_expired: "Tu sesión ha expirado. Por favor, inicia sesión nuevamente.",
};

const RESOURCE_LABELS = {
  report: "reportes",
  document: "documentos y presentaciones",
  simulator: "simuladores",
  visor: "visores",
};

export default function Login() {
  const location = useLocation();
  const navigate = useNavigate();
  const [errorMessage, setErrorMessage] = useState(null);
  const [loading, setLoading] = useState(false);
  const contactEmail = import.meta.env.VITE_SUPPORT_EMAIL || "info@universidad.edu.co";
  const loginParams = new URLSearchParams(location.search);
  const resourceType = loginParams.get("resourceType");
  const resourceLabel = RESOURCE_LABELS[resourceType] || "visores";

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
    <div className="min-h-screen flex flex-col items-center justify-center px-4 gap-6">
      {resourceType ? (
          <div className="w-full max-w-sm text-center space-y-2">
          <h1 className="text-3xl font-bold font-serif italic text-primary-blue-strong">
            ¡{capitalize(resourceLabel)} detallados a tu alcance!
          </h1>
          <p className="text-md text-primary-blue-strong">
            Accede a los {resourceLabel} generados por el Observatorio de la Facultad de Ciencias
          </p>
        </div>
      ) : null}

      <div className="w-full max-w-sm bg-secondary-gray-soft rounded-xl shadow-lg border border-primary-blue-strong p-8 space-y-6">

        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl md:text-4xl font-bold font-serif italic text-primary-blue-strong">
            Inicia sesión
          </h1>
          <p className="text-md text-primary-blue-strong font-bold font-serif italic pt-3">
            ¿Aún no tienes acceso? <a href={`mailto:${contactEmail}`} className="text-secondary-cyan-strong underline">
             Escríbenos
            </a>
          </p>
        </div>

        {/* Google login */}
        <button
          onClick={handleLogin}
          className="
            w-auto mx-auto flex items-center justify-center gap-3
            px-4 py-3 rounded-md
            border border-secondary-cyan-strong
            text-black font-serif italic
            font-bold
            bg-white
            hover:bg-secondary-cyan-soft
            transition
          "
        >
          <img
            src="https://developers.google.com/identity/images/g-logo.png"
            alt="Google logo"
            className="w-5 h-5"
          />
          Continuar con Google
        </button>

        {/* Footer */}
        <p className="text-xs text-center text-gray-500">
          Al ingresar, aceptas nuestros Términos de Uso y reconoces haber leído nuestra Política de Privacidad 
        </p>
      </div>

      <ErrorPopup
        error={errorMessage}
        onClose={() => setErrorMessage(null)}
      />
    </div>
  );
}