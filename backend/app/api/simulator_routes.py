from flask import Blueprint, jsonify, request # type: ignore
from flask_jwt_extended import get_jwt_identity, jwt_required # type: ignore

from app.api.utils.check_roles import AccessChecker, assert_admin
from app.api.utils.resource_urls import build_resource_url, delete_resource_file
from app.api.utils.serializers import serialize_resource_with_roles
from app.api.utils.validate_schema import validate_schema
from app.domain.exceptions import SchemaValidationError, UnauthorizedError
from app.schemas.simulator_schema import SimulatorCreateRequest, SimulatorUpdateRequest
from app.services.relations.role_simulator_relation import RoleSimulatorRelation
from app.services.relations.simulator_data_source_relation import SimulatorDataSourceRelation
from app.services.role_service import RoleService
from app.services.simulator_service import SimulatorService


simulator_bp = Blueprint("simulator", __name__, url_prefix="/simulator")


def _get_simulator_payload(schema_class):
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict(flat=True)
        role_ids = request.form.getlist("role_ids")
        if role_ids:
            data["role_ids"] = role_ids

    return validate_schema(data, schema_class).model_dump(exclude_unset=True)


def _get_simulator_source_url_field() -> str:
    return "simulator_url"


@simulator_bp.post("")
@jwt_required()
def create_simulator():
    assert_admin("El usuario no tiene permiso para crear simuladores")

    simulator_data = _get_simulator_payload(SimulatorCreateRequest)
    r_program = request.files.get("r_program")
    source_url_field = _get_simulator_source_url_field()
    from_file = simulator_data.pop("from_file", None)
    if from_file is None:
        from_file = r_program is not None
    from_file = bool(from_file)
    simulator_data["from_file"] = from_file

    if from_file and r_program is None:
        raise SchemaValidationError("Debes adjuntar el archivo r_program")
    if not from_file and not simulator_data.get(source_url_field):
        raise SchemaValidationError("Debes enviar la URL del simulador")

    role_ids = simulator_data.pop("role_ids", [])
    selected_role_ids = list({int(role_id) for role_id in role_ids})
    admin_role = RoleService.get_by_name("Administrador")

    for role_id in selected_role_ids:
        RoleService.get_by_id(role_id)

    simulator = SimulatorService.create(**simulator_data)
    if from_file:
        simulator_url = build_resource_url(r_program, simulator.id, "simulator")
        SimulatorService.update(
            simulator.id,
            simulator_url=simulator_url,
        )
    simulator = SimulatorService.get_by_id(simulator.id)

    AccessChecker.grant_admin_access(simulator.id, "simulator")
    for role_id in selected_role_ids:
        if role_id != admin_role.id:
            RoleSimulatorRelation.add(role_id, simulator.id)

    simulator = SimulatorService.get_by_id(simulator.id)

    include = ["id", "title", "description", "from_file", "simulator_url", "specs_file_id", "updated_at"]
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
            item = simulator.to_dict(include=["id", "title", "from_file", "updated_at"])
            item["roles"] = [role.name for role in getattr(simulator, "roles", [])]
            payload.append(item)
        return jsonify(payload), 200

    payload = [serialize_resource_with_roles(simulator) for simulator in simulators]
    return jsonify(payload), 200


@simulator_bp.get("/access/<int:simulator_id>")
@jwt_required()
def validate_simulator_access(simulator_id):
    user_email = get_jwt_identity()
    has_access = AccessChecker.check_access(user_email, simulator_id, "simulator")
    if not has_access:
        raise UnauthorizedError("El usuario no tiene permiso para acceder a este simulador")

    return "", 200


@simulator_bp.get("/<int:simulator_id>")
@jwt_required()
def get_simulator_by_id(simulator_id):
    user_email = get_jwt_identity()
    if not AccessChecker.check_access(user_email, simulator_id, "simulator"):
        raise UnauthorizedError("El usuario no tiene permiso para acceder a este simulador")

    simulator = SimulatorService.get_by_id(simulator_id)
    response = simulator.to_dict(
        include=["id", "title", "description", "from_file", "simulator_url", "specs_file_id", "updated_at"]
    )
    response["roles"] = [role.name for role in getattr(simulator, "roles", [])]
    response["role_ids"] = [role.id for role in getattr(simulator, "roles", [])]
    return jsonify(response), 200


