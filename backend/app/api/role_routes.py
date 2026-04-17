from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.utils.check_roles import AccessChecker, assert_admin
from app.api.utils.serializers import serialize_user
from app.api.utils.parsers import parse_role_assignment_payload, parse_resource_access_validation_params
from app.api.utils.filters import filter_exclude_admin
from app.domain.exceptions import IllegalOperationError
from app.services.role_service import RoleService
from app.services.user_service import UserService
from app.services.relations.user_role_relation import UserRoleRelation


role_bp = Blueprint("role", __name__, url_prefix="/role")


@role_bp.get("/all")
@jwt_required()
def get_roles():
    assert_admin("El usuario no tiene permiso para gestionar roles")

    exclude_admin = request.args.get("exclude_admin", "false").lower() == "true"
    roles = RoleService.get_all_dict(include=["id", "name"])

    if exclude_admin:
        roles = filter_exclude_admin(roles)

    return jsonify(roles), 200


@role_bp.get("/management-data")
@jwt_required()
def get_role_management_data():
    assert_admin("El usuario no tiene permiso para gestionar roles")

    exclude_admin = request.args.get("exclude_admin", "true").lower() == "true"
    roles = RoleService.get_all_dict(include=["id", "name"])
    if exclude_admin:
        roles = filter_exclude_admin(roles)

    users = UserService.get_all()
    users_payload = [serialize_user(user) for user in users]

    return jsonify({
        "roles": roles,
        "users": users_payload,
    }), 200


@role_bp.post("/assign")
@jwt_required()
def assign_role_to_user():
    assert_admin("El usuario no tiene permiso para gestionar roles")

    user_email, role_id = parse_role_assignment_payload()
    user = UserRoleRelation.get_user_by_email(user_email)
    RoleService.get_by_id(role_id)

    if any(role.id == role_id for role in getattr(user, "roles", [])):
        raise IllegalOperationError("El usuario ya tiene el rol seleccionado")

    UserRoleRelation.add_role_to_user(user_email, role_id)

    user = UserRoleRelation.get_user_by_email(user_email)
    return jsonify(serialize_user(user)), 200


@role_bp.post("/remove")
@jwt_required()
def remove_role_from_user():
    assert_admin("El usuario no tiene permiso para gestionar roles")

    user_email, role_id = parse_role_assignment_payload()
    user = UserRoleRelation.get_user_by_email(user_email)
    RoleService.get_by_id(role_id)

    if not any(role.id == role_id for role in getattr(user, "roles", [])):
        raise IllegalOperationError("El usuario no tiene el rol seleccionado")

    UserRoleRelation.remove_role_from_user(user_email, role_id)

    user = UserRoleRelation.get_user_by_email(user_email)
    return jsonify(serialize_user(user)), 200


@role_bp.get("/validate")
@jwt_required()
def validate_resource_access():
    user_email = get_jwt_identity()
    resource_id, resource_type = parse_resource_access_validation_params()

    has_access = AccessChecker.check_access(user_email, resource_id, resource_type)

    return jsonify(
        {
            "has_access": has_access,
            "resource_id": resource_id,
            "resourceType": resource_type,
        }
    ), 200
