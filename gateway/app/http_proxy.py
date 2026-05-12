from __future__ import annotations

from urllib.parse import urlencode

import httpx
from fastapi import Request
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}


def _filter_headers(headers: httpx.Headers | dict[str, str], *, strip_host: bool = False) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in headers.items():
        key_lower = key.lower()
        if key_lower in HOP_BY_HOP_HEADERS:
            continue
        if strip_host and key_lower in {"host", "content-length"}:
            continue
        result[key] = value
    return result


def _build_http_upstream_url(base_url: str, resource_type: str, resource_id: int, subpath: str) -> str:
    normalized = f"{resource_type}/{resource_id}/"
    if subpath:
        normalized = f"{normalized}{subpath.lstrip('/')}"
    return f"{base_url}/{normalized}"


async def proxy_http_request(
    request: Request,
    *,
    shiny_http_client: httpx.AsyncClient,
    shiny_http_base_url: str,
    resource_type: str,
    resource_id: int,
    subpath: str = "",
) -> StreamingResponse:
    upstream_url = _build_http_upstream_url(shiny_http_base_url, resource_type, resource_id, subpath)
    query_string = urlencode(list(request.query_params.multi_items()), doseq=True)
    target_url = f"{upstream_url}?{query_string}" if query_string else upstream_url

    upstream_request = shiny_http_client.build_request(
        method=request.method,
        url=target_url,
        headers=_filter_headers(request.headers, strip_host=True),
        content=request.stream(),
    )

    upstream_response = await shiny_http_client.send(upstream_request, stream=True)
    filtered_response_headers = _filter_headers(upstream_response.headers)

    return StreamingResponse(
        upstream_response.aiter_raw(),
        status_code=upstream_response.status_code,
        headers=filtered_response_headers,
        background=BackgroundTask(upstream_response.aclose),
    )
