import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    backend_base_url: str = os.getenv("BACKEND_BASE_URL", "http://backend:5000").rstrip("/")
    shiny_http_base_url: str = os.getenv("SHINY_HTTP_BASE_URL", "http://shinyserver:3838").rstrip("/")
    shiny_ws_base_url: str = os.getenv("SHINY_WS_BASE_URL", "ws://shinyserver:3838").rstrip("/")
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "60"))
    connect_timeout_seconds: float = float(os.getenv("CONNECT_TIMEOUT_SECONDS", "10"))
