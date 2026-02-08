import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import Loading from "../components/Loading";

const ERROR_MESSAGES = {
  unauthorized: "No estás autorizado para acceder a esta aplicación.",
  session_expired: "Tu sesión ha expirado. Por favor, inicia sesión nuevamente.",
  domain_not_allowed: "Por favor, usa tu correo institucional para iniciar sesión.",
};

export default function Login() {
  const [searchParams] = useSearchParams();
  const [errorMessage, setErrorMessage] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const error = searchParams.get("error");
    if (error) {
      setErrorMessage(ERROR_MESSAGES[error] || error);
    }
  }, [searchParams]);

  const handleLogin = () => {
    setLoading(true);
    window.location.href = `${import.meta.env.VITE_API_URL}/auth/login`;
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
          <div className="text-sm text-red-700 bg-red-100 border border-red-200 px-4 py-2 font-ancizar rounded">
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