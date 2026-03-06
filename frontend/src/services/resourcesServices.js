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
    } catch (err) {
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

export function parseResourcesForCards(type, data) {
    if (!Array.isArray(data) || data.length === 0) return [];
    return data.map((item) => toResourceCardModel(type, item));
}

export function parseResourcesText(type, data) {
    return toResourceDisplayModel(type, data);
}

export { isTimeoutError, isBackendUnavailableError };