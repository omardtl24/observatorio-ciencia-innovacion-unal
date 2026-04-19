from flask import current_app


def build_resource_url(resource_type: str, resource_id: int) -> str:
    """Build a frontend resource URL using app config when available."""
    resource_path = f"/resource/{resource_type}/{resource_id}"
    frontend_url = (current_app.config.get("FRONTEND_URL") or "").strip()
    if not frontend_url:
        return resource_path
    return f"{frontend_url.rstrip('/')}{resource_path}"
