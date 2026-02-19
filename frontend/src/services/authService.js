import { jwtDecode } from "jwt-decode";
import { setCookie, getCookie, deleteCookie } from "./cookiesManager";
import { setItem, getItem, removeItem } from "./localStorageManager";

const TOKEN_KEY = "access_token";
const POPUP_WIDTH = 500;
const POPUP_HEIGHT = 600;

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
      reject(new Error("Failed to open authentication popup. Please allow popups in your browser."));
      return;
    }
    
    // Handler for messages from the popup
    const messageHandler = (event) => {
      console.log("Received postMessage from origin:", event.origin);
      console.log("Received postMessage data:", event.data);
      
      // Validate origin for security
      const expectedOrigin = new URL(apiUrl).origin;
      console.log("Expected origin:", expectedOrigin);
      
      if (event.origin !== expectedOrigin) {
        console.warn("Message received from untrusted origin. Expected:", expectedOrigin, "Got:", event.origin);
        return;
      }
      
      if (event.data.status === "ok") {
        // Authentication successful
        window.removeEventListener("message", messageHandler);
        
        // Store profile picture in localStorage if provided
        if (event.data.picture) {
          console.log("Storing profile picture in localStorage:", event.data.picture);
          setItem("pp", event.data.picture);
          console.log("localStorage 'pp' set successfully");
        } else {
          console.warn("No picture provided in postMessage");
        }
        
        resolve();
      } else if (event.data.status === "error") {
        // Authentication failed
        window.removeEventListener("message", messageHandler);
        reject(new Error(event.data.message || "Authentication failed"));
      }
    };
    
    // Listen for postMessage from the popup
    window.addEventListener("message", messageHandler);
    
    // Timeout after 10 minutes
    const timeout = setTimeout(() => {
      window.removeEventListener("message", messageHandler);
      popup.close();
      reject(new Error("Authentication timeout"));
    }, 600000);
    
    // Clean up timeout if authentication completes
    const originalResolve = resolve;
    resolve = () => {
      clearTimeout(timeout);
      originalResolve();
    };
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
        throw new Error("Not authenticated. Please log in.");
      }
      throw new Error(`Failed to retrieve access token: ${response.statusText}`);
    }
    
    const data = await response.json();
    if (!data.access_token) {
      throw new Error("No access token in response");
    }
    
    // Store token in memory only (never in URLs)
    localStorage.setItem(TOKEN_KEY, data.access_token);
    
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
  removeItem("pp"); // Delete profile picture from localStorage
  window.location.href = "/login?error=session_expired";
}

export function logout(origin = null, navigate = null) {
  localStorage.removeItem(TOKEN_KEY);
  deleteCookie(TOKEN_KEY);
  removeItem("pp"); // Delete profile picture from localStorage
  
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
    
    // Get profile picture from localStorage
    const picture = getItem("pp") || "";
    console.log("getUserInfo - Retrieved picture from localStorage:", picture);
    
    return {
      email: decoded.sub,
      names: decoded.names || "",
      lastNames: decoded.last_names || "",
      picture: picture,
      expiresAt: decoded.exp * 1000 // Convert to milliseconds
    };
  } catch (e) {
    console.error("Error decoding token:", e);
    return null;
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
 */
export function redirectToLogin(navigate, customOrigin = null) {
  const origin = customOrigin || window.location.pathname;
  const encodedOrigin = encodeURIComponent(origin);
  navigate(`/login?origin=${encodedOrigin}`);
}

/**
 * Redirect to login for non-component contexts (fallback).
 * Prefer redirectToLogin(navigate) when in a React component.
 * 
 * @param {string} customOrigin - Optional custom origin to redirect to after login
 */
export function redirectToLoginFallback(customOrigin = null) {
  const origin = customOrigin || window.location.pathname;
  const encodedOrigin = encodeURIComponent(origin);
  window.location.href = `/login?origin=${encodedOrigin}`;
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
    const response = await fetch(`${apiUrl}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('API is not responding correctly');
    }
    
    // Open authentication popup
    await openAuthPopup();
    
    // Retrieve access token from backend
    const result = await getAccessToken();
    
    // Redirect to origin after successful authentication
    window.location.href = result.redirectTo;
  } catch (error) {
    console.error("Login error:", error);
    if (error.message.includes("popup")) {
      window.location.href = `/login?error=popup_blocked&message=${encodeURIComponent(error.message)}`;
    } else if (error.message.includes("timeout")) {
      window.location.href = `/login?error=timeout&message=${encodeURIComponent("Authentication took too long")}`;
    } else {
      const origin = encodeURIComponent(window.location.pathname);
      window.location.href = `/connection-error?origin=${origin}`;
    }
  }
}



