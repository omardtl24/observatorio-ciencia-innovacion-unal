from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.utils.check_roles import AccessChecker
from app.domain.exceptions import SchemaValidationError, UnauthorizedError
from app.middleware import schema_validator
from app.schemas.simulator_schema import SimulatorCreateRequest, SimulatorUpdateRequest
from app.services.relations.role_simulator_relation import RoleSimulatorRelation
from app.services.relations.simulator_data_source_relation import SimulatorDataSourceRelation
from app.services.role_service import RoleService
from app.services.simulator_service import SimulatorService


simulator_bp = Blueprint("simulator", __name__, url_prefix="/simulator")


def _simulator_to_dict_with_roles(simulator):
    payload = simulator.to_dict()
    payload["roles"] = [role.name for role in getattr(simulator, "roles", [])]
    return payload


@simulator_bp.post("")
@jwt_required()
@schema_validator(SimulatorCreateRequest)
def create_simulator():
    user_email = get_jwt_identity()
    if not AccessChecker.is_admin(user_email):
        raise UnauthorizedError("El usuario no tiene permiso para crear simuladores")

    simulator_data = request.validated_data.dict()
    role_ids = simulator_data.pop("role_ids", [])
    selected_role_ids = list({int(role_id) for role_id in role_ids})
    admin_role = RoleService.get_by_name("Administrador")

    for role_id in selected_role_ids:
        RoleService.get_by_id(role_id)

    simulator = SimulatorService.create(**simulator_data)
    simulator = SimulatorService.get_by_id(simulator.id)

    AccessChecker.grant_admin_access(simulator.id, "simulator")
    for role_id in selected_role_ids:
        if role_id != admin_role.id:
            RoleSimulatorRelation.add(role_id, simulator.id)

    simulator = SimulatorService.get_by_id(simulator.id)

    include = ["id", "main_title", "auxiliary_title", "description", "specs_file_id", "updated_at"]
    response = simulator.to_dict(include=include)
    response["roles"] = [role.name for role in getattr(simulator, "roles", [])]
    return jsonify(response), 201


@simulator_bp.get("/all")
def get_simulators():
    full = request.args.get("full") == "true"
    simulators = SimulatorService.get_all()
    if not full:
        payload = []
        for simulator in simulators:
            item = simulator.to_dict(include=["id", "main_title", "auxiliary_title", "updated_at"])
            item["roles"] = [role.name for role in getattr(simulator, "roles", [])]
            payload.append(item)
        return jsonify(payload), 200

    payload = [_simulator_to_dict_with_roles(simulator) for simulator in simulators]
    return jsonify(payload), 200


@simulator_bp.get("/<int:simulator_id>")
@jwt_required()
def get_simulator_by_id(simulator_id):
    user_email = get_jwt_identity()
    if not AccessChecker.check_access(user_email, simulator_id, "simulator"):
        raise UnauthorizedError("El usuario no tiene permiso para acceder a este simulador")

    simulator = SimulatorService.get_by_id(simulator_id)
    response = simulator.to_dict(
        include=["id", "main_title", "auxiliary_title", "description", "specs_file_id", "updated_at"]
    )
    response["roles"] = [role.name for role in getattr(simulator, "roles", [])]
    response["role_ids"] = [role.id for role in getattr(simulator, "roles", [])]
    return jsonify(response), 200


@simulator_bp.patch("/<int:simulator_id>")
@jwt_required()
@schema_validator(SimulatorUpdateRequest)
def update_simulator(simulator_id):
    user_email = get_jwt_identity()
    if not AccessChecker.is_admin(user_email):
        raise UnauthorizedError("El usuario no tiene permiso para actualizar este simulador")

    update_data = request.validated_data.dict(exclude_unset=True)
    if not update_data:
        raise SchemaValidationError("At least one field must be provided")

    simulator = SimulatorService.update(simulator_id, **update_data)

    return jsonify(
        simulator.to_dict(
            include=["id", "main_title", "auxiliary_title", "description", "specs_file_id", "updated_at"]
        )
    ), 200


@simulator_bp.patch("/<int:simulator_id>/roles")
@jwt_required()
def update_simulator_roles(simulator_id):
    user_email = get_jwt_identity()
    if not AccessChecker.is_admin(user_email):
        raise UnauthorizedError("El usuario no tiene permiso para actualizar roles de este simulador")

    payload = request.get_json(silent=True) or {}
    role_ids = payload.get("role_ids")
    if not isinstance(role_ids, list):
        raise SchemaValidationError("role_ids must be a list")

    try:
        selected_role_ids = list({int(role_id) for role_id in role_ids})
    except (TypeError, ValueError):
        raise SchemaValidationError("role_ids must contain valid integers")

    admin_role = RoleService.get_by_name("Administrador")
    for role_id in selected_role_ids:
        RoleService.get_by_id(role_id)

    RoleSimulatorRelation.remove_all_a_for_b(simulator_id)
    AccessChecker.grant_admin_access(simulator_id, "simulator")
    for role_id in selected_role_ids:
        if role_id != admin_role.id:
            RoleSimulatorRelation.add(role_id, simulator_id)

    simulator = SimulatorService.get_by_id(simulator_id)
    response = simulator.to_dict(include=["id", "main_title", "auxiliary_title", "description", "specs_file_id", "updated_at"])
    response["roles"] = [role.name for role in getattr(simulator, "roles", [])]
    response["role_ids"] = [role.id for role in getattr(simulator, "roles", [])]
    return jsonify(response), 200


@simulator_bp.delete("/<int:simulator_id>")
@jwt_required()
def delete_simulator(simulator_id):
    user_email = get_jwt_identity()
    if not AccessChecker.is_admin(user_email):
        raise UnauthorizedError("El usuario no tiene permiso para eliminar este simulador")

    cascade = request.args.get("cascade", "false").lower() == "true"

    if cascade:
        SimulatorDataSourceRelation.remove_all_b_for_a(simulator_id)
        RoleSimulatorRelation.remove_all_a_for_b(simulator_id)

    SimulatorService.delete(simulator_id)

    return "", 204
