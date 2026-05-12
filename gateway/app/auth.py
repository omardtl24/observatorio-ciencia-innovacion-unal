from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus
from typing import Mapping

import httpx


class AuthError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


@dataclass
class AuthService:
    backend_client: httpx.AsyncClient

    def extract_user_jwt(self, cookies: Mapping[str, str]) -> str:
        token = cookies.get("user_jwt")
        if not token:
            raise AuthError(HTTPStatus.UNAUTHORIZED, "Missing user_jwt cookie")
        return token

    async def validate_access(self, token: str, resource_type: str, resource_id: int) -> None:
        endpoint = f"/access/{resource_type}/{resource_id}/"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = await self.backend_client.get(endpoint, headers=headers)
        except httpx.RequestError as exc:
            raise AuthError(HTTPStatus.FORBIDDEN, "Authorization backend unavailable") from exc

        if response.status_code == HTTPStatus.OK:
            return

        if response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
            raise AuthError(response.status_code, "Access denied")

        # Deny by default on any unexpected response.
        raise AuthError(HTTPStatus.FORBIDDEN, "Access denied")
