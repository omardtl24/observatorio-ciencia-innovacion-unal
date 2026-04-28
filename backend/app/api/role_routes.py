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
from app.services.relations.role_report_relation import RoleReportRelation
from app.services.relations.role_simulator_relation import RoleSimulatorRelation
from app.services.relations.role_visor_relation import RoleVisorRelation
from app.services.relations.role_data_source_relation import RoleDataSourceRelation
from app.services.relations.document_presentation_role_relation import DocumentPresentationRoleRelation


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
    roles = RoleService.get_all_dict(include=["id", "name", "description"])
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


@role_bp.post("")
@jwt_required()
def create_role():
    assert_admin("El usuario no tiene permiso para crear roles")

    data = request.get_json()
    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify({"error": "El nombre del rol es obligatorio"}), 400

    new_role = RoleService.create(name=name, description=description)
    return jsonify(new_role.to_dict()), 201


@role_bp.patch("/<int:role_id>")
@jwt_required()
def update_role(role_id):
    assert_admin("El usuario no tiene permiso para actualizar roles")

    data = request.get_json()
    name = data.get("name")
    description = data.get("description")

    updated_role = RoleService.update(role_id, name=name, description=description)
    return jsonify(updated_role.to_dict()), 200



@role_bp.delete("/<int:role_id>")
@jwt_required()
def delete_role(role_id):
    assert_admin("El usuario no tiene permiso para eliminar roles")

    cascade = request.args.get("cascade", "false").lower() == "true"

    if cascade:
        RoleReportRelation.remove_all_b_for_a(role_id)
        RoleSimulatorRelation.remove_all_b_for_a(role_id)
        RoleVisorRelation.remove_all_b_for_a(role_id)
        RoleDataSourceRelation.remove_all_b_for_a(role_id)
        DocumentPresentationRoleRelation.remove_all_a_for_b(role_id)
        UserRoleRelation.remove_all_a_for_b(role_id)

    RoleService.delete(role_id)
    return "", 204

