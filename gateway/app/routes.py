from __future__ import annotations

from fastapi import APIRouter, Request, WebSocket
from fastapi.responses import JSONResponse
from websockets.exceptions import InvalidStatusCode

from app.auth import AuthError, AuthService
from app.http_proxy import proxy_http_request
from app.ws_proxy import proxy_websocket

router = APIRouter()
HTTP_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]


def _auth_service(request: Request) -> AuthService:
    return AuthService(backend_client=request.app.state.backend_client)


def _ws_auth_service(websocket: WebSocket) -> AuthService:
    return AuthService(backend_client=websocket.app.state.backend_client)


async def _authorize_http(request: Request, resource_type: str, resource_id: int) -> JSONResponse | None:
    auth = _auth_service(request)
    token = auth.extract_user_jwt(request.cookies)
    await auth.validate_access(token, resource_type, resource_id)
    return None


async def _authorize_ws(websocket: WebSocket, resource_type: str, resource_id: int) -> bool:
    auth = _ws_auth_service(websocket)
    token = auth.extract_user_jwt(websocket.cookies)
    await auth.validate_access(token, resource_type, resource_id)
    return True


@router.api_route("/visor/{resource_id}/", methods=HTTP_METHODS)
@router.api_route("/visor/{resource_id}/{subpath:path}", methods=HTTP_METHODS)
async def visor_http_proxy(request: Request, resource_id: int, subpath: str = ""):
    await _authorize_http(request, "visor", resource_id)
    return await proxy_http_request(
        request,
        shiny_http_client=request.app.state.shiny_client,
        shiny_http_base_url=request.app.state.settings.shiny_http_base_url,
        resource_type="visor",
        resource_id=resource_id,
        subpath=subpath,
    )


@router.api_route("/simulator/{resource_id}/", methods=HTTP_METHODS)
@router.api_route("/simulator/{resource_id}/{subpath:path}", methods=HTTP_METHODS)
async def simulator_http_proxy(request: Request, resource_id: int, subpath: str = ""):
    await _authorize_http(request, "simulator", resource_id)
    return await proxy_http_request(
        request,
        shiny_http_client=request.app.state.shiny_client,
        shiny_http_base_url=request.app.state.settings.shiny_http_base_url,
        resource_type="simulator",
        resource_id=resource_id,
        subpath=subpath,
    )


@router.websocket("/visor/{resource_id}/")
@router.websocket("/visor/{resource_id}/{subpath:path}")
async def visor_ws_proxy(websocket: WebSocket, resource_id: int, subpath: str = "") -> None:
    try:
        await _authorize_ws(websocket, "visor", resource_id)
    except AuthError:
        await websocket.close(code=1008, reason="Access denied")
        return

    try:
        await proxy_websocket(
            websocket,
            shiny_ws_base_url=websocket.app.state.settings.shiny_ws_base_url,
            resource_type="visor",
            resource_id=resource_id,
            subpath=subpath,
        )
    except InvalidStatusCode:
        await websocket.close(code=1011, reason="Upstream WebSocket unavailable")


@router.websocket("/simulator/{resource_id}/")
@router.websocket("/simulator/{resource_id}/{subpath:path}")
async def simulator_ws_proxy(websocket: WebSocket, resource_id: int, subpath: str = "") -> None:
    try:
        await _authorize_ws(websocket, "simulator", resource_id)
    except AuthError:
        await websocket.close(code=1008, reason="Access denied")
        return

    try:
        await proxy_websocket(
            websocket,
            shiny_ws_base_url=websocket.app.state.settings.shiny_ws_base_url,
            resource_type="simulator",
            resource_id=resource_id,
            subpath=subpath,
        )
    except InvalidStatusCode:
        await websocket.close(code=1011, reason="Upstream WebSocket unavailable")
