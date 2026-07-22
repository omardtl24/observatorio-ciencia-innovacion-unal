import { jwtDecode } from "jwt-decode";
import { setCookie, getCookie, deleteCookie } from "./cookiesManager";
import { navigateTo } from "../navigation";


const TOKEN_KEY = "access_token";
const IMAGE_ID_KEY = "profile_image_id";
const ROLES_KEY = "user_roles";
const POPUP_WIDTH = 500;
const POPUP_HEIGHT = 600;
const REQUEST_TIMEOUT_MS = Number(import.meta.env.VITE_REQUEST_TIMEOUT_MS || 10000);
const PROFILE_IMAGE_CACHE_NAME = "profile-image-blobs-v1";
const profileImageBlobCache = new Map();
const profileImagePendingRequests = new Map();

function createTimeoutError(timeoutMs) {
  const error = new Error(`La solicitud tardó demasiado (${timeoutMs} ms)`);
  error.name = "TimeoutError";
  return error;
}

function isBackendUnavailableError(err) {
  if (err?.name === "TimeoutError") {
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

function profileImageCacheRequest(imageId) {
  const cacheUrl = `${window.location.origin}/__profile_image_cache__/${imageId}`;
  return new Request(cacheUrl, { method: "GET" });
}

async function readProfileImageFromPersistentCache(imageId) {
  if (!("caches" in window)) {
    return null;
  }

  const cache = await caches.open(PROFILE_IMAGE_CACHE_NAME);
  const cachedResponse = await cache.match(profileImageCacheRequest(imageId));
  if (!cachedResponse) {
    return null;
  }

  const blob = await cachedResponse.blob();
  const blobUrl = URL.createObjectURL(blob);
  profileImageBlobCache.set(imageId, blobUrl);
  return blobUrl;
}

async function writeProfileImageToPersistentCache(imageId, response) {
  if (!("caches" in window)) {
    return;
  }

  const cache = await caches.open(PROFILE_IMAGE_CACHE_NAME);
  await cache.put(profileImageCacheRequest(imageId), response.clone());
}

async function clearPersistentProfileImageCache() {
  if (!("caches" in window)) {
    return;
  }
  await caches.delete(PROFILE_IMAGE_CACHE_NAME);
}

function clearProfileImageBlobCache() {
  for (const blobUrl of profileImageBlobCache.values()) {
    URL.revokeObjectURL(blobUrl);
  }
  profileImageBlobCache.clear();
  profileImagePendingRequests.clear();
  clearPersistentProfileImageCache().catch(() => {});
}

function saveRoles(roles) {
  if (!Array.isArray(roles)) {
    return;
  }
  sessionStorage.setItem(ROLES_KEY, JSON.stringify(roles));
}

function readRoles() {
  const raw = sessionStorage.getItem(ROLES_KEY);
  if (!raw) {
    return [];
  }

  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

/**
 * Open an authentication popup to the backend login endpoint.
 * The popup will handle Auth0 authentication and communicate back via postMessage.
 * This function waits for the login process to complete and resolves when successful.
 * 
 * @returns {Promise} Resolves when authentication is complete
 */
export function openAuthPopup() {
  return new Promise((resolve, reject) => {
    const apiUrl = import.meta.env.VITE_API_URL;
    const left = window.screenX + (window.outerWidth - POPUP_WIDTH) / 2;
    const top = window.screenY + (window.outerHeight - POPUP_HEIGHT) / 2;
    
    const popup = window.open(
      `${apiUrl}/auth/login`,
      "auth_popup",
      `width=${POPUP_WIDTH},height=${POPUP_HEIGHT},left=${left},top=${top},resizable,scrollbars`
    );
    
    if (!popup) {
      reject(new Error("No fue posible abrir la ventana de autenticación. Habilita los popups e intenta nuevamente."));
      return;
    }

    let isSettled = false;
    let timeoutId = null;
    let closedCheckId = null;

    const cleanup = () => {
      window.removeEventListener("message", messageHandler);
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      if (closedCheckId) {
        clearInterval(closedCheckId);
      }
    };

    const settle = (fn, value) => {
      if (isSettled) {
        return;
      }
      isSettled = true;
      if (popup && !popup.closed) {
        popup.close();
      }
      cleanup();
      fn(value);
    };
    
    // Handler for messages from the popup
    const messageHandler = (event) => {
      console.log("Received postMessage from origin:", event.origin);
      console.log("Received postMessage data:", event.data);
      
      // Validate origin for security
      // Support relative `VITE_API_URL` (e.g. "/api") by resolving against current origin
      let expectedOrigin;
      try {
        expectedOrigin = new URL(apiUrl, window.location.origin).origin;
      } catch (e) {
        expectedOrigin = window.location.origin;
      }
      console.log("Expected origin:", expectedOrigin);
      
      if (event.origin !== expectedOrigin) {
        console.warn("Message received from untrusted origin. Expected:", expectedOrigin, "Got:", event.origin);
        return;
      }
      
      if (event.data.status === "ok") {
        if (event.data.image_id) {
          const previousImageId = sessionStorage.getItem(IMAGE_ID_KEY);
          if (previousImageId && previousImageId !== event.data.image_id) {
            clearProfileImageBlobCache();
          }
          sessionStorage.setItem(IMAGE_ID_KEY, event.data.image_id);
        }

        if (Array.isArray(event.data.roles)) {
          saveRoles(event.data.roles);
        }

        settle(resolve);
      } else if (event.data.status === "error") {
        settle(reject, new Error(event.data.message || "No fue posible completar la autenticación"));
      }
    };
    
    // Listen for postMessage from the popup
    window.addEventListener("message", messageHandler);
    
    // Timeout after 10 minutes
    timeoutId = setTimeout(() => {
      if (!popup.closed) {
        popup.close();
      }
      settle(reject, new Error("La autenticación tardó demasiado. Intenta nuevamente."));
    }, 600000);

    // If user closes popup manually, reject immediately so login can be retried.
    closedCheckId = setInterval(() => {
      if (!isSettled && popup.closed) {
        settle(reject, new Error("La ventana de autenticación fue cerrada por el usuario"));
      }
    }, 300);
  });
}

/**
 * Retrieve an access token by making a POST request to /auth/session.
 * This endpoint validates the HttpOnly session cookie and returns a short-lived access token.
 * 
 * @returns {Promise<string>} The access token
 * @throws {Error} If unable to retrieve token
 */
export async function getAccessToken() {
  const apiUrl = import.meta.env.VITE_API_URL;
  
  try {
    const response = await fetch(`${apiUrl}/auth/session`, {
      method: "POST",
      credentials: "include", // Include HttpOnly session cookie
      headers: {
        "Content-Type": "application/json"
      }
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("No hay una sesión activa. Inicia sesión para continuar.");
      }
      throw new Error("No fue posible obtener el token de acceso");
    }
    
    const data = await response.json();
    if (!data.access_token) {
      throw new Error("La respuesta no incluyó un token de acceso");
    }
    
    // Store token in memory only (never in URLs)
    localStorage.setItem(TOKEN_KEY, data.access_token);
    // Also set cookies used by legacy code and iframe proxy
    try {
      setCookie(TOKEN_KEY, data.access_token);
      setCookie("user_jwt", data.access_token, { sameSite: "Lax" });
    } catch (e) {
      // non-fatal: continue even if cookie write fails
      console.warn("No se pudo establecer cookie user_jwt:", e);
    }
    
    // Get the intended destination and clear it
    const origin = sessionStorage.getItem("auth_origin_redirect");
    if (origin) {
      sessionStorage.removeItem("auth_origin_redirect");
      return { token: data.access_token, redirectTo: origin };
    }
    
    return { token: data.access_token, redirectTo: "/" };
  } catch (error) {
    console.error("Error retrieving access token:", error);
    throw error;
  }
}

export function saveTokensFromUrlParams(params) {
  const token = params.get("access_token");
  if (!token) return false;

  setCookie(TOKEN_KEY, token);
  return true;
}

export function saveTokensFromPayload(payload) {
  if (!payload || !payload.access_token) return false;
  setCookie(TOKEN_KEY, payload.access_token);
  // Keep user_jwt in sync for iframe/Nginx proxy
  try {
    setCookie("user_jwt", payload.access_token, { sameSite: "Lax" });
  } catch (e) {
    console.warn("No se pudo establecer cookie user_jwt:", e);
  }
  return true;
}

export function getToken() {
  // Try to get token from localStorage first (in-memory during session)
  let token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    return token;
  }
  
  // Fall back to cookie for backwards compatibility
  return getCookie(TOKEN_KEY);
}

export function isAuthenticated() {
  const token = getToken();
  if (!token) return false;

  try {
    const decoded = jwtDecode(token);

    const now = Date.now() / 1000;
    if (decoded.exp && decoded.exp < now) {
      expired();
      return false;
    }
    return true;
  } catch (e) {
    expired();
    return false;
  }
}

export function expired() {
  localStorage.removeItem(TOKEN_KEY);
  deleteCookie(TOKEN_KEY);
  // Remove proxy cookie used by iframe/proxy
  try {
    deleteCookie("user_jwt");
  } catch (e) {
    console.warn("No se pudo eliminar cookie user_jwt:", e);
  }
  sessionStorage.removeItem(IMAGE_ID_KEY);
  sessionStorage.removeItem(ROLES_KEY);
  clearProfileImageBlobCache();
  navigateTo("/login?error=session_expired", {
        replace: true,
    });
}

export function logout(origin = null, navigate = null) {
  localStorage.removeItem(TOKEN_KEY);
  deleteCookie(TOKEN_KEY);
  // Also remove cookie used by iframe proxy
  try {
    deleteCookie("user_jwt");
  } catch (e) {
    console.warn("No se pudo eliminar cookie user_jwt:", e);
  }
  sessionStorage.removeItem(IMAGE_ID_KEY);
  sessionStorage.removeItem(ROLES_KEY);
  clearProfileImageBlobCache();
  
  // Calculate the appropriate destination
  const destination = origin || getLogoutDestination();
  
  // If destination is null, reload the page to reflect logout state
  if (destination === null) {
    window.location.reload();
    return;
  }
  
  // If navigate is provided (from React Router), use SPA navigation
  if (navigate) {
    navigate(destination);
  } else {
    // Fallback for non-component contexts (should rarely happen in iframe)
    window.location.href = destination;
  }
}

export function getUserInfo() {
  const token = getToken();
  if (!token) return null;

  try {
    const decoded = jwtDecode(token);
    
    const imageId = decoded.image_id || sessionStorage.getItem(IMAGE_ID_KEY) || null;
    if (imageId) {
      sessionStorage.setItem(IMAGE_ID_KEY, imageId);
    }
    const roles = Array.isArray(decoded.roles) ? decoded.roles : readRoles();
    if (Array.isArray(decoded.roles)) {
      saveRoles(decoded.roles);
    }
    
    return {
      email: decoded.sub,
      names: decoded.names || "",
      lastNames: decoded.last_names || "",
      imageId,
      roles,
      expiresAt: decoded.exp * 1000 // Convert to milliseconds
    };
  } catch (e) {
    console.error("Error decoding token:", e);
    return null;
  }
}

export async function fetchProfileImage(imageId) {
  const token = getToken();
  if (!token || !imageId) {
    return null;
  }

  if (profileImageBlobCache.has(imageId)) {
    return profileImageBlobCache.get(imageId);
  }

  const persistentBlobUrl = await readProfileImageFromPersistentCache(imageId);
  if (persistentBlobUrl) {
    return persistentBlobUrl;
  }

  if (profileImagePendingRequests.has(imageId)) {
    return profileImagePendingRequests.get(imageId);
  }

  const apiUrl = import.meta.env.VITE_API_URL;
  const pendingRequest = (async () => {
    const response = await fetch(`${apiUrl}/auth/images/${imageId}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.status === 404) {
      return null;
    }

    if (!response.ok) {
      throw new Error("No fue posible cargar la imagen de perfil");
    }

    await writeProfileImageToPersistentCache(imageId, response);

    const blob = await response.blob();
    const blobUrl = URL.createObjectURL(blob);
    profileImageBlobCache.set(imageId, blobUrl);
    return blobUrl;
  })();

  profileImagePendingRequests.set(imageId, pendingRequest);

  try {
    return await pendingRequest;
  } finally {
    profileImagePendingRequests.delete(imageId);
  }
}

export function getTokenExpiresIn() {
  const token = getToken();
  if (!token) return 0;

  try {
    const decoded = jwtDecode(token);
    const expiresAt = decoded.exp * 1000;
    const now = Date.now();
    const expiresIn = Math.max(0, expiresAt - now);
    return expiresIn;
  } catch (e) {
    return 0;
  }
}

/**
 * Redirect to login page with the current page as origin.
 * For use in components - use this version with useNavigate.
 * 
 * @param {Function} navigate - React Router navigate function
 * @param {string} customOrigin - Optional custom origin to redirect to after login
 * @param {string|null} resourceType - Optional resource type context
 */
export function redirectToLogin(navigate, customOrigin = null, resourceType = null) {
  const origin = customOrigin || window.location.pathname;
  const params = new URLSearchParams({ origin });
  if (resourceType) {
    params.set("resourceType", resourceType);
  }
  navigate(`/login?${params.toString()}`);
}

/**
 * Determine the appropriate logout destination based on current page.
 * If on a resource detail page (/resource/type/id), redirect to the resources list (/resources/type).
 * Otherwise, return null to trigger page reload (allows UI to update with session cleared).
 * 
 * @returns {string|null} The path to redirect to, or null to reload current page
 */
export function getLogoutDestination() {
  const pathname = window.location.pathname;
  
  // Check if on a resource detail page: /resource/:type/:id
  const resourceDetailMatch = pathname.match(/^\/resource\/([^\/]+)\/[^\/]+$/);
  if (resourceDetailMatch) {
    const resourceType = resourceDetailMatch[1];
    return `/resources/${resourceType}`;
  }

  // Return null to signal page reload
  return null;
}

/**
 * Start the login flow for an iframe-embedded application.
 * Opens an authentication popup to complete Auth0 login.
 * After successful authentication, retrieves an access token and redirects to origin.
 * 
 * @param {string} origin - The page to redirect to after successful login (defaults to "/")
 */
export async function startLogin(origin = "/") {
  try {
    // Store the origin for redirect after token retrieval
    sessionStorage.setItem("auth_origin_redirect", origin);
    
    // Verify backend is available
    const apiUrl = import.meta.env.VITE_API_URL;
    const response = await fetchWithTimeout(`${apiUrl}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error("El servicio no está respondiendo correctamente");
    }
    
    // Open authentication popup
    await openAuthPopup();
    
    // Retrieve access token from backend
    const result = await getAccessToken();
    
    // Redirect to origin after successful authentication
    navigateTo(result.redirectTo);
  } catch (error) {
    console.error("Login error:", error);
    if (error?.message?.includes("closed by user")) {
      throw error;
    }
    if (error?.message?.includes("popup")) {
      throw new Error("No fue posible abrir la ventana de autenticacion. Habilita los popups e intenta nuevamente.");
    }
    if (isBackendUnavailableError(error)) {
      throw new Error("No fue posible conectar con el servidor. Intenta nuevamente en unos minutos.");
    }
    if (error?.message?.includes("timeout")) {
      throw new Error("La autenticacion tardó demasiado. Intenta nuevamente.");
    }
    throw new Error(error?.message || "No fue posible completar el inicio de sesion.");
  }
}



