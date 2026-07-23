import { getToken } from "./authService";
import { toResourceCardModel, toResourceDisplayModel } from "./resourceModels";

const REQUEST_TIMEOUT_MS = Number(import.meta.env.VITE_REQUEST_TIMEOUT_MS || 10000);

const API_ENDPOINT_ALIASES = {
    report: "report",
    visor: "visor",
    simulator: "simulator",
    document: "document",
    reports: "report",
    visors: "visor",
    simulators: "simulator",
    documents_presentations: "document",
    documents_presentation: "document",
    document_presentation: "document",
    documents: "document",
    document: "document",
};

const RESOURCE_TYPES_WITH_DATA_SOURCES = new Set(["report", "visor", "simulator"]);

function normalizeApiEndpoint(type) {
    if (!type) {
        return type;
    }

    const normalized = String(type).toLowerCase();
    return API_ENDPOINT_ALIASES[normalized] || normalized;
}

function supportsDataSources(type) {
    const endpoint = normalizeApiEndpoint(type);
    return RESOURCE_TYPES_WITH_DATA_SOURCES.has(endpoint);
}

function createTimeoutError(timeoutMs) {
    const error = new Error(`La solicitud tardó demasiado (${timeoutMs} ms)`);
    error.name = "TimeoutError";
    return error;
}

function isTimeoutError(err) {
    return err?.name === "TimeoutError";
}

function isBackendUnavailableError(err) {
    if (isTimeoutError(err)) {
        return true;
    }

    const message = (err?.message || "").toLowerCase();
    const name = (err?.name || "").toLowerCase();
    const isNetworkTypeError = name === "typeerror";
    const isNetworkMessage =
        message.includes("failed to fetch") ||
        message.includes("networkerror") ||
        message.includes("load failed");

    return isNetworkTypeError || isNetworkMessage;
}

async function fetchWithTimeout(url, options = {}, timeoutMs = REQUEST_TIMEOUT_MS) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
        return await fetch(url, {
            ...options,
            signal: controller.signal,
        });
    } catch (err) {
        if (err?.name === "AbortError") {
            throw createTimeoutError(timeoutMs);
        }
        throw err;
    } finally {
        clearTimeout(timeoutId);
    }
}

function redirectToConnectionError() {
    if (typeof window === "undefined") return;
    if (window.location.pathname === "/connection-error") return;
    const origin = encodeURIComponent(window.location.pathname);
    window.location.assign(`${window.location.origin}/connection-error?origin=${origin}`);
}

async function getErrorMessage(response, fallbackMessage) {
    try {
        const data = await response.json();
        if (data && typeof data.message === "string" && data.message.trim() !== "") {
            return data.message;
        }
    } catch {
        return fallbackMessage;
    }
    return fallbackMessage;
}

function isMultipartPayload(payload) {
    return typeof FormData !== "undefined" && payload instanceof FormData;
}

function buildApiUrl(...parts) {
    const base = (import.meta.env.VITE_API_URL || "").replace(/\/+$/g, "");
    const cleaned = parts
        .map((p) => String(p || "").replace(/^\/+|\/+$/g, ""))
        .filter(Boolean)
        .join("/");
    return cleaned ? `${base}/${cleaned}` : base;
}

