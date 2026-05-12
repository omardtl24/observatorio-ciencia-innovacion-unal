from flask import Blueprint, current_app # type: ignore
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore
from app.api.utils.check_roles import AccessChecker
from app.domain.exceptions import UnauthorizedError


access_bp = Blueprint("access", __name__, url_prefix="/access")


@access_bp.get("/simulator/<int:simulator_id>/")
@jwt_required()
def check_simulator_access(simulator_id):
    user_email = get_jwt_identity()
    
    has_access = AccessChecker.check_access(user_email, simulator_id, "simulator")
    current_app.logger.info(f"Checking access for user {user_email} to simulator {simulator_id} --> {has_access}")
    if not has_access:
        raise UnauthorizedError("El usuario no tiene permiso para acceder a este simulador")

    return "", 200


@access_bp.get("/visor/<int:visor_id>/")
@jwt_required()
def check_visor_access(visor_id):
    user_email = get_jwt_identity()
    has_access = AccessChecker.check_access(user_email, visor_id, "visor")
    current_app.logger.info(f"Checking access for user {user_email} to visor {visor_id} --> {has_access}")
    if not has_access:
        raise UnauthorizedError("El usuario no tiene permiso para acceder a este visor")

    return "", 200
