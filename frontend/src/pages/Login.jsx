import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import Loading from "../components/Loading";

const ERROR_MESSAGES = {
  unauthorized: "No estás autorizado para acceder a esta aplicación.",
  session_expired: "Tu sesión ha expirado. Por favor, inicia sesión nuevamente.",
  domain_not_allowed: "Por favor, usa tu correo institucional para iniciar sesión."
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
    <div className="min-h-screen flex flex-col items-center justify-center gap-6 p-4">

      <h1 className="text-4xl font-bold">Iniciar Sesión</h1>
      {errorMessage && (
        <div className="text-red-600 bg-red-100 px-4 py-2 rounded">
          {errorMessage}
        </div>
      )}


      <button
        onClick={handleLogin}
        className="flex items-center gap-3 px-6 py-3 rounded-lg border border-gray-300 hover:bg-gray-100 transition"
      >
        <img
          src="https://developers.google.com/identity/images/g-logo.png"
          alt="Google logo"
          className="w-6 h-6"
        />
        <span className="font-medium text-gray-700">Iniciar sesión con Google</span>
      </button>
    </div>
  );
}