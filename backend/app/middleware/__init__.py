"""Middleware for Flask application."""
from app.middleware.schema_validator import schema_validator

__all__ = ["schema_validator"]
