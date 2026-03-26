from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.utils.check_roles import AccessChecker
from app.domain.exceptions import IllegalOperationError, SchemaValidationError, UnauthorizedError
from app.services.role_service import RoleService
from app.services.user_service import UserService
from app.services.relations.user_role_relation import UserRoleRelation


role_bp = Blueprint("role", __name__, url_prefix="/role")


def _assert_admin():
    user_email = get_jwt_identity()
    if not AccessChecker.is_admin(user_email):
        raise UnauthorizedError("El usuario no tiene permiso para gestionar roles")


def _parse_role_assignment_payload():
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


def _serialize_user(user):
    return {
        "email": user.email,
        "names": user.names,
        "last_names": user.last_names,
        "roles": [
            {
                "id": role.id,
                "name": role.name,
            }
            for role in getattr(user, "roles", [])
        ],
    }


@role_bp.get("/all")
@jwt_required()
def get_roles():
    _assert_admin()

    exclude_admin = request.args.get("exclude_admin", "false").lower() == "true"
    roles = RoleService.get_all_dict(include=["id", "name"])

    if exclude_admin:
        roles = [role for role in roles if role.get("name") != "Administrador"]

    return jsonify(roles), 200


@role_bp.get("/management-data")
@jwt_required()
def get_role_management_data():
    _assert_admin()

    exclude_admin = request.args.get("exclude_admin", "true").lower() == "true"
    roles = RoleService.get_all_dict(include=["id", "name"])
    if exclude_admin:
        roles = [role for role in roles if role.get("name") != "Administrador"]

    users = UserService.get_all()
    users_payload = [_serialize_user(user) for user in users]

    return jsonify({
        "roles": roles,
        "users": users_payload,
    }), 200


@role_bp.post("/assign")
@jwt_required()
def assign_role_to_user():
    _assert_admin()

    user_email, role_id = _parse_role_assignment_payload()
    user = UserRoleRelation.get_user_by_email(user_email)
    RoleService.get_by_id(role_id)

    if any(role.id == role_id for role in getattr(user, "roles", [])):
        raise IllegalOperationError("El usuario ya tiene el rol seleccionado")

    UserRoleRelation.add_role_to_user(user_email, role_id)

    user = UserRoleRelation.get_user_by_email(user_email)
    return jsonify(_serialize_user(user)), 200


@role_bp.post("/remove")
@jwt_required()
def remove_role_from_user():
    _assert_admin()

    user_email, role_id = _parse_role_assignment_payload()
    user = UserRoleRelation.get_user_by_email(user_email)
    RoleService.get_by_id(role_id)

    if not any(role.id == role_id for role in getattr(user, "roles", [])):
        raise IllegalOperationError("El usuario no tiene el rol seleccionado")

    UserRoleRelation.remove_role_from_user(user_email, role_id)

    user = UserRoleRelation.get_user_by_email(user_email)
    return jsonify(_serialize_user(user)), 200
