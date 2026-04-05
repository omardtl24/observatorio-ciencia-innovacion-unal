import { getToken } from "./authService";
import { toResourceCardModel, toResourceDisplayModel } from "./resourceModels";

const REQUEST_TIMEOUT_MS = Number(import.meta.env.VITE_REQUEST_TIMEOUT_MS || 10000);

function createTimeoutError(timeoutMs) {
    const error = new Error(`Request timeout after ${timeoutMs}ms`);
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
        const message = await getErrorMessage(response, `Failed to fetch from ${url}`);
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
        const message = await getErrorMessage(response, `Failed to fetch file from ${url}`);
        throw new Error(message);
    }
    const blob = await response.blob();
    return URL.createObjectURL(blob);
}

export async function fetchResources(type) {
    const fetchUrl = `${import.meta.env.VITE_API_URL}/${type}/all`;
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
        const message = await getErrorMessage(response, `Failed to fetch ${type} resources`);
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
        const message = await getErrorMessage(response, "Failed to fetch roles");
        throw new Error(message);
    }
    return response.json();
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
        const message = await getErrorMessage(response, "Failed to fetch role management data");
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
        const message = await getErrorMessage(response, "Failed to assign role to user");
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
        const message = await getErrorMessage(response, "Failed to remove role from user");
        throw new Error(message);
    }

    return response.json();
}


export async function fetchResource(type, id) {
    const fetchUrl = `${import.meta.env.VITE_API_URL}/${type}/${id}`;
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
            `Failed to fetch ${type} resource with ID ${id}`
        );
        throw new Error(message);
    }
    return response.json();
}

export async function uploadResourceFile(file) {
    if (!(file instanceof File)) {
        throw new Error("A valid file is required");
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
        const message = await getErrorMessage(response, "Failed to upload file");
        throw new Error(message);
    }

    return response.json();
}

export async function createResource(type, payload, updatedDate = null) {
    const createUrl = `${import.meta.env.VITE_API_URL}/${type}`;
    const token = getToken();

    const payloadToSend = { ...payload };
    if (updatedDate) {
        payloadToSend.updated_at = updatedDate;
    }

    let response;
    try {
        response = await fetchWithTimeout(createUrl, {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify(payloadToSend),
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }

    if (!response.ok) {
        const message = await getErrorMessage(response, `Failed to create ${type}`);
        throw new Error(message);
    }

    return response.json();
}

export async function updateResource(type, id, payload, updatedDate = null) {
    const updateUrl = `${import.meta.env.VITE_API_URL}/${type}/${id}`;
    const token = getToken();

    const payloadToSend = { ...payload };
    if (updatedDate) {
        payloadToSend.updated_at = updatedDate;
    }

    let response;
    try {
        response = await fetchWithTimeout(updateUrl, {
            method: "PATCH",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify(payloadToSend),
        });
    } catch (err) {
        if (isBackendUnavailableError(err)) {
            redirectToConnectionError();
        }
        throw err;
    }

    if (!response.ok) {
        const message = await getErrorMessage(response, `Failed to update ${type}`);
        throw new Error(message);
    }

    return response.json();
}

export async function updateResourceRoles(type, id, roleIds = []) {
    const updateRolesUrl = `${import.meta.env.VITE_API_URL}/${type}/${id}/roles`;
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
        const message = await getErrorMessage(response, `Failed to update roles for ${type}`);
        throw new Error(message);
    }

    return response.json();
}

export async function deleteResource(type, id, cascade = true) {
    const query = cascade ? "?cascade=true" : "";
    const deleteUrl = `${import.meta.env.VITE_API_URL}/${type}/${id}${query}`;
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
        const message = await getErrorMessage(response, `Failed to delete ${type} with ID ${id}`);
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
        const message = await getErrorMessage(response, `Failed to delete file ${fileId}`);
        throw new Error(message);
    }
}

export function parseResourcesForCards(type, data) {
    if (!Array.isArray(data) || data.length === 0) return [];
    return data.map((item) => toResourceCardModel(type, item));
}

export function parseResourcesText(type, data) {
    return toResourceDisplayModel(type, data);
}

export { isTimeoutError, isBackendUnavailableError };