import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getUserInfo, isAuthenticated, redirectToLogin } from "../services/authService";
import ErrorPopup from "../components/ErrorPopup";
import { fetchRoleManagementData, updateRole } from "../services/resourcesServices";
import { hasAdministratorRole } from "../services/dashboardUtils";

export default function EditRole() {
  const navigate = useNavigate();
  const { roleId } = useParams();
  const [hasAdminAccess, setHasAdminAccess] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({
    name: "",
    description: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      redirectToLogin(navigate, `/edit-role/${roleId}`);
      return;
    }

    const userInfo = getUserInfo();
    const isAdmin = hasAdministratorRole(userInfo);
    setHasAdminAccess(isAdmin);
    setAuthChecked(true);

    if (!isAdmin) {
      return;
    }

    const loadRole = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchRoleManagementData({ excludeAdmin: false });
        const roles = Array.isArray(data?.roles) ? data.roles : [];
        const role = roles.find((item) => Number(item.id) === Number(roleId));

        if (!role) {
          setError("No se encontró el rol.");
          return;
        }

        setForm({
          name: role.name || "",
          description: role.description || "",
        });
      } catch (err) {
        setError(err?.message || "No fue posible cargar el rol.");
      } finally {
        setLoading(false);
      }
    };

    loadRole();
  }, [navigate, roleId]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setMessageType("");
    setSubmitting(true);

    try {
      await updateRole(Number(roleId), {
        name: form.name.trim(),
        description: form.description.trim(),
      });

      setMessage("Rol actualizado correctamente.");
      setMessageType("success");

      setTimeout(() => {
        navigate("/dashboard");
      }, 1000);
    } catch (err) {
      setMessage(err?.message || "No fue posible actualizar el rol.");
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

  if (loading) {
    return (
      <div className="p-10 flex items-center justify-center">
        <p className="text-lg text-gray-700">Cargando rol...</p>
      </div>
    );
  }

  if (error) {
    return (
      <ErrorPopup
        error={error}
        onClose={() => navigate("/dashboard")}
      />
    );
  }

  return (
    <div className="p-10 flex flex-col items-center">
      <div className="w-full max-w-2xl">
        <div className="mb-8">
          <h1 className="text-3xl font-semibold text-gray-800">Editar rol</h1>
          <p className="text-sm text-gray-600 mt-1">Actualiza los datos del rol.</p>
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
              value={form.name}
              onChange={handleInputChange}
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
              value={form.description}
              onChange={handleInputChange}
              placeholder="Describe brevemente este rol..."
              rows="4"
              disabled={submitting}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-gray-700 placeholder-gray-400 focus:outline-none focus:border-primary-cyan-strong focus:ring-1 focus:ring-primary-cyan-strong disabled:bg-gray-100"
            />
          </div>

          <div className="flex items-center gap-4">
            <button
              type="submit"
              disabled={submitting || !form.name.trim()}
              className="bg-primary-cyan-strong text-white px-6 py-2 rounded-lg text-sm font-semibold hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? "Actualizando..." : "Actualizar rol"}
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
