export function setCookie(name, value, options = {}) {
  const defaults = { path: '/', maxAge: 7 * 24 * 60 * 60 };
  const settings = { ...defaults, ...options };

  let cookieString = `${name}=${encodeURIComponent(value)}`;

  if (settings.maxAge !== undefined) {
    cookieString += `; max-age=${settings.maxAge}`;
  }
  if (settings.path) {
    cookieString += `; path=${settings.path}`;
  }
  if (settings.sameSite) {
    cookieString += `; SameSite=${settings.sameSite}`;
  }
  if (settings.secure) {
    cookieString += `; Secure`;
  }

  document.cookie = cookieString;
}

export function getCookie(name) {
  const nameEQ = name + "=";
  const cookies = document.cookie.split(';');
  
  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith(nameEQ)) {
      return decodeURIComponent(cookie.substring(nameEQ.length));
    }
  }
  return null;
}

export function deleteCookie(name) {
  // Ensure we remove cookie using same default path and no value
  setCookie(name, "", { maxAge: 0 });
}
