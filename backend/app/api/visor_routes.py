from flask import Blueprint, jsonify, request # type: ignore
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore
from app.services.visor_service import VisorService
from app.services.relations.visor_data_source_relation import VisorDataSourceRelation
from app.services.relations.role_visor_relation import RoleVisorRelation
from app.domain.exceptions import UnauthorizedError, SchemaValidationError
from app.schemas.visor_schema import VisorCreateRequest, VisorUpdateRequest
from app.api.utils.check_roles import AccessChecker, assert_admin
from app.api.utils.resource_urls import build_resource_url, delete_resource_file
from app.api.utils.validate_schema import validate_schema
from app.api.utils.serializers import serialize_resource_with_roles
from app.services.role_service import RoleService

visor_bp = Blueprint("visor", __name__, url_prefix="/visor")


def _get_visor_payload(schema_class):
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict(flat=True)
        role_ids = request.form.getlist("role_ids")
        if role_ids:
            data["role_ids"] = role_ids

    return validate_schema(data, schema_class).model_dump(exclude_unset=True)


def _get_visor_source_url_field() -> str:
    return "visor_url"


@visor_bp.post("")
@jwt_required()
def create_visor():
    """Create a new visor.
    
    Payload:
        name (str, required): The name of the visor.
        description (str, optional): The description of the visor.
    
    Returns:
        dict: The created visor with status code 201.
    
    Raises:
        400: If validation fails.
        401: If not authenticated.
    """

    assert_admin("El usuario no tiene permiso para crear visores")

    visor_service = VisorService()
    visor_data = _get_visor_payload(VisorCreateRequest)
    r_program = request.files.get("r_program")
    source_url_field = _get_visor_source_url_field()
    from_file = visor_data.pop("from_file", None)
    if from_file is None:
        from_file = r_program is not None
    from_file = bool(from_file)
    visor_data["from_file"] = from_file

    if from_file and r_program is None:
        raise SchemaValidationError("Debes adjuntar el archivo r_program")
    if not from_file and not visor_data.get(source_url_field):
        raise SchemaValidationError("Debes enviar la URL del visor")

    role_ids = visor_data.pop("role_ids", [])
    selected_role_ids = list({int(role_id) for role_id in role_ids})
    admin_role = RoleService.get_by_name("Administrador")

    for role_id in selected_role_ids:
        RoleService.get_by_id(role_id)

    visor = visor_service.create(**visor_data)
    if from_file:
        visor_url = build_resource_url(r_program, visor.id, "visor")
        visor_service.update(visor.id, visor_url=visor_url)

    visor = visor_service.get_by_id(visor.id)
    
    # Grant admin role access to the newly created visor
    AccessChecker.grant_admin_access(visor.id, "visor")
    for role_id in selected_role_ids:
        if role_id != admin_role.id:
            RoleVisorRelation.add(role_id, visor.id)

    visor = visor_service.get_by_id(visor.id)

    include = ["id", "title", "description", "from_file", "visor_url", "updated_at"]
    response = visor.to_dict(include=include)
    response["roles"] = [role.name for role in getattr(visor, "roles", [])]
    return jsonify(response), 201

@visor_bp.get("/all")
def get_visor():
    """Retreive all visors available for preview
    Returns:
    """
    full = request.args.get("full") == "true"
    visors = VisorService.get_all()
    if not full:
        payload = []
        for visor in visors:
            item = visor.to_dict(include=["id", "title", "type", "from_file", "updated_at"])
            item["roles"] = [role.name for role in getattr(visor, "roles", [])]
            payload.append(item)
        return jsonify(payload), 200

    payload = [serialize_resource_with_roles(visor) for visor in visors]
    return jsonify(payload), 200


@visor_bp.get("/access/<int:visor_id>")
@jwt_required()
def validate_visor_access(visor_id):
    user_email = get_jwt_identity()
    has_access = AccessChecker.check_access(user_email, visor_id, "visor")
    if not has_access:
        raise UnauthorizedError("El usuario no tiene permiso para acceder a este visor")

    return "", 200

@visor_bp.get("/<int:visor_id>")
@jwt_required()
def get_visor_by_id(visor_id):
    """Retreive specific information of visor by id
    Returns:
    """
    user_email = get_jwt_identity()
    has_access = AccessChecker.check_access(user_email, visor_id, "visor")

    if not has_access:
        raise UnauthorizedError("El usuario no tiene permiso para acceder a este visor")


    visor = VisorService.get_by_id(visor_id)
    response = visor.to_dict(include=["id",
                                      "title",
                                      "description",
                                      "from_file",
                                      "visor_url",
                                      "updated_at"])
    response["role_ids"] = [role.id for role in getattr(visor, "roles", [])]
    return jsonify(response), 200


