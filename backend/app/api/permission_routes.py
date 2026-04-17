from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.utils.check_roles import AccessChecker, assert_admin
from app.domain.exceptions import UnauthorizedError
from app.middleware import schema_validator
from app.schemas.permission_schema import PermissionRefreshTokenUpdateRequest
from app.services.permission_service import PermissionService


permission_bp = Blueprint("permission", __name__, url_prefix="/permissions")


@permission_bp.post("/update-refresh-token")
@jwt_required()
@schema_validator(PermissionRefreshTokenUpdateRequest)
def update_refresh_token():
    assert_admin("El usuario no tiene permiso para actualizar el refresh token")

    user_email = get_jwt_identity()
    payload = request.validated_data.model_dump()
    new_refresh_token = payload["refresh_token"]

    permission_service = PermissionService(current_app)
    permission_service.updateRefreshToken(new_refresh_token)
    is_valid = permission_service.isRefreshTokenValid()

    current_app.logger.info(
        f"Refresh token actualizado por {user_email}. Validez inicial: {is_valid}"
    )

    return jsonify(
        {
            "updated": True,
            "is_valid": is_valid,
            "message": "Refresh token actualizado en configuración de la aplicación",
        }
    ), 200