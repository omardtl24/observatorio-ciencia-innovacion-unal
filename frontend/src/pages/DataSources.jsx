import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getUserInfo, isAuthenticated, redirectToLogin } from "../services/authService";
import ErrorPopup from "../components/ErrorPopup";
import {
  fetchDataSources,
  deleteDataSource,
} from "../services/resourcesServices";
import { hasAdministratorRole } from "../services/dashboardUtils";
import { formatDate, getItemLastUpdate } from "../services/dashboardUtils";
import { parseColor } from "../services/stringServices.jsx";

export default function DataSources() {
  const navigate = useNavigate();
  const [hasAdminAccess, setHasAdminAccess] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);
  const [dataSources, setDataSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionMessage, setActionMessage] = useState("");
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      redirectToLogin(navigate, "/data-sources");
      return;
    }

    const userInfo = getUserInfo();
    const isAdmin = hasAdministratorRole(userInfo);
    setHasAdminAccess(isAdmin);
    setAuthChecked(true);

    if (!isAdmin) {
      return;
    }

    const loadDataSources = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchDataSources();
        setDataSources(Array.isArray(data) ? data : []);
      } catch (err) {
        setError(err?.message || "No fue posible cargar las fuentes de datos");
        setDataSources([]);
      } finally {
        setLoading(false);
      }
    };

    loadDataSources();
  }, [navigate]);

  const handleDelete = async (dataSourceId) => {
    const confirmed = window.confirm("¿Seguro que deseas eliminar esta fuente de datos?");
    if (!confirmed) {
      return;
    }

    setDeletingId(dataSourceId);
    setActionMessage("");

    try {
      await deleteDataSource(dataSourceId);
      setDataSources((prev) => prev.filter((ds) => ds.id !== dataSourceId));
      setActionMessage("Fuente de datos eliminada correctamente.");
    } catch (err) {
      setActionMessage(err?.message || "No fue posible eliminar la fuente de datos.");
    } finally {
      setDeletingId(null);
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
      <div className="w-full max-w-5xl">
        {/* HEADER */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-semibold text-gray-800">Fuentes de Datos</h1>
            <p className="text-sm text-gray-600 mt-1">Crea, edita y gestiona todas tus fuentes de datos.</p>
          </div>
          <button
            onClick={() => navigate("/data-sources/create")}
            className="bg-primary-cyan-strong text-white px-4 py-2 rounded-lg text-sm font-semibold hover:opacity-90 transition"
          >
            Crear fuente de datos
          </button>
        </div>

        {/* ACTION MESSAGE */}
        {actionMessage && (
          <div className="mb-4 rounded-lg border border-blue-200 bg-blue-50 text-blue-700 px-4 py-3 text-sm">
            {actionMessage}
          </div>
        )}

        {/* ERROR MESSAGE */}
        {error && (
          <div className="mb-4 rounded-lg border border-red-200 bg-red-50 text-red-700 px-4 py-3 text-sm">
            {error}
          </div>
        )}

        {/* TABLE */}
        <div className="bg-white shadow-md rounded-xl border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-gray-50 text-gray-700 uppercase tracking-wide text-xs">
                <tr>
                  <th className="px-6 py-3">Nombre</th>
                  <th className="px-6 py-3">Descripción</th>
                  <th className="px-6 py-3">Actualizado en</th>
                  <th className="px-6 py-3">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr className="border-t border-gray-100">
                    <td className="px-6 py-4 text-gray-500" colSpan={4}>
                      Cargando fuentes de datos...
                    </td>
                  </tr>
                )}

                {!loading && dataSources.length === 0 && (
                  <tr className="border-t border-gray-100">
                    <td className="px-6 py-4 text-gray-500" colSpan={4}>
                      No hay fuentes de datos disponibles.
                    </td>
                  </tr>
                )}

                {!loading &&
                  dataSources.map((dataSource) => (
                    <tr key={dataSource.id} className="border-t border-gray-100 hover:bg-gray-50">
                      <td className="px-6 py-3 text-gray-900 font-medium">
                        {dataSource.name ? parseColor(dataSource.name, "font-bold") : "Sin nombre"}
                      </td>
                      <td className="px-6 py-3 text-gray-700">
                        {dataSource.description ? (
                          parseColor(dataSource.description, "text-sm")
                        ) : (
                          <span className="text-gray-400">Sin descripción</span>
                        )}
                      </td>
                      <td className="px-6 py-3 text-gray-700">
                        {formatDate(getItemLastUpdate(dataSource))}
                      </td>
                      <td className="px-6 py-3">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => navigate(`/data-sources/edit/${dataSource.id}`)}
                            className="inline-flex items-center justify-center rounded-lg border border-primary-blue text-primary-blue hover:bg-blue-50 px-2 py-1 transition"
                            title="Editar fuente de datos"
                            aria-label="Editar fuente de datos"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2"
                              className="w-4 h-4"
                            >
                              <path strokeLinecap="round" strokeLinejoin="round" d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                              <path strokeLinecap="round" strokeLinejoin="round" d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                            </svg>
                          </button>
                          <button
                            onClick={() => handleDelete(dataSource.id)}
                            disabled={deletingId === dataSource.id}
                            className="inline-flex items-center justify-center rounded-lg border border-red-300 text-red-600 hover:bg-red-50 px-2 py-1 transition disabled:opacity-50 disabled:cursor-not-allowed"
                            title="Eliminar fuente de datos"
                            aria-label="Eliminar fuente de datos"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2"
                              className="w-4 h-4"
                            >
                              <path strokeLinecap="round" strokeLinejoin="round" d="M3 6h18" />
                              <path strokeLinecap="round" strokeLinejoin="round" d="M8 6V4h8v2" />
                              <path strokeLinecap="round" strokeLinejoin="round" d="M19 6l-1 14H6L5 6" />
                              <path strokeLinecap="round" strokeLinejoin="round" d="M10 11v6" />
                              <path strokeLinecap="round" strokeLinejoin="round" d="M14 11v6" />
                            </svg>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
