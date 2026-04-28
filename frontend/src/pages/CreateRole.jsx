import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getUserInfo, isAuthenticated, redirectToLogin } from "../services/authService";
import ErrorPopup from "../components/ErrorPopup";
import { createRole } from "../services/resourcesServices";
import { hasAdministratorRole } from "../services/dashboardUtils";

export default function CreateRole() {
  const navigate = useNavigate();
  const [hasAdminAccess, setHasAdminAccess] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");

  useEffect(() => {
    if (!isAuthenticated()) {
      redirectToLogin(navigate, "/create-role");
      return;
    }

    const userInfo = getUserInfo();
    const isAdmin = hasAdministratorRole(userInfo);
    setHasAdminAccess(isAdmin);
    setAuthChecked(true);
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setMessageType("");
    setSubmitting(true);

    try {
      await createRole({
        name: name.trim(),
        description: description.trim(),
      });
      setMessage("Rol creado correctamente.");
      setMessageType("success");

      setTimeout(() => {
        navigate("/dashboard");
      }, 1000);
    } catch (err) {
      setMessage(err?.message || "No fue posible crear el rol.");
      setMessageType("error");
    } finally {
      setSubmitting(false);
    }
  };

  if (!authChecked) {
    return (
      <div className="p-10 flex items-center justify-center">
        <p className="text-lg text-gray-700">Verificando sesión...</p>
      </div>
    );
  }

  if (!hasAdminAccess) {
    return (
      <ErrorPopup
        error="Tu cuenta no tiene permisos de Administrador para acceder a este panel."
        onClose={() => navigate("/dashboard")}
      />
    );
  }

  return (
    <div className="p-10 flex flex-col items-center">
      <div className="w-full max-w-2xl">
        <div className="mb-8">
          <h1 className="text-3xl font-semibold text-gray-800">Crear rol</h1>
          <p className="text-sm text-gray-600 mt-1">Completa el formulario para crear un nuevo rol.</p>
        </div>

        {message && (
          <div
            className={`mb-6 rounded-lg border px-4 py-3 text-sm flex items-start justify-between gap-3 ${
              messageType === "error"
                ? "border-red-200 bg-red-50 text-red-700"
                : "border-green-200 bg-green-50 text-green-700"
            }`}
          >
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-white shadow-md rounded-xl border border-gray-200 p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nombre <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              name="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ej: Investigador"
              required
              disabled={submitting}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-gray-700 placeholder-gray-400 focus:outline-none focus:border-primary-cyan-strong focus:ring-1 focus:ring-primary-cyan-strong disabled:bg-gray-100"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Descripción
            </label>
            <textarea
              name="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe brevemente este rol..."
              rows="4"
              disabled={submitting}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-gray-700 placeholder-gray-400 focus:outline-none focus:border-primary-cyan-strong focus:ring-1 focus:ring-primary-cyan-strong disabled:bg-gray-100"
            />
          </div>

          <div className="flex items-center gap-4">
            <button
              type="submit"
              disabled={submitting || !name.trim()}
              className="bg-primary-blue-strong text-white px-6 py-2 rounded-lg text-sm font-semibold hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? "Creando..." : "Crear rol"}
            </button>
            <button
              type="button"
              onClick={() => navigate("/dashboard")}
              disabled={submitting}
              className="border border-gray-300 text-gray-700 px-6 py-2 rounded-lg text-sm font-semibold hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}