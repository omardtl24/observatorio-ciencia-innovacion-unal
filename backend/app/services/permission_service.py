from datetime import datetime, timedelta

import requests
from flask import current_app # type: ignore

from app.domain.exceptions import IllegalOperationError, UnauthorizedError


class PermissionService:
    """Service for managing Looker Studio asset permissions."""

    LOOKER_API_BASE = "https://datastudio.googleapis.com/v1"
    TOKEN_URL = "https://oauth2.googleapis.com/token"

    def __init__(self, app=None):
        self.app = app or current_app
        self._access_token = None
        self._access_token_expires_at = None

    def _is_access_token_cached_and_valid(self):
        return (
            self._access_token
            and self._access_token_expires_at
            and datetime.utcnow() < self._access_token_expires_at
        )

    def _safe_response_data(self, response):
        try:
            return response.json()
        except Exception:
            return response.text

    def _refresh_access_token(self, force=False):
        if not force and self._is_access_token_cached_and_valid():
            return self._access_token

        refresh_token = self.app.config.get("REFRESH_TOKEN")
        client_id = self.app.config.get("CLIENT_ID")
        client_secret = self.app.config.get("CLIENT_SECRET")

        if not refresh_token:
            raise UnauthorizedError("REFRESH_TOKEN no configurado")
        if not client_id or not client_secret:
            raise IllegalOperationError("CLIENT_ID o CLIENT_SECRET no configurado")

        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        try:
            response = requests.post(self.TOKEN_URL, data=payload, timeout=20)
        except requests.RequestException as exc:
            self.app.logger.error(f"Error de red al refrescar access token: {str(exc)}")
            raise IllegalOperationError("No fue posible refrescar el access token") from exc

        response_data = self._safe_response_data(response)
        if response.status_code >= 400:
            self.app.logger.error(
                f"Error al refrescar token ({response.status_code}): {response_data}"
            )
            raise UnauthorizedError("Refresh token inválido o expirado")

        access_token = response_data.get("access_token") if isinstance(response_data, dict) else None
        if not access_token:
            self.app.logger.error(f"Respuesta sin access_token: {response_data}")
            raise IllegalOperationError("La respuesta de token no incluyó access_token")

        expires_in = int(response_data.get("expires_in", 3600))
        self._access_token = access_token
        self._access_token_expires_at = datetime.utcnow() + timedelta(seconds=max(expires_in - 60, 60))

        rotated_refresh_token = response_data.get("refresh_token") if isinstance(response_data, dict) else None
        if rotated_refresh_token:
            self.app.config["REFRESH_TOKEN"] = rotated_refresh_token
            self.app.logger.info("Refresh token rotado y actualizado en app config")

        return self._access_token

    def _request_with_auto_refresh(self, method, url, **kwargs):
        access_token = self._refresh_access_token()
        headers = kwargs.pop("headers", {})
        headers = {
            **headers,
            "Authorization": f"Bearer {access_token}",
        }

        try:
            response = requests.request(method, url, headers=headers, timeout=20, **kwargs)
        except requests.RequestException as exc:
            self.app.logger.error(f"Error llamando API de Looker Studio: {str(exc)}")
            raise IllegalOperationError("No fue posible comunicarse con la API de Looker Studio") from exc

        if response.status_code == 401:
            access_token = self._refresh_access_token(force=True)
            retry_headers = {
                **headers,
                "Authorization": f"Bearer {access_token}",
            }
            response = requests.request(method, url, headers=retry_headers, timeout=20, **kwargs)

        return response

    def getPermissions(self, asset_id):
        url = f"{self.LOOKER_API_BASE}/assets/{asset_id}/permissions"
        response = self._request_with_auto_refresh("GET", url)
        data = self._safe_response_data(response)
        if response.status_code >= 400:
            self.app.logger.error(f"Error getPermissions ({response.status_code}): {data}")
        return data

    def addViewers(self, asset_id, emails: list):
        url = f"{self.LOOKER_API_BASE}/assets/{asset_id}/permissions:addMembers"
        params = {"role": "VIEWER", "members": [f"user:{email}" for email in emails]}
        response = self._request_with_auto_refresh("POST", url, params=params)
        data = self._safe_response_data(response)
        if response.status_code >= 400:
            self.app.logger.error(f"Error addViewers ({response.status_code}): {data}")
        return data

    def addEditors(self, asset_id, emails: list):
        url = f"{self.LOOKER_API_BASE}/assets/{asset_id}/permissions:addMembers"
        params = {
            "role": "EDITOR",
            "members": [f"serviceAccount:{email}" for email in emails],
        }
        response = self._request_with_auto_refresh("POST", url, params=params)
        data = self._safe_response_data(response)
        if response.status_code >= 400:
            self.app.logger.error(f"Error addEditors ({response.status_code}): {data}")
        return data

    def removeViewers(self, asset_id, emails: list):
        url = f"{self.LOOKER_API_BASE}/assets/{asset_id}/permissions:revokeAllPermissions"
        params = {"members": [f"user:{email}" for email in emails]}
        response = self._request_with_auto_refresh("POST", url, params=params)
        data = self._safe_response_data(response)
        if response.status_code >= 400:
            self.app.logger.error(f"Error removeViewers ({response.status_code}): {data}")
        return data

    def applyRolePermissions(self, asset_id, role, emails: list):
        """Apply role-based permission changes internally from backend logic."""
        normalized_role = (role or "").upper().strip()
        if normalized_role == "VIEWER":
            return self.addViewers(asset_id, emails)
        if normalized_role == "EDITOR":
            return self.addEditors(asset_id, emails)
        if normalized_role == "REMOVE_VIEWER":
            return self.removeViewers(asset_id, emails)
        raise IllegalOperationError(f"Rol no soportado para permisos: {role}")

    def updateRefreshToken(self, new_token):
        if not isinstance(new_token, str) or not new_token.strip():
            raise IllegalOperationError("new_token debe ser un string no vacío")

        self.app.config["REFRESH_TOKEN"] = new_token.strip()
        self._access_token = None
        self._access_token_expires_at = None
        self.app.logger.info("Refresh token actualizado en app config")
        return True

    def isRefreshTokenValid(self):
        try:
            self._refresh_access_token(force=True)
            return True
        except Exception as exc:
            self.app.logger.warning(f"Refresh token inválido: {str(exc)}")
            return False