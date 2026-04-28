import { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  fetchProfileImage,
  getUserInfo,
  isAuthenticated,
  logout,
  redirectToLogin,
} from "../services/authService";
import ErrorPopup from "../components/ErrorPopup";
import {
  RESOURCE_TABLES,
  NON_RESOURCE_TABLES,
  fetchFirstAvailableResource,
  formatDate,
  getItemLastUpdate,
  getMostRecentDate,
  hasAdministratorRole
} from "../services/dashboardUtils";
import {
  assignRoleToUser,
  deleteRole,
  deleteFileById,
  deleteResource,
  fetchResource,
  fetchRoleManagementData,
  removeRoleFromUser,
  fetchDataSources,
  deleteDataSource,
} from "../services/resourcesServices";
import { parseColor } from "../services/stringServices.jsx";

const RESOURCE_FILE_ID_KEYS = {
  report: ["document_file_id", "documentFileId"],
  document: ["file_id", "fileId"],
  simulator: ["specs_file_id", "specsFileId"],
};

function getLinkedFileId(resourceType, resourceData) {
  const candidates = RESOURCE_FILE_ID_KEYS[resourceType] || [];
  for (const key of candidates) {
    const value = resourceData?.[key];
    if (value !== null && value !== undefined && value !== "") {
      return value;
    }
  }
  return null;
}

function getRoleNamesFromItem(item) {
  const roles = item?.roles;
  if (!Array.isArray(roles)) {
    return [];
  }

  return roles
    .map((role) => {
      if (typeof role === "string") {
        return role;
      }
      if (role && typeof role.name === "string") {
        return role.name;
      }
      return "";
    })
    .filter(Boolean);
}

