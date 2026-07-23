import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getUserInfo, isAuthenticated, redirectToLogin } from "../services/authService";
import ErrorPopup from "../components/ErrorPopup";
import {
  fetchResource,
  fetchDataSourceFileHistory,
  fetchFileWithAuth,
  updateDataSource,
  uploadResourceFile,
} from "../services/resourcesServices";
import { hasAdministratorRole } from "../services/dashboardUtils";

function formatDate(isoString) {
  if (!isoString) return "";
  try {
    return new Date(isoString).toLocaleString();
  } catch {
    return isoString;
  }
}

export default function EditDataSource() {
  const navigate = useNavigate();
  const { id } = useParams();
  const fileInputRef = useRef(null);
  const [hasAdminAccess, setHasAdminAccess] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({
    name: "",
    description: "",
  });
  const [versions, setVersions] = useState([]);
  const [file, setFile] = useState(null);
  const [selectedVersionFileId, setSelectedVersionFileId] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      redirectToLogin(navigate, `/data-sources/edit/${id}`);
      return;
    }

    const userInfo = getUserInfo();
    const isAdmin = hasAdministratorRole(userInfo);
    setHasAdminAccess(isAdmin);
    setAuthChecked(true);

    if (!isAdmin) {
      return;
    }

    const loadDataSource = async () => {
      try {
        setLoading(true);
        setError(null);

        const [dataSource, history] = await Promise.all([
          fetchResource("data-source", id),
          fetchDataSourceFileHistory(id),
        ]);

        setForm({
          name: dataSource.name || "",
          description: dataSource.description || "",
        });
        setVersions(history);
      } catch (err) {
        setError(err?.message || "No fue posible cargar la fuente de datos.");
      } finally {
        setLoading(false);
      }
    };

    loadDataSource();
  }, [navigate, id]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0] || null);
    setSelectedVersionFileId(null);
  };

  const handleSelectVersion = (fileId) => {
    setSelectedVersionFileId(fileId);
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleClearSelection = () => {
    setSelectedVersionFileId(null);
  };

  const handleDownloadVersion = async (version) => {
    try {
      const downloadUrl = `${import.meta.env.VITE_API_URL}/file/download/${version.file_id}`;
      const objectUrl = await fetchFileWithAuth(downloadUrl, {
        resource: "data_source",
        id,
        display: "false",
      });

      const link = document.createElement("a");
      link.href = objectUrl;
      link.setAttribute("download", version.filename || `version-${version.file_id}`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(objectUrl);
    } catch (err) {
      setMessage(err?.message || "No fue posible descargar esta versión.");
      setMessageType("error");
    }
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
      const payload = {
        name: form.name.trim(),
        description: form.description.trim(),
      };

      if (file) {
        setUploading(true);
        try {
          const uploadedFile = await uploadResourceFile(file);
          payload.file_id = uploadedFile.id;
        } finally {
          setUploading(false);
        }
      } else if (selectedVersionFileId != null) {
        payload.file_id = selectedVersionFileId;
      }

      await updateDataSource(Number(id), payload);

      const history = await fetchDataSourceFileHistory(id);
      setVersions(history);
      setFile(null);
      setSelectedVersionFileId(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      setMessage("Fuente de datos actualizada correctamente.");
      setMessageType("success");

      setTimeout(() => {
        navigate("/dashboard");
      }, 1000);
    } catch (err) {
      setMessage(err?.message || "No fue posible actualizar la fuente de datos.");
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
        <p className="text-lg text-gray-700">Cargando fuente de datos...</p>
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

  const busy = submitting || uploading;
  const currentVersion = versions.find((v) => v.is_current);
  const pendingLabel = file
    ? `Nuevo archivo: ${file.name}`
    : selectedVersionFileId != null
      ? `Se publicará: ${versions.find((v) => v.file_id === selectedVersionFileId)?.filename || `versión ${selectedVersionFileId}`}`
      : null;

  return (
    <div className="p-10 flex flex-col items-center">
      <div className="w-full max-w-2xl">
        {/* HEADER */}
        <div className="mb-8">
          <h1 className="text-3xl font-semibold text-gray-800">Editar fuente de datos</h1>
          <p className="text-sm text-gray-600 mt-1">Actualiza los datos de la fuente de datos.</p>
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
              disabled={busy}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-gray-700 placeholder-gray-400 focus:outline-none focus:border-secondary-cyan-strong focus:ring-1 focus:ring-secondary-cyan-strong disabled:bg-gray-100"
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
              disabled={busy}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-gray-700 placeholder-gray-400 focus:outline-none focus:border-secondary-cyan-strong focus:ring-1 focus:ring-secondary-cyan-strong disabled:bg-gray-100"
            />
          </div>

          {/* CURRENT VERSION */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Versión publicada actualmente
            </label>
            <p className="text-sm text-gray-600">
              {currentVersion
                ? currentVersion.filename || `Archivo #${currentVersion.file_id}`
                : "Sin archivo publicado"}
            </p>
          </div>

          {/* VERSION HISTORY */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Historial de versiones
            </label>
            {versions.length === 0 ? (
              <p className="text-sm text-gray-500">No hay versiones registradas todavía.</p>
            ) : (
              <ul className="border border-gray-200 rounded-lg divide-y divide-gray-200 max-h-64 overflow-y-auto">
                {versions.map((version) => {
                  const isSelected = selectedVersionFileId === version.file_id;
                  return (
                    <li
                      key={version.file_id}
                      className={`flex items-center justify-between gap-3 px-4 py-3 ${
                        isSelected ? "bg-secondary-cyan-strong/10" : ""
                      }`}
                    >
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-gray-800 truncate">
                          {version.filename || `Archivo #${version.file_id}`}
                          {version.is_current && (
                            <span className="ml-2 inline-block rounded-full bg-green-100 text-green-700 text-xs font-semibold px-2 py-0.5">
                              Actual
                            </span>
                          )}
                          {isSelected && !version.is_current && (
                            <span className="ml-2 inline-block rounded-full bg-secondary-cyan-strong/20 text-secondary-cyan-strong text-xs font-semibold px-2 py-0.5">
                              Seleccionada
                            </span>
                          )}
                        </p>
                        <p className="text-xs text-gray-500">
                          Publicada: {formatDate(version.published_at)}
                        </p>
                      </div>

                      <div className="flex items-center gap-2 flex-shrink-0">
                        <button
                          type="button"
                          onClick={() => handleDownloadVersion(version)}
                          disabled={busy}
                          className="text-xs border border-gray-300 text-gray-700 px-3 py-1.5 rounded-lg hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Descargar
                        </button>
                        {!version.is_current && (
                          <button
                            type="button"
                            onClick={() => handleSelectVersion(version.file_id)}
                            disabled={busy}
                            className="text-xs bg-secondary-cyan-strong text-white px-3 py-1.5 rounded-lg hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            Publicar esta versión
                          </button>
                        )}
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          {/* NEW FILE */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Subir nueva versión (opcional)
            </label>
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileChange}
              disabled={busy}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-gray-700 focus:outline-none focus:border-secondary-cyan-strong focus:ring-1 focus:ring-secondary-cyan-strong disabled:bg-gray-100"
            />
            {pendingLabel && (
              <div className="mt-2 flex items-center justify-between gap-3">
                <p className="text-sm text-gray-600">{pendingLabel}</p>
                {selectedVersionFileId != null && (
                  <button
                    type="button"
                    onClick={handleClearSelection}
                    disabled={busy}
                    className="text-xs text-gray-500 underline hover:text-gray-700 disabled:opacity-50"
                  >
                    Cancelar selección
                  </button>
                )}
              </div>
            )}
          </div>

          {/* BUTTONS */}
          <div className="flex items-center gap-4">
            <button
              type="submit"
              disabled={busy || !form.name.trim()}
              className="bg-secondary-cyan-strong text-white px-6 py-2 rounded-lg text-sm font-semibold hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading && "Cargando archivo..."}
              {submitting && !uploading && "Actualizando..."}
              {!busy && "Actualizar fuente de datos"}
            </button>
            <button
              type="button"
              onClick={() => navigate("/dashboard")}
              disabled={busy}
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
