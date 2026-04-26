from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.utils.check_roles import AccessChecker


resource_bp = Blueprint("resource", __name__, url_prefix="/resource")
_ALLOWED_RESOURCE_TYPES = {"simulator", "visor"}


@resource_bp.get("/<int:resource_id>")
@jwt_required()
def validate_resource_access(resource_id):
    resource_type = (request.args.get("resourceType") or "").strip().lower()
    if resource_type not in _ALLOWED_RESOURCE_TYPES:
        return "", 403

    user_email = get_jwt_identity()
    has_access = AccessChecker.check_access(user_email, resource_id, resource_type)
    if not has_access:
        return "", 403

    return "", 200
