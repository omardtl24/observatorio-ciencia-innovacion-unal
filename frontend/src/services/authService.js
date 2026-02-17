const TOKEN_KEY = "access_token";
import {jwtDecode} from "jwt-decode";
import { setCookie, getCookie, deleteCookie } from "./cookiesManager";

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
  deleteCookie(TOKEN_KEY);
  window.location.href = "/login?error=session_expired";
}

export function logout() {
  deleteCookie(TOKEN_KEY);
  window.location.href = "/login";
}

export function startLogin() {
  window.location.href = `${import.meta.env.VITE_API_URL}/auth/login`;
}



