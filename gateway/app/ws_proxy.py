from __future__ import annotations

import asyncio
from urllib.parse import urlencode

from fastapi import WebSocket
from websockets.client import connect as ws_connect
from websockets.exceptions import ConnectionClosed


async def _relay_client_to_upstream(client_ws: WebSocket, upstream_ws) -> None:
    while True:
        message = await client_ws.receive()
        message_type = message.get("type")

        if message_type == "websocket.disconnect":
            return

        text_data = message.get("text")
        bytes_data = message.get("bytes")

        if text_data is not None:
            await upstream_ws.send(text_data)
        elif bytes_data is not None:
            await upstream_ws.send(bytes_data)


async def _relay_upstream_to_client(client_ws: WebSocket, upstream_ws) -> None:
    try:
        async for message in upstream_ws:
            if isinstance(message, bytes):
                await client_ws.send_bytes(message)
            else:
                await client_ws.send_text(message)
    except ConnectionClosed:
        return


def _build_ws_upstream_url(base_url: str, resource_type: str, resource_id: int, subpath: str, raw_query: str) -> str:
    normalized = f"{resource_type}/{resource_id}/"
    if subpath:
        normalized = f"{normalized}{subpath.lstrip('/')}"
    upstream_url = f"{base_url}/{normalized}"
    if raw_query:
        return f"{upstream_url}?{raw_query}"
    return upstream_url


async def proxy_websocket(
    websocket: WebSocket,
    *,
    shiny_ws_base_url: str,
    resource_type: str,
    resource_id: int,
    subpath: str = "",
) -> None:
    query_string = urlencode(list(websocket.query_params.multi_items()), doseq=True)
    upstream_url = _build_ws_upstream_url(
        shiny_ws_base_url,
        resource_type,
        resource_id,
        subpath,
        query_string,
    )

    upstream_headers = {
        key: value
        for key, value in websocket.headers.items()
        if key.lower() not in {"host", "connection", "upgrade", "sec-websocket-key", "sec-websocket-version"}
    }

    async with ws_connect(upstream_url, extra_headers=upstream_headers) as upstream_ws:
        await websocket.accept()

        task_up = asyncio.create_task(_relay_client_to_upstream(websocket, upstream_ws))
        task_down = asyncio.create_task(_relay_upstream_to_client(websocket, upstream_ws))

        done, pending = await asyncio.wait({task_up, task_down}, return_when=asyncio.FIRST_COMPLETED)

        for task in pending:
            task.cancel()

        await asyncio.gather(*pending, return_exceptions=True)
        for task in done:
            _ = task.exception()

        await upstream_ws.close()
