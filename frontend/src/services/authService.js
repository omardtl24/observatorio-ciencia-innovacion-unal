const TOKEN_KEY = "access_token";
import {jwtDecode} from "jwt-decode";

export function saveTokensFromUrlParams(params) {
  const token = params.get("access_token");
  if (!token) return false;

  for (const [key, value] of params.entries()) {
    localStorage.setItem(key, value);
  }

  return true;
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
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
  localStorage.clear();
  window.location.href = "/login?error=session_expired";
}

export function logout() {
  localStorage.clear();
  window.location.href = "/login";
}



