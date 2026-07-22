let navigateFunction = null;

export function setNavigate(navigate) {
  navigateFunction = navigate;
}

export function navigateTo(path, options = {}) {
  if (navigateFunction) {
    navigateFunction(path, options);
  } else {
    console.warn("Navigation not initialized");
  }
}