@visor_bp.patch("/<int:visor_id>")
@jwt_required()
def update_visor(visor_id):
    assert_admin("El usuario no tiene permiso para actualizar este visor")

    existing_visor = VisorService.get_by_id(visor_id)
    update_data = _get_visor_payload(VisorUpdateRequest)
    role_ids = update_data.pop("role_ids", None)
    from_file = update_data.pop("from_file", None)
    if from_file is None:
        from_file = existing_visor.from_file
    from_file = bool(from_file)

    if not update_data and role_ids is None and from_file == existing_visor.from_file:
        raise SchemaValidationError("Debes enviar al menos un campo para actualizar")

    r_program = request.files.get("r_program")
    source_url_field = _get_visor_source_url_field()
    resource_url = update_data.get(source_url_field)

    if from_file:
        if r_program is not None:
            if existing_visor.from_file:
                delete_resource_file(visor_id, "visor")
            visor_url = build_resource_url(r_program, visor_id, "visor")
            update_data[source_url_field] = visor_url
        elif not existing_visor.from_file:
            raise SchemaValidationError("Debes adjuntar el archivo r_program")
    else:
        if not resource_url:
            raise SchemaValidationError("Debes enviar la URL del visor")
        if existing_visor.from_file:
            delete_resource_file(visor_id, "visor")

    update_data["from_file"] = from_file
    if update_data:
        VisorService.update(visor_id, **update_data)

    if role_ids is not None:
        selected_role_ids = list({int(role_id) for role_id in role_ids})
        admin_role = RoleService.get_by_name("Administrador")

        for role_id in selected_role_ids:
            RoleService.get_by_id(role_id)

        RoleVisorRelation.remove_all_a_for_b(visor_id)
        for role_id in selected_role_ids:
            if role_id != admin_role.id:
                RoleVisorRelation.add(role_id, visor_id)

    visor = VisorService.get_by_id(visor_id)
    include = ["id", "title", "description", "from_file", "visor_url", "updated_at"]
    response = visor.to_dict(include=include)
    response["roles"] = [role.name for role in getattr(visor, "roles", [])]
    response["role_ids"] = [role.id for role in getattr(visor, "roles", [])]
    return jsonify(response), 200


@visor_bp.get("/<int:visor_id>/data-sources")
@jwt_required()
def get_visor_data_sources(visor_id):
    user_email = get_jwt_identity()
    if not AccessChecker.check_access(user_email, visor_id, "visor"):
        raise UnauthorizedError("El usuario no tiene permiso para acceder a este visor")

    data_sources = VisorDataSourceRelation.get_all_b_for_a(visor_id)
    payload = [
        data_source.to_dict(include=["id", "name", "description", "file_id", "updated_at"])
        for data_source in data_sources
    ]
    return jsonify(payload), 200


@visor_bp.post("/<int:visor_id>/data-sources/<int:data_source_id>")
@jwt_required()
def add_visor_data_source(visor_id, data_source_id):
    assert_admin("El usuario no tiene permiso para actualizar este visor")

    VisorDataSourceRelation.add_data_source_to_visor(visor_id, data_source_id)
    data_sources = VisorDataSourceRelation.get_all_b_for_a(visor_id)
    payload = [
        data_source.to_dict(include=["id", "name", "description", "file_id", "updated_at"])
        for data_source in data_sources
    ]
    return jsonify(payload), 200


@visor_bp.delete("/<int:visor_id>/data-sources/<int:data_source_id>")
@jwt_required()
def remove_visor_data_source(visor_id, data_source_id):
    assert_admin("El usuario no tiene permiso para actualizar este visor")

    VisorDataSourceRelation.remove_data_source_from_visor(visor_id, data_source_id)
    data_sources = VisorDataSourceRelation.get_all_b_for_a(visor_id)
    payload = [
        data_source.to_dict(include=["id", "name", "description", "file_id", "updated_at"])
        for data_source in data_sources
    ]
    return jsonify(payload), 200


@visor_bp.patch("/<int:visor_id>/roles")
@jwt_required()
def update_visor_roles(visor_id):
    assert_admin("El usuario no tiene permiso para actualizar roles de este visor")

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

    RoleVisorRelation.remove_all_a_for_b(visor_id)
    AccessChecker.grant_admin_access(visor_id, "visor")
    for role_id in selected_role_ids:
        if role_id != admin_role.id:
            RoleVisorRelation.add(role_id, visor_id)

    visor = VisorService.get_by_id(visor_id)
    include = ["id", "title", "description", "type", "visor_url", "updated_at"]
    response = visor.to_dict(include=include)
    response["roles"] = [role.name for role in getattr(visor, "roles", [])]
    response["role_ids"] = [role.id for role in getattr(visor, "roles", [])]
    return jsonify(response), 200

@visor_bp.delete("/<int:visor_id>")
@jwt_required()
def delete_visor(visor_id):
    assert_admin("El usuario no tiene permiso para eliminar visores")

    visor = VisorService.get_by_id(visor_id)
    cascade = request.args.get("cascade", "false").lower() == "true"
    
    if cascade:
        VisorDataSourceRelation.remove_all_b_for_a(visor_id)
        RoleVisorRelation.remove_all_a_for_b(visor_id)
    
    # Delete resource files only for Shiny uploads
    if visor.from_file:
        delete_resource_file(visor_id, "visor")
    
    VisorService.delete(visor_id)

    return "", 204



