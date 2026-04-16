import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getUserInfo, isAuthenticated, redirectToLogin } from "../services/authService";
import ErrorPopup from "../components/ErrorPopup";
import { createDataSource, uploadResourceFile } from "../services/resourcesServices";
import { hasAdministratorRole } from "../services/dashboardUtils";

export default function CreateDataSource() {
  const navigate = useNavigate();
  const [hasAdminAccess, setHasAdminAccess] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);
  const [form, setForm] = useState({
    name: "",
    description: "",
    file_id: null,
  });
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");

  useEffect(() => {
    if (!isAuthenticated()) {
      redirectToLogin(navigate, "/data-sources/create");
      return;
    }

    const userInfo = getUserInfo();
    const isAdmin = hasAdministratorRole(userInfo);
    setHasAdminAccess(isAdmin);
    setAuthChecked(true);
  }, [navigate]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0] || null);
  };

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
      let payload = {
        name: form.name.trim(),
        description: form.description.trim(),
      };

      // Upload file if provided
      if (file) {
        setUploading(true);
        try {
          const uploadedFile = await uploadResourceFile(file);
          payload.file_id = uploadedFile.id;
        } finally {
          setUploading(false);
        }
      }

      // Create data source
      const createdDataSource = await createDataSource(payload);
      setMessage("Fuente de datos creada correctamente.");
      setMessageType("success");

      // Redirect to data sources page after 1 second
      setTimeout(() => {
        navigate("/data-sources");
      }, 1000);
    } catch (err) {
      setMessage(err?.message || "No fue posible crear la fuente de datos.");
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
        {/* HEADER */}
        <div className="mb-8">
          <h1 className="text-3xl font-semibold text-gray-800">Crear fuente de datos</h1>
          <p className="text-sm text-gray-600 mt-1">Completa el formulario para crear una nueva fuente de datos.</p>
        </div>

        {/* MESSAGE */}
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

        {/* FORM */}
        <form onSubmit={handleSubmit} className="bg-white shadow-md rounded-xl border border-gray-200 p-6 space-y-6">
          {/* NAME */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nombre <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              name="name"
              value={form.name}
              onChange={handleInputChange}
              placeholder="Ej: Base de datos COVID-19"
              required
              disabled={submitting || uploading}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-gray-700 placeholder-gray-400 focus:outline-none focus:border-primary-cyan-strong focus:ring-1 focus:ring-primary-cyan-strong disabled:bg-gray-100"
            />
          </div>

          {/* DESCRIPTION */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Descripción
            </label>
            <textarea
              name="description"
              value={form.description}
              onChange={handleInputChange}
              placeholder="Describe brevemente esta fuente de datos..."
              rows="4"
              disabled={submitting || uploading}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-gray-700 placeholder-gray-400 focus:outline-none focus:border-primary-cyan-strong focus:ring-1 focus:ring-primary-cyan-strong disabled:bg-gray-100"
            />
          </div>

          {/* FILE */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Archivo (opcional)
            </label>
            <input
              type="file"
              onChange={handleFileChange}
              disabled={submitting || uploading}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-gray-700 focus:outline-none focus:border-primary-cyan-strong focus:ring-1 focus:ring-primary-cyan-strong disabled:bg-gray-100"
            />
            {file && (
              <p className="text-sm text-gray-600 mt-2">
                Archivo seleccionado: <strong>{file.name}</strong>
              </p>
            )}
          </div>

          {/* BUTTONS */}
          <div className="flex items-center gap-4">
            <button
              type="submit"
              disabled={submitting || uploading || !form.name.trim()}
              className="bg-primary-blue-strong text-white px-6 py-2 rounded-lg text-sm font-semibold hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading && "Cargando archivo..."}
              {submitting && !uploading && "Creando..."}
              {!submitting && !uploading && "Crear fuente de datos"}
            </button>
            <button
              type="button"
              onClick={() => navigate("/data-sources")}
              disabled={submitting || uploading}
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