function RoleManagementTable({ roles, onDelete }) {
  const navigate = useNavigate();

  return (
    <div className="w-full max-w-5xl mt-8 bg-white shadow-md rounded-xl border border-gray-200 overflow-hidden">
      {/* HEADER */}
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 className="text-xl font-semibold text-gray-800">
          Roles
        </h3>

        <button
          onClick={() => navigate("/create-role")}
          className="border border-primary-blue text-primary-blue px-3 py-1.5 rounded-lg text-xs font-semibold hover:bg-blue-50 transition"
        >
          Create New Role
        </button>
      </div>

      {/* TABLE */}
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-gray-50 text-gray-700 uppercase tracking-wide text-xs">
            <tr>
              <th className="px-6 py-3">Nombre</th>
              <th className="px-6 py-3">Descripción</th>
              <th className="px-6 py-3">Acciones</th>
            </tr>
          </thead>

          <tbody>
            {roles.length === 0 ? (
              <tr className="border-t border-gray-100">
                <td colSpan={3} className="px-6 py-4 text-gray-500">
                  No roles available.
                </td>
              </tr>
            ) : (
              roles.map((role) => {
                const isAdmin = role.name === "Administrador";

                return (
                  <tr
                    key={role.id}
                    className="border-t border-gray-100 hover:bg-gray-50 transition"
                  >
                    <td className="px-6 py-3 text-gray-900 font-medium">
                      {role.name}
                    </td>

                    <td className="px-6 py-3 text-gray-700">
                      {role.description || (
                        <span className="text-gray-400">
                          No description
                        </span>
                      )}
                    </td>

                    <td className="px-6 py-3">
                      {!isAdmin && (
                        <div className="flex items-center gap-2">
                          {/* EDIT BUTTON */}
                          <button
                            onClick={() =>
                              navigate(`/edit-role/${role.id}`)
                            }
                            className="inline-flex items-center justify-center rounded-lg border border-primary-blue text-primary-blue hover:bg-blue-50 px-2 py-1 transition"
                            title="Edit Role"
                            aria-label="Edit Role"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2"
                              className="w-4 h-4"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"
                              />
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"
                              />
                            </svg>
                          </button>

                          {/* DELETE BUTTON */}
                          <button
                            onClick={() => onDelete(role.id)}
                            className="inline-flex items-center justify-center rounded-lg border border-red-300 text-red-600 hover:bg-red-50 px-2 py-1 transition"
                            title="Delete Role"
                            aria-label="Delete Role"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2"
                              className="w-4 h-4"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M3 6h18"
                              />
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M8 6V4h8v2"
                              />
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M19 6l-1 14H6L5 6"
                              />
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M10 11v6"
                              />
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M14 11v6"
                              />
                            </svg>
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [imageSrc, setImageSrc] = useState("https://via.placeholder.com/150");
  const [hasAdminAccess, setHasAdminAccess] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);
  const [resourcesByType, setResourcesByType] = useState({});
  const [dataSources, setDataSources] = useState([]);
  const [tablesLoading, setTablesLoading] = useState(true);
  const [refreshCounter, setRefreshCounter] = useState(0);
  const [lastRefreshedAt, setLastRefreshedAt] = useState(null);
  const [deletingKey, setDeletingKey] = useState(null);
  const [actionMessage, setActionMessage] = useState("");
  const [roleManagerLoading, setRoleManagerLoading] = useState(true);
  const [roleActionLoading, setRoleActionLoading] = useState(false);
  const [manageableRoles, setManageableRoles] = useState([]);
  const [usersForRoles, setUsersForRoles] = useState([]);
  const [roleSearchQuery, setRoleSearchQuery] = useState("");
  const [selectedUserEmail, setSelectedUserEmail] = useState("");
  const [selectedRoleId, setSelectedRoleId] = useState("");
  const [roleManagerMessage, setRoleManagerMessage] = useState("");
  const [roleManagerMessageType, setRoleManagerMessageType] = useState("");

  const trimmedRoleSearchQuery = roleSearchQuery.trim().toLowerCase();
  const filteredUsersForRoles = useMemo(() => {
    if (!trimmedRoleSearchQuery) {
      return [];
    }

    return usersForRoles.filter((user) => {
      const fullName = `${user.names || ""} ${user.last_names || ""}`.toLowerCase();
      const userEmail = (user.email || "").toLowerCase();
      return fullName.includes(trimmedRoleSearchQuery) || userEmail.includes(trimmedRoleSearchQuery);
    });
  }, [trimmedRoleSearchQuery, usersForRoles]);

  useEffect(() => {
    if (!isAuthenticated()) {
      redirectToLogin(navigate, "/dashboard");
      return;
    }

    const user = getUserInfo();
    const isAdmin = hasAdministratorRole(user);
    setHasAdminAccess(isAdmin);
    setAuthChecked(true);

    if (!isAdmin) {
      setTablesLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    if (!authChecked || !hasAdminAccess) {
      return;
    }

    let active = true;

    const loadResources = async () => {
      setTablesLoading(true);

      const entries = await Promise.all(
        [...NON_RESOURCE_TABLES, ...RESOURCE_TABLES].map(async (resourceTable) => {
          const result = await fetchFirstAvailableResource(resourceTable.endpointCandidates);
          return [resourceTable.key, result];
        })
      );

      if (!active) {
        return;
      }

      setResourcesByType(Object.fromEntries(entries));
      
      // Load data sources
      try {
        const dataSourcesData = await fetchDataSources();
        setDataSources(Array.isArray(dataSourcesData) ? dataSourcesData.slice(0, 5) : []);
      } catch {
        setDataSources([]);
      }

      setLastRefreshedAt(new Date());
      setTablesLoading(false);
    };

    loadResources();

    return () => {
      active = false;
    };
  }, [authChecked, hasAdminAccess, refreshCounter]);

  useEffect(() => {
    if (!authChecked || !hasAdminAccess) {
      return;
    }

    let active = true;

    const loadRoleManagerData = async () => {
      setRoleManagerLoading(true);
      setRoleManagerMessage("");
      setRoleManagerMessageType("");

      try {
        const data = await fetchRoleManagementData({ excludeAdmin: false });
        if (!active) {
          return;
        }

        const roles = Array.isArray(data?.roles) ? data.roles : [];
        const users = Array.isArray(data?.users) ? data.users : [];

        setManageableRoles(roles);
        setUsersForRoles(users);
        setSelectedRoleId((prev) => prev || String(roles[0]?.id || ""));
      } catch (error) {
        if (active) {
          setRoleManagerMessage(error?.message || "No fue posible cargar el gestor de roles.");
          setRoleManagerMessageType("error");
        }
      } finally {
        if (active) {
          setRoleManagerLoading(false);
        }
      }
    };

    loadRoleManagerData();

    return () => {
      active = false;
    };
  }, [authChecked, hasAdminAccess]);

  useEffect(() => {
    if (!trimmedRoleSearchQuery) {
      setSelectedUserEmail("");
      return;
    }

    setSelectedUserEmail((prev) => {
      if (prev && filteredUsersForRoles.some((user) => user.email === prev)) {
        return prev;
      }
      return filteredUsersForRoles[0]?.email || "";
    });
  }, [trimmedRoleSearchQuery, filteredUsersForRoles]);

  useEffect(() => {
    if (!authChecked || !hasAdminAccess) {
      return;
    }

    let active = true;

    const loadImage = async () => {
      const user = getUserInfo();
      if (!user?.imageId) {
        return;
      }

      try {
        const url = await fetchProfileImage(user.imageId);
        if (active && url) {
          setImageSrc(url);
        }
      } catch {
        if (active) {
          setImageSrc("https://via.placeholder.com/150");
        }
      }
    };

    loadImage();

    return () => {
      active = false;
    };
  }, [authChecked, hasAdminAccess]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const handleRefresh = () => {
    if (tablesLoading) {
      return;
    }
    setRefreshCounter((value) => value + 1);
  };

  const updateUserInRoleState = (updatedUser) => {
    if (!updatedUser?.email) {
      return;
    }

    setUsersForRoles((prev) => prev.map((user) => (user.email === updatedUser.email ? updatedUser : user)));
  };

  const handleAssignRole = async () => {
    if (!selectedUserEmail || !selectedRoleId) {
      setRoleManagerMessage("Selecciona un usuario y un rol.");
      setRoleManagerMessageType("error");
      return;
    }

    setRoleActionLoading(true);
    setRoleManagerMessage("");
    setRoleManagerMessageType("");

    try {
      const updatedUser = await assignRoleToUser(selectedUserEmail, Number(selectedRoleId));
      updateUserInRoleState(updatedUser);
      setRoleManagerMessage("Rol asignado correctamente.");
      setRoleManagerMessageType("success");
    } catch (error) {
      setRoleManagerMessage(error?.message || "No fue posible asignar el rol.");
      setRoleManagerMessageType("error");
    } finally {
      setRoleActionLoading(false);
    }
  };

  const handleRemoveRole = async () => {
    if (!selectedUserEmail || !selectedRoleId) {
      setRoleManagerMessage("Selecciona un usuario y un rol.");
      setRoleManagerMessageType("error");
      return;
    }

    setRoleActionLoading(true);
    setRoleManagerMessage("");
    setRoleManagerMessageType("");

    try {
      const updatedUser = await removeRoleFromUser(selectedUserEmail, Number(selectedRoleId));
      updateUserInRoleState(updatedUser);
      setRoleManagerMessage("Rol retirado correctamente.");
      setRoleManagerMessageType("success");
    } catch (error) {
      setRoleManagerMessage(error?.message || "No fue posible retirar el rol.");
      setRoleManagerMessageType("error");
    } finally {
      setRoleActionLoading(false);
    }
  };

  const handleDeleteResource = async (resourceType, row) => {
    const resourceId = row?.id;
    const confirmed = window.confirm("¿Seguro que deseas eliminar este recurso?");
    if (!confirmed) {
      return;
    }

    if (!resourceId) {
      setActionMessage("No fue posible identificar el recurso a eliminar.");
      return;
    }

    const key = `${resourceType}-${resourceId}`;
    setDeletingKey(key);
    setActionMessage("");

    try {
      let linkedFileId = getLinkedFileId(resourceType, row);

      // Read full resource only when file id is not present in list payload.
      if (!linkedFileId && RESOURCE_FILE_ID_KEYS[resourceType]) {
        try {
          const fullResource = await fetchResource(resourceType, resourceId);
          linkedFileId = getLinkedFileId(resourceType, fullResource);
        } catch {
          // Keep delete flow even when full resource lookup fails.
        }
      }

      await deleteResource(resourceType, resourceId, true);

      if (linkedFileId) {
        try {
          await deleteFileById(linkedFileId);
          setActionMessage("Recurso y documento asociado eliminados correctamente.");
        } catch {
          setActionMessage("Recurso eliminado, pero no fue posible eliminar el documento asociado.");
        }
      } else {
        setActionMessage("Recurso eliminado correctamente.");
      }

      setRefreshCounter((value) => value + 1);
    } catch (error) {
      setActionMessage(error?.message || "No fue posible eliminar el recurso.");
    } finally {
      setDeletingKey(null);
    }
  };

  const handleDeleteDataSource = async (dataSourceId) => {
    const confirmed = window.confirm("¿Seguro que deseas eliminar esta fuente de datos?");
    if (!confirmed) {
      return;
    }

    const key = `data-source-${dataSourceId}`;
    setDeletingKey(key);
    setActionMessage("");

    try {
      await deleteDataSource(dataSourceId);
      setActionMessage("Fuente de datos eliminada correctamente.");
      setRefreshCounter((value) => value + 1);
    } catch (error) {
      setActionMessage(error?.message || "No fue posible eliminar la fuente de datos.");
    } finally {
      setDeletingKey(null);
    }
  };

  const handleDeleteRole = async (roleId) => {
    const confirmed = window.confirm("¿Seguro que deseas eliminar este rol?");
    if (!confirmed) {
      return;
    }

    try {
      await deleteRole(roleId);
      setManageableRoles((prevRoles) => prevRoles.filter((role) => role.id !== roleId));
      setRoleManagerMessage("Rol eliminado correctamente.");
      setRoleManagerMessageType("success");
    } catch (error) {
      setRoleManagerMessage(error?.message || "No fue posible eliminar el rol.");
      setRoleManagerMessageType("error");
    }
  };

  const lastRefreshLabel = lastRefreshedAt
    ? lastRefreshedAt.toLocaleString("es-CO", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "Aun no se ha actualizado";

  const userInfo = getUserInfo();
  const name = userInfo?.names || "Invitado";
  const lastName = userInfo?.lastNames || "";
  const email = userInfo?.email || "desconocido";

  const summaryRows = [...RESOURCE_TABLES, ...NON_RESOURCE_TABLES].map((resource) => {
    const resourceResult = resourcesByType[resource.key];
    const data = resourceResult?.data || [];
    const lastUpdateDate = getMostRecentDate(data);

    return {
      key: resource.key,
      title: resource.title,
      createType: resource.endpointCandidates[0],
      total: data.length,
      lastUpdateDate,
      status: resourceResult?.error ? "No disponible" : "Disponible",
    };
  });

  if (!authChecked) {
    return (
      <div className="p-10 flex items-center justify-center">
        <p className="text-lg text-gray-700">Verificando sesion...</p>
      </div>
    );
  }

  if (!hasAdminAccess) {
    return (
      <ErrorPopup
        error="Tu cuenta no tiene permisos de Administrador para acceder a este panel."
        onClose={() => handleLogout()}
      />
    );
  }

  return (
    <div className="p-10 flex flex-col items-center">
      {/* USER INFO BLOCK */}
      <div className="flex flex-col md:flex-row items-center justify-center mt-12 gap-10 text-center md:text-left">

        {/* LEFT — IMAGE */}
        <div className="flex flex-col items-center md:items-start">
          <img
            src={imageSrc}
            alt="Avatar de usuario"
            className="w-32 h-32 rounded-full mb-4 object-cover"
          />
        </div>

        {/* RIGHT — INFO */}
        <div className="flex flex-col items-center md:items-start text-lg">
          <p>Bienvenido,</p>
          <p className="font-semibold">
            {name} {lastName}!
          </p>
          <p>Correo: {email}</p>
        </div>
      </div>

      <div className="w-full max-w-5xl mt-12 bg-white shadow-md rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 flex flex-col md:flex-row gap-4 md:items-center md:justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-secondary-cyan-strong">Resumen de recursos</h2>
            <p className="text-sm text-gray-600 mt-1">Recursos disponibles por categoria para administradores.</p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={tablesLoading}
            className="bg-secondary-cyan-strong text-white px-4 py-2 rounded-lg text-sm font-semibold hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {tablesLoading ? "Actualizando..." : "Actualizar datos"}
          </button>
          <p className="text-xs text-gray-600 md:text-right">
            Ultima actualizacion: {lastRefreshLabel}
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-gray-50 text-gray-700 uppercase tracking-wide text-xs">
              <tr>
                <th className="px-6 py-3">Tipo de recurso</th>
                <th className="px-6 py-3">Total disponible</th>
                <th className="px-6 py-3">Ultima actualizacion</th>
                <th className="px-6 py-3">Estado</th>
              </tr>
            </thead>
            <tbody>
              {summaryRows.map((row) => (
                <tr key={row.key} className="border-t border-gray-100">
                  <td className="px-6 py-3 font-medium text-gray-900">{row.title}</td>
                  <td className="px-6 py-3 text-gray-700">{tablesLoading ? "..." : row.total}</td>
                  <td className="px-6 py-3 text-gray-700">{tablesLoading ? "..." : formatDate(row.lastUpdateDate)}</td>
                  <td className="px-6 py-3">
                    <span
                      className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold ${
                        row.status === "Disponible"
                          ? "bg-green-100 text-green-700"
                          : "bg-yellow-100 text-yellow-800"
                      }`}
                    >
                      {tablesLoading ? "Cargando" : row.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {actionMessage && (
        <div className="w-full max-w-5xl mt-4 rounded-lg border border-blue-200 bg-blue-50 text-blue-700 px-4 py-3 text-sm">
          {actionMessage}
        </div>
      )}

      {RESOURCE_TABLES.map((resource) => {
        const resourceResult = resourcesByType[resource.key];
        const rows = resourceResult?.data || [];
        const resourceType = resource.endpointCandidates[0];

        return (
          <div
            key={resource.key}
            className="w-full max-w-5xl mt-8 bg-white shadow-md rounded-xl border border-gray-200 overflow-hidden"
          >
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h3 className="text-xl font-semibold text-gray-800">{resource.title}</h3>
              <div className="flex items-center gap-3">
                <span className="text-sm text-gray-500">Ultimos 5 registros</span>
                <button
                  onClick={() => navigate(`/resources/create?type=${resource.endpointCandidates[0]}`)}
                  className="border border-primary-blue text-primary-blue px-3 py-1.5 rounded-lg text-xs font-semibold hover:bg-blue-50 transition"
                >
                  Crear {resource.title}
                </button>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead className="bg-gray-50 text-gray-700 uppercase tracking-wide text-xs">
                  <tr>
                    <th className="px-6 py-3">Titulo</th>
                    <th className="px-6 py-3">Roles asociados</th>
                    <th className="px-6 py-3">Actualizado en</th>
                    <th className="px-6 py-3">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {!tablesLoading && rows.length === 0 && (
                    <tr className="border-t border-gray-100">
                      <td className="px-6 py-4 text-gray-500" colSpan={4}>
                        No hay registros disponibles.
                      </td>
                    </tr>
                  )}

                  {(tablesLoading ? [] : rows.slice(0, 5)).map((row) => (
                    <tr key={row.id} className="border-t border-gray-100">
                      <td className="px-6 py-3 text-gray-900 font-medium">
                        {row.title
                          ? parseColor(row.title, "font-bold")
                          : "No disponible"}
                      </td>
                      <td className="px-6 py-3 text-gray-700">
                        {(() => {
                          const roleNames = getRoleNamesFromItem(row);
                          return roleNames.length > 0 ? roleNames.join(", ") : "Sin roles asociados";
                        })()}
                      </td>
                      <td className="px-6 py-3 text-gray-700">{formatDate(getItemLastUpdate(row))}</td>
                      <td className="px-6 py-3">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => navigate(`/resource/${resourceType}/${row.id}`)}
                            className="inline-flex items-center justify-center rounded-lg border border-emerald-300 text-emerald-700 hover:bg-emerald-50 px-2 py-1 transition"
                            title="Ver recurso"
                            aria-label="Ver recurso"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2"
                              className="w-4 h-4"
                            >
                              <path strokeLinecap="round" strokeLinejoin="round" d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z" />
                              <circle cx="12" cy="12" r="3" />
                            </svg>
                          </button>
                          <button
                            onClick={() => navigate(`/resource/edit/${resourceType}/${row.id}`)}
                            className="inline-flex items-center justify-center rounded-lg border border-primary-blue text-primary-blue hover:bg-blue-50 px-2 py-1 transition"
                            title="Editar recurso"
                            aria-label="Editar recurso"
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
                            onClick={() => handleDeleteResource(resourceType, row)}
                            disabled={deletingKey === `${resourceType}-${row.id}`}
                            className="inline-flex items-center justify-center rounded-lg border border-red-300 text-red-600 hover:bg-red-50 px-2 py-1 transition disabled:opacity-50 disabled:cursor-not-allowed"
                            title="Eliminar recurso"
                            aria-label="Eliminar recurso"
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

                  {tablesLoading && (
                    <tr className="border-t border-gray-100">
                      <td className="px-6 py-4 text-gray-500" colSpan={4}>
                        Cargando registros...
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        );
      })}

      {/* DATA SOURCES SECTION */}
      <div className="w-full max-w-5xl mt-8 bg-white shadow-md rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="text-xl font-semibold text-gray-800">Fuentes de Datos</h3>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">Ultimos 5 registros</span>
            <button
              onClick={() => navigate("/data-sources/create")}
              className="border border-primary-blue text-primary-blue px-3 py-1.5 rounded-lg text-xs font-semibold hover:bg-blue-50 transition"
            >
              Crear fuente de datos
            </button>
          </div>
        </div>
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
              {!tablesLoading && dataSources.length === 0 && (
                <tr className="border-t border-gray-100">
                  <td className="px-6 py-4 text-gray-500" colSpan={4}>
                    No hay fuentes de datos disponibles.
                  </td>
                </tr>
              )}

              {(tablesLoading ? [] : dataSources).map((dataSource) => (
                <tr key={dataSource.id} className="border-t border-gray-100">
                  <td className="px-6 py-3 text-gray-900 font-medium">
                    {dataSource.name
                      ? parseColor(dataSource.name, "font-bold")
                      : "Sin nombre"}
                  </td>
                  <td className="px-6 py-3 text-gray-700">
                    {dataSource.description ? (
                      parseColor(dataSource.description, "text-sm")
                    ) : (
                      <span className="text-gray-400">Sin descripción</span>
                    )}
                  </td>
                  <td className="px-6 py-3 text-gray-700">{formatDate(getItemLastUpdate(dataSource))}</td>
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
                        onClick={() => handleDeleteDataSource(dataSource.id)}
                        disabled={deletingKey === `data-source-${dataSource.id}`}
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

              {tablesLoading && (
                <tr className="border-t border-gray-100">
                  <td className="px-6 py-4 text-gray-500" colSpan={4}>
                    Cargando registros...
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ROLE */}
      <RoleManagementTable roles={manageableRoles} onDelete={handleDeleteRole} />

      {/* ROLE MANAGEMENT SECTION */}
      <div className="w-full max-w-5xl mt-10 bg-white shadow-md rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-xl font-semibold text-gray-800">Gestor de roles</h3>
          <p className="text-sm text-gray-600 mt-1">Busca usuarios por nombre o correo para ver sus roles y ajustar permisos.</p>
        </div>

        <div className="p-6 space-y-5">
          {roleManagerLoading ? (
            <p className="text-sm text-gray-600">Cargando usuarios y roles...</p>
          ) : (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Buscar usuario o correo</label>
                <input
                  type="text"
                  value={roleSearchQuery}
                  onChange={(e) => setRoleSearchQuery(e.target.value)}
                  placeholder="Ejemplo: juan o juan@unal.edu.co"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  disabled={roleActionLoading}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Usuario</label>
                  <select
                    value={selectedUserEmail}
                    onChange={(e) => setSelectedUserEmail(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    disabled={roleActionLoading}
                  >
                    <option value="">Selecciona un usuario de los resultados</option>
                    {filteredUsersForRoles.map((user) => (
                      <option key={user.email} value={user.email}>
                        {user.names} {user.last_names} ({user.email})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Rol</label>
                  <select
                    value={selectedRoleId}
                    onChange={(e) => setSelectedRoleId(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    disabled={roleActionLoading}
                  >
                    <option value="">Selecciona un rol</option>
                    {manageableRoles.map((role) => (
                      <option key={role.id} value={role.id}>
                        {role.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={handleAssignRole}
                  disabled={roleActionLoading}
                  className="bg-secondary-cyan-strong text-white px-4 py-2 rounded-lg text-sm font-semibold hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Agregar usuario al rol
                </button>
                <button
                  onClick={handleRemoveRole}
                  disabled={roleActionLoading}
                  className="border border-red-300 text-red-600 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-red-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Retirar usuario del rol
                </button>
              </div>

              {roleManagerMessage && (
                <div
                  className={`rounded-lg border px-4 py-3 text-sm flex items-start justify-between gap-3 ${
                    roleManagerMessageType === "error"
                      ? "border-red-200 bg-red-50 text-red-700"
                      : "border-green-200 bg-green-50 text-green-700"
                  }`}
                >
                  <span>{roleManagerMessage}</span>
                  <button
                    type="button"
                    onClick={() => {
                      setRoleManagerMessage("");
                      setRoleManagerMessageType("");
                    }}
                    className="inline-flex items-center justify-center rounded border border-current px-1.5 py-0.5 text-xs font-semibold hover:opacity-80 transition"
                    aria-label="Cerrar mensaje"
                    title="Cerrar"
                  >
                    x
                  </button>
                </div>
              )}

              <div className="overflow-x-auto border border-gray-200 rounded-lg">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-gray-50 text-gray-700 uppercase tracking-wide text-xs">
                    <tr>
                      <th className="px-4 py-3">Usuario</th>
                      <th className="px-4 py-3">Correo</th>
                      <th className="px-4 py-3">Roles</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsersForRoles.map((user) => (
                      <tr key={user.email} className="border-t border-gray-100">
                        <td className="px-4 py-3 text-gray-800">{user.names} {user.last_names}</td>
                        <td className="px-4 py-3 text-gray-700">{user.email}</td>
                        <td className="px-4 py-3 text-gray-700">
                          {Array.isArray(user.roles) && user.roles.length > 0
                            ? user.roles.map((role) => role.name).join(", ")
                            : "Sin roles adicionales"}
                        </td>
                      </tr>
                    ))}
                    {!trimmedRoleSearchQuery && (
                      <tr className="border-t border-gray-100">
                        <td className="px-4 py-3 text-gray-500" colSpan={3}>
                          La tabla esta vacia. Escribe un nombre o correo para ver resultados.
                        </td>
                      </tr>
                    )}
                    {trimmedRoleSearchQuery && filteredUsersForRoles.length === 0 && (
                      <tr className="border-t border-gray-100">
                        <td className="px-4 py-3 text-gray-500" colSpan={3}>
                          No se encontraron usuarios para la busqueda ingresada.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      </div>

      {/* LOGOUT BUTTON (red, below the info) */}
      <button
        onClick={handleLogout}
        className="mt-10 bg-red-500 text-white px-6 py-3 rounded-xl text-lg shadow-md hover:bg-red-600 transition"
      >
        Cerrar sesion
      </button>
    </div>
  );
}
