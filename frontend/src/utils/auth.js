import jwtDecode from "jwt-decode";

export function getAccessToken() {
  return localStorage.getItem("access_token");
}

export function isAuthenticated() {
  const token = getAccessToken();
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