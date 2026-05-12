from __future__ import annotations

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.auth import AuthError
from app.config import Settings
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    timeout = httpx.Timeout(
        timeout=settings.request_timeout_seconds,
        connect=settings.connect_timeout_seconds,
    )

    app.state.settings = settings
    app.state.backend_client = httpx.AsyncClient(
        base_url=settings.backend_base_url,
        timeout=timeout,
    )
    app.state.shiny_client = httpx.AsyncClient(timeout=timeout)

    try:
        yield
    finally:
        await app.state.backend_client.aclose()
        await app.state.shiny_client.aclose()


app = FastAPI(title="Shiny Gateway", version="1.0.0", lifespan=lifespan)


@app.exception_handler(AuthError)
async def auth_error_handler(_: Request, exc: AuthError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/healthz")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(router)