@simulator_bp.patch("/<int:simulator_id>")
@jwt_required()
def update_simulator(simulator_id):
    assert_admin("El usuario no tiene permiso para actualizar este simulador")

    existing_simulator = SimulatorService.get_by_id(simulator_id)
    update_data = _get_simulator_payload(SimulatorUpdateRequest)
    r_program = request.files.get("r_program")
    from_file = update_data.pop("from_file", None)
    if from_file is None:
        from_file = existing_simulator.from_file
    from_file = bool(from_file)
    source_url_field = _get_simulator_source_url_field()
    resource_url = update_data.get(source_url_field)

    if not update_data and r_program is None and from_file == existing_simulator.from_file:
        raise SchemaValidationError("Debes enviar al menos un campo para actualizar")

    if from_file:
        if r_program is not None:
            if existing_simulator.from_file:
                delete_resource_file(simulator_id, "simulator")
            simulator_url = build_resource_url(r_program, simulator_id, "simulator")
            update_data[source_url_field] = simulator_url
        elif not existing_simulator.from_file:
            raise SchemaValidationError("Debes adjuntar el archivo r_program")
    else:
        if not resource_url:
            raise SchemaValidationError("Debes enviar la URL del simulador")
        if existing_simulator.from_file:
            delete_resource_file(simulator_id, "simulator")

    update_data["from_file"] = from_file
    if update_data:
        SimulatorService.update(simulator_id, **update_data)

    simulator = SimulatorService.get_by_id(simulator_id)

    return jsonify(
        simulator.to_dict(
            include=["id", "title", "description", "from_file", "simulator_url", "specs_file_id", "updated_at"]
        )
    ), 200


@simulator_bp.get("/<int:simulator_id>/data-sources")
@jwt_required()
def get_simulator_data_sources(simulator_id):
    user_email = get_jwt_identity()
    if not AccessChecker.check_access(user_email, simulator_id, "simulator"):
        raise UnauthorizedError("El usuario no tiene permiso para acceder a este simulador")

    data_sources = SimulatorDataSourceRelation.get_all_b_for_a(simulator_id)
    payload = [
        data_source.to_dict(include=["id", "name", "description", "file_id", "updated_at"])
        for data_source in data_sources
    ]
    return jsonify(payload), 200


@simulator_bp.post("/<int:simulator_id>/data-sources/<int:data_source_id>")
@jwt_required()
def add_simulator_data_source(simulator_id, data_source_id):
    assert_admin("El usuario no tiene permiso para actualizar este simulador")

    SimulatorDataSourceRelation.add_data_source_to_simulator(simulator_id, data_source_id)
    data_sources = SimulatorDataSourceRelation.get_all_b_for_a(simulator_id)
    payload = [
        data_source.to_dict(include=["id", "name", "description", "file_id", "updated_at"])
        for data_source in data_sources
    ]
    return jsonify(payload), 200


@simulator_bp.delete("/<int:simulator_id>/data-sources/<int:data_source_id>")
@jwt_required()
def remove_simulator_data_source(simulator_id, data_source_id):
    assert_admin("El usuario no tiene permiso para actualizar este simulador")

    SimulatorDataSourceRelation.remove_data_source_from_simulator(simulator_id, data_source_id)
    data_sources = SimulatorDataSourceRelation.get_all_b_for_a(simulator_id)
    payload = [
        data_source.to_dict(include=["id", "name", "description", "file_id", "updated_at"])
        for data_source in data_sources
    ]
    return jsonify(payload), 200


@simulator_bp.patch("/<int:simulator_id>/roles")
@jwt_required()
def update_simulator_roles(simulator_id):
    assert_admin("El usuario no tiene permiso para actualizar roles de este simulador")

    payload = request.get_json(silent=True) or {}
    role_ids = payload.get("role_ids")
    if not isinstance(role_ids, list):
        raise SchemaValidationError("El campo role_ids debe ser una lista")

    try:
        selected_role_ids = list({int(role_id) for role_id in role_ids})
    except (TypeError, ValueError):
        raise SchemaValidationError("El campo role_ids debe contener números enteros válidos")

    admin_role = RoleService.get_by_name("Administrador")
    for role_id in selected_role_ids:
        RoleService.get_by_id(role_id)

    RoleSimulatorRelation.remove_all_a_for_b(simulator_id)
    AccessChecker.grant_admin_access(simulator_id, "simulator")
    for role_id in selected_role_ids:
        if role_id != admin_role.id:
            RoleSimulatorRelation.add(role_id, simulator_id)

    simulator = SimulatorService.get_by_id(simulator_id)
    response = simulator.to_dict(include=["id", "title", "description", "simulator_url", "specs_file_id", "updated_at"])
    response["roles"] = [role.name for role in getattr(simulator, "roles", [])]
    response["role_ids"] = [role.id for role in getattr(simulator, "roles", [])]
    return jsonify(response), 200


@simulator_bp.delete("/<int:simulator_id>")
@jwt_required()
def delete_simulator(simulator_id):
    assert_admin("El usuario no tiene permiso para eliminar simuladores")

    simulator = SimulatorService.get_by_id(simulator_id)
    cascade = request.args.get("cascade", "false").lower() == "true"

    if cascade:
        SimulatorDataSourceRelation.remove_all_b_for_a(simulator_id)
        RoleSimulatorRelation.remove_all_a_for_b(simulator_id)

    # Delete resource files only for Shiny uploads
    if simulator.from_file:
        delete_resource_file(simulator_id, "simulator")
    
    SimulatorService.delete(simulator_id)

    return "", 204