export async function fetchFromUrl(url) {
    const token = getToken();
    let response;
    try {
        response = await fetchWithTimeout(url, {
            credentials: "include",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }
    if (!response.ok) {
        const message = await getErrorMessage(response, `No fue posible obtener la información solicitada`);
        throw new Error(message);
    }
    return response.json();
}

export async function fetchFileWithAuth(url, additionalParams = {}) {
    const token = getToken();
    
    // Parse the URL to properly handle existing query params
    const urlObj = new URL(url, window.location.origin);
    
    // Add any additional parameters
    Object.entries(additionalParams).forEach(([key, value]) => {
        urlObj.searchParams.set(key, value);
    });
    
    let response;
    try {
        response = await fetchWithTimeout(urlObj.toString(), {
            credentials: "include",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }
    if (!response.ok) {
        const message = await getErrorMessage(response, `No fue posible obtener el archivo solicitado`);
        throw new Error(message);
    }
    const blob = await response.blob();
    return URL.createObjectURL(blob);
}

export async function fetchResources(type) {
    const endpoint = normalizeApiEndpoint(type);
    const fetchUrl = `${import.meta.env.VITE_API_URL}/${endpoint}/all`;
    const token = getToken();
    let response;
    try {
        response = await fetchWithTimeout(fetchUrl, {
            credentials: "include",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }
    if (!response.ok) {
        const message = await getErrorMessage(response, `No fue posible consultar los recursos de tipo ${type}`);
        throw new Error(message);
    }
    return response.json();
}

export async function fetchAssignableRoles() {
    const fetchUrl = `${import.meta.env.VITE_API_URL}/role/all?exclude_admin=true`;
    const token = getToken();
    let response;
    try {
        response = await fetchWithTimeout(fetchUrl, {
            credentials: "include",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }
    if (!response.ok) {
        const message = await getErrorMessage(response, "No fue posible consultar los roles");
        throw new Error(message);
    }
    return response.json();
}

export async function fetchDataSources() {
    const fetchUrl = `${import.meta.env.VITE_API_URL}/data-source/all`;
    const token = getToken();
    let response;
    try {
        response = await fetchWithTimeout(fetchUrl, {
            credentials: "include",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }
    if (!response.ok) {
        const message = await getErrorMessage(response, "No fue posible consultar las fuentes de datos");
        throw new Error(message);
    }
    return response.json();
}

export async function fetchDataSourceFileHistory(dataSourceId) {
    const fetchUrl = `${import.meta.env.VITE_API_URL}/data-source/${dataSourceId}/files`;
    const token = getToken();
    let response;
    try {
        response = await fetchWithTimeout(fetchUrl, {
            credentials: "include",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }
    if (!response.ok) {
        const message = await getErrorMessage(response, "No fue posible consultar el historial de versiones de la fuente de datos");
        throw new Error(message);
    }

    const payload = await response.json();
    return Array.isArray(payload) ? payload : [];
}

export async function fetchResourceDataSources(type, id) {
    if (!supportsDataSources(type)) {
        return [];
    }

    const endpoint = normalizeApiEndpoint(type);
    const fetchUrl = `${import.meta.env.VITE_API_URL}/${endpoint}/${id}/data-sources`;
    const token = getToken();
    let response;
    try {
        response = await fetchWithTimeout(fetchUrl, {
            credentials: "include",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }
    if (!response.ok) {
        const message = await getErrorMessage(response, "No fue posible consultar las fuentes de datos del recurso");
        throw new Error(message);
    }

    const payload = await response.json();
    return Array.isArray(payload) ? payload : [];
}

export async function syncResourceDataSources(type, id, desiredDataSourceIds = []) {
    if (!supportsDataSources(type)) {
        return [];
    }

    const endpoint = normalizeApiEndpoint(type);
    const token = getToken();
    const desiredIds = Array.isArray(desiredDataSourceIds)
        ? Array.from(new Set(desiredDataSourceIds.map((value) => Number(value)).filter(Number.isFinite)))
        : [];

    const currentDataSources = await fetchResourceDataSources(endpoint, id);
    const currentIds = currentDataSources
        .map((item) => Number(item?.id))
        .filter(Number.isFinite);

    const currentSet = new Set(currentIds);
    const desiredSet = new Set(desiredIds);

    const toAdd = desiredIds.filter((dataSourceId) => !currentSet.has(dataSourceId));
    const toRemove = currentIds.filter((dataSourceId) => !desiredSet.has(dataSourceId));

    for (const dataSourceId of toAdd) {
        const addUrl = `${import.meta.env.VITE_API_URL}/${endpoint}/${id}/data-sources/${dataSourceId}`;
        let response;
        try {
            response = await fetchWithTimeout(addUrl, {
                method: "POST",
                credentials: "include",
                headers: {
                    "Authorization": `Bearer ${token}`,
                },
            });
        } catch (err) {
            if (isBackendUnavailableError(err)) {
                redirectToConnectionError();
            }
            throw err;
        }

        if (!response.ok) {
            const message = await getErrorMessage(response, `No fue posible asociar la fuente de datos ${dataSourceId}`);
            throw new Error(message);
        }
    }

    for (const dataSourceId of toRemove) {
        const removeUrl = `${import.meta.env.VITE_API_URL}/${endpoint}/${id}/data-sources/${dataSourceId}`;
        let response;
        try {
            response = await fetchWithTimeout(removeUrl, {
                method: "DELETE",
                credentials: "include",
                headers: {
                    "Authorization": `Bearer ${token}`,
                },
            });
        } catch (err) {
            if (isBackendUnavailableError(err)) {
                redirectToConnectionError();
            }
            throw err;
        }

        if (!response.ok) {
            const message = await getErrorMessage(response, `No fue posible desasociar la fuente de datos ${dataSourceId}`);
            throw new Error(message);
        }
    }

    return fetchResourceDataSources(endpoint, id);
}

export async function fetchRoleManagementData(options = {}) {
    const excludeAdmin = options.excludeAdmin ?? true;
    const fetchUrl = `${import.meta.env.VITE_API_URL}/role/management-data?exclude_admin=${excludeAdmin}`;
    const token = getToken();
    let response;
    try {
        response = await fetchWithTimeout(fetchUrl, {
            credentials: "include",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }
    if (!response.ok) {
        const message = await getErrorMessage(response, "No fue posible consultar la información de gestión de roles");
        throw new Error(message);
    }
    return response.json();
}

export async function assignRoleToUser(userEmail, roleId) {
    const url = `${import.meta.env.VITE_API_URL}/role/assign`;
    const token = getToken();

    let response;
    try {
        response = await fetchWithTimeout(url, {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify({
                user_email: userEmail,
                role_id: roleId,
            }),
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }

    if (!response.ok) {
        const message = await getErrorMessage(response, "No fue posible asignar el rol al usuario");
        throw new Error(message);
    }

    return response.json();
}

export async function removeRoleFromUser(userEmail, roleId) {
    const url = `${import.meta.env.VITE_API_URL}/role/remove`;
    const token = getToken();

    let response;
    try {
        response = await fetchWithTimeout(url, {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify({
                user_email: userEmail,
                role_id: roleId,
            }),
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }

    if (!response.ok) {
        const message = await getErrorMessage(response, "No fue posible retirar el rol del usuario");
        throw new Error(message);
    }

    return response.json();
}


export async function fetchResource(type, id) {
    const endpoint = normalizeApiEndpoint(type);
    const fetchUrl = `${import.meta.env.VITE_API_URL}/${endpoint}/${id}`;
    const token = getToken();
    let response;
    try {
        response = await fetchWithTimeout(fetchUrl, {
            credentials: "include",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }
    if (!response.ok) {
        const message = await getErrorMessage(
            response,
            `No fue posible consultar el recurso ${type} con id ${id}`
        );
        throw new Error(message);
    }
    return response.json();
}

export async function uploadResourceFile(file) {
    if (!(file instanceof File)) {
        throw new Error("Debes seleccionar un archivo válido");
    }

    const uploadUrl = `${import.meta.env.VITE_API_URL}/file/upload`;
    const token = getToken();
    const formData = new FormData();
    formData.append("file", file);

    let response;
    try {
        response = await fetchWithTimeout(uploadUrl, {
            method: "POST",
            credentials: "include",
            headers: {
                "Authorization": `Bearer ${token}`,
            },
            body: formData,
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }

    if (!response.ok) {
        const message = await getErrorMessage(response, "No fue posible cargar el archivo");
        if (typeof window !== "undefined") {
            window.dispatchEvent(new CustomEvent("show-error-popup", { detail: { message } }));
        }
        throw new Error(message);
    }

    return response.json();
}

export async function createResource(type, payload, updatedDate = null) {
    const endpoint = normalizeApiEndpoint(type);
    const createUrl = `${import.meta.env.VITE_API_URL}/${endpoint}`;
    const token = getToken();

    const multipartPayload = isMultipartPayload(payload);
    const payloadToSend = multipartPayload ? payload : { ...payload };
    if (updatedDate) {
        if (multipartPayload) {
            payloadToSend.append("updated_at", updatedDate);
        } else {
            payloadToSend.updated_at = updatedDate;
        }
    }

    const headers = {
        "Authorization": `Bearer ${token}`,
    };
    if (!multipartPayload) {
        headers["Content-Type"] = "application/json";
    }

    let response;
    try {
        response = await fetchWithTimeout(createUrl, {
            method: "POST",
            credentials: "include",
            headers,
            body: multipartPayload ? payloadToSend : JSON.stringify(payloadToSend),
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }

    if (!response.ok) {
        const message = await getErrorMessage(response, `No fue posible crear el recurso de tipo ${type}`);
        if (typeof window !== "undefined") {
            window.dispatchEvent(new CustomEvent("show-error-popup", { detail: { message } }));
        }
        throw new Error(message);
    }

    return response.json();
}

export async function updateResource(type, id, payload, updatedDate = null) {
    const endpoint = normalizeApiEndpoint(type);
    const updateUrl = `${import.meta.env.VITE_API_URL}/${endpoint}/${id}`;
    const token = getToken();

    const multipartPayload = isMultipartPayload(payload);
    const payloadToSend = multipartPayload ? payload : { ...payload };
    if (updatedDate) {
        if (multipartPayload) {
            payloadToSend.append("updated_at", updatedDate);
        } else {
            payloadToSend.updated_at = updatedDate;
        }
    }

    const headers = {
        "Authorization": `Bearer ${token}`,
    };
    if (!multipartPayload) {
        headers["Content-Type"] = "application/json";
    }

    let response;
    try {
        response = await fetchWithTimeout(updateUrl, {
            method: "PATCH",
            credentials: "include",
            headers,
            body: multipartPayload ? payloadToSend : JSON.stringify(payloadToSend),
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }

    if (!response.ok) {
        const message = await getErrorMessage(response, `No fue posible actualizar el recurso de tipo ${type}`);
        if (typeof window !== "undefined") {
            window.dispatchEvent(new CustomEvent("show-error-popup", { detail: { message } }));
        }
        throw new Error(message);
    }

    return response.json();
}

export async function updateResourceRoles(type, id, roleIds = []) {
    const endpoint = normalizeApiEndpoint(type);
    const updateRolesUrl = `${import.meta.env.VITE_API_URL}/${endpoint}/${id}/roles`;
    const token = getToken();

    let response;
    try {
        response = await fetchWithTimeout(updateRolesUrl, {
            method: "PATCH",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify({ role_ids: Array.isArray(roleIds) ? roleIds : [] }),
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }

    if (!response.ok) {
        const message = await getErrorMessage(response, `No fue posible actualizar los roles del recurso ${type}`);
        throw new Error(message);
    }

    return response.json();
}

export async function deleteResource(type, id, cascade = true) {
    const query = cascade ? "?cascade=true" : "";
    const endpoint = normalizeApiEndpoint(type);
    const base = (import.meta.env.VITE_API_URL || "").replace(/\/+$/g, "");
    const ep = String(endpoint || "").replace(/^\/+|\/+$/g, "");
    const deleteUrl = `${base}/${ep}/${id}${query}`;
    const token = getToken();

    let response;
    try {
        response = await fetchWithTimeout(deleteUrl, {
            method: "DELETE",
            credentials: "include",
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }

    if (!response.ok) {
        const message = await getErrorMessage(response, `No fue posible eliminar el recurso ${type} con id ${id}`);
        if (typeof window !== "undefined") {
            window.dispatchEvent(new CustomEvent("show-error-popup", { detail: { message } }));
        }
        throw new Error(message);
    }
}

export async function deleteFileById(fileId) {
    const deleteUrl = `${import.meta.env.VITE_API_URL}/file/${fileId}`;
    const token = getToken();

    let response;
    try {
        response = await fetchWithTimeout(deleteUrl, {
            method: "DELETE",
            credentials: "include",
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }

    if (!response.ok) {
        const message = await getErrorMessage(response, `No fue posible eliminar el archivo ${fileId}`);
        if (typeof window !== "undefined") {
            window.dispatchEvent(new CustomEvent("show-error-popup", { detail: { message } }));
        }
        throw new Error(message);
    }
}

export async function createDataSource(payload) {
    const url = `${import.meta.env.VITE_API_URL}/data-source`;
    const token = getToken();

    let response;
    try {
        response = await fetchWithTimeout(url, {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify(payload),
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }

    if (!response.ok) {
        const message = await getErrorMessage(response, "No fue posible crear la fuente de datos");
        if (typeof window !== "undefined") {
            window.dispatchEvent(new CustomEvent("show-error-popup", { detail: { message } }));
        }
        throw new Error(message);
    }

    return response.json();
}

export async function updateDataSource(dataSourceId, payload) {
    const url = `${import.meta.env.VITE_API_URL}/data-source/${dataSourceId}`;
    const token = getToken();

    let response;
    try {
        response = await fetchWithTimeout(url, {
            method: "PUT",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify(payload),
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }

    if (!response.ok) {
        const message = await getErrorMessage(response, "No fue posible actualizar la fuente de datos");
        if (typeof window !== "undefined") {
            window.dispatchEvent(new CustomEvent("show-error-popup", { detail: { message } }));
        }
        throw new Error(message);
    }

    return response.json();
}

export async function deleteDataSource(dataSourceId) {
    const url = `${import.meta.env.VITE_API_URL}/data-source/${dataSourceId}`;
    const token = getToken();

    let response;
    try {
        response = await fetchWithTimeout(url, {
            method: "DELETE",
            credentials: "include",
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }

    if (!response.ok) {
        const message = await getErrorMessage(response, "No fue posible eliminar la fuente de datos");
        if (typeof window !== "undefined") {
            window.dispatchEvent(new CustomEvent("show-error-popup", { detail: { message } }));
        }
        throw new Error(message);
    }
}

export async function createRole(payload) {
    return createResource("role", payload);
}

export async function updateRole(roleId, payload) {
    return updateResource("role", roleId, payload);
}

export async function deleteRole(roleId) {
    return deleteResource("role", roleId, true);
}

export function parseResourcesForCards(type, data) {
    if (!Array.isArray(data) || data.length === 0) return [];
    return data.map((item) => toResourceCardModel(type, item));
}

export function parseResourcesText(type, data) {
    return toResourceDisplayModel(type, data);
}

export { isTimeoutError, isBackendUnavailableError };