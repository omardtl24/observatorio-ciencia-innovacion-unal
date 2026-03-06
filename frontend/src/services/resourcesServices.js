import { getToken } from "./authService";
import { toResourceCardModel, toResourceDisplayModel } from "./resourceModels";

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
        response = await fetch(url, {
            credentials: "include",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
    } catch (err) {
        redirectToConnectionError();
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
        response = await fetch(urlObj.toString(), {
            credentials: "include",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
    } catch (err) {
        redirectToConnectionError();
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
    const fetch_url = `${import.meta.env.VITE_API_URL}/${type}/all`;
    const token = getToken();
    let response;
    try {
        response = await fetch(fetch_url, {
            credentials: "include",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
    } catch (err) {
        redirectToConnectionError();
        throw err;
    }
    if (!response.ok) {
        const message = await getErrorMessage(response, `Failed to fetch ${type} resources`);
        throw new Error(message);
    }
    return response.json();
}


export async function fetchResource(type, id) {
    const fetch_url = `${import.meta.env.VITE_API_URL}/${type}/${id}`;
    const token = getToken();
    let response;
    try {
        response = await fetch(fetch_url, {
            credentials: "include",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
    } catch (err) {
        redirectToConnectionError();
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