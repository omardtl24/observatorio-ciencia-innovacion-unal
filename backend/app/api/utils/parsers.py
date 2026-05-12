"""Parser utilities for extracting and validating request data."""

from flask import request # type: ignore
from app.domain.exceptions import SchemaValidationError
from app.api.utils.check_roles import AccessChecker

VALID_RESOURCE_TYPES = {"report", "visor", "document", "simulator", "data_source"}


def parse_role_assignment_payload():
    """Parse and validate role assignment request payload.
    
    Expects JSON body with user_email and role_id.
    
    Returns:
        tuple: (user_email, role_id) after validation.
    
    Raises:
        SchemaValidationError: If validation fails.
    """
    payload = request.get_json(silent=True) or {}
    user_email = payload.get("user_email")
    role_id = payload.get("role_id")

    if not isinstance(user_email, str) or not user_email.strip():
        raise SchemaValidationError("El campo user_email es obligatorio")

    try:
        parsed_role_id = int(role_id)
    except (TypeError, ValueError):
        raise SchemaValidationError("El campo role_id debe ser un numero entero")

    return user_email.strip(), parsed_role_id


def parse_resource_access_validation_params():
    """Parse and validate resource access validation query parameters.
    
    Expects query parameters: id (int) and resourceType (str).
    
    Returns:
        tuple: (resource_id, normalized_resource_type) after validation.
    
    Raises:
        SchemaValidationError: If validation fails.
    """
    resource_id = request.args.get("id")
    resource_type = request.args.get("resourceType")

    if resource_id is None or resource_type is None:
        raise SchemaValidationError("Los parámetros id y resourceType son obligatorios")

    try:
        parsed_resource_id = int(resource_id)
    except (TypeError, ValueError):
        raise SchemaValidationError("El parámetro id debe ser un número entero")

    normalized_resource_type = AccessChecker._normalize_resource_type(resource_type)
    if normalized_resource_type not in VALID_RESOURCE_TYPES:
        raise SchemaValidationError(
            "El tipo de recurso no es válido. Usa report, visor, document, simulator o data_source"
        )

    return parsed_resource_id, normalized_resource_type
