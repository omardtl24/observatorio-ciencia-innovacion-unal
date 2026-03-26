from urllib.parse import urlencode
from flask import Blueprint, jsonify, current_app, redirect, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.visor_service import VisorService
from app.services.relations.visor_data_source_relation import VisorDataSourceRelation
from app.services.relations.role_visor_relation import RoleVisorRelation
from app.domain.exceptions import DomainError, UnauthorizedError
from app.schemas.visor_schema import VisorCreateRequest
from app.middleware import schema_validator
from app.api.utils.check_roles import AccessChecker
from app.services.role_service import RoleService

visor_bp = Blueprint("visor", __name__, url_prefix="/visor")


def _visor_to_dict_with_roles(visor):
    payload = visor.to_dict()
    payload["roles"] = [role.name for role in getattr(visor, "roles", [])]
    return payload

@visor_bp.post("")
@jwt_required()
@schema_validator(VisorCreateRequest)
def create_visor():
    """Create a new visor.
    
    Payload:
        name (str, required): The name of the visor.
        description (str, optional): The description of the visor.
        type (str, optional): The type of the visor.
        visor_url (str, optional): The URL of the visor.
    
    Returns:
        dict: The created visor with status code 201.
    
    Raises:
        400: If validation fails.
        401: If not authenticated.
    """

    user_email = get_jwt_identity()
    if not AccessChecker.is_admin(user_email):
        raise UnauthorizedError("El usuario no tiene permiso para crear visores")

    visor_service = VisorService()
    visor_data = request.validated_data.dict()
    role_ids = visor_data.pop("role_ids", [])
    selected_role_ids = list({int(role_id) for role_id in role_ids})
    admin_role = RoleService.get_by_name("Administrador")

    for role_id in selected_role_ids:
        RoleService.get_by_id(role_id)

    visor = visor_service.create(**visor_data)
    visor = visor_service.get_by_id(visor.id)
    
    # Grant admin role access to the newly created visor
    AccessChecker.grant_admin_access(visor.id, "visor")
    for role_id in selected_role_ids:
        if role_id != admin_role.id:
            RoleVisorRelation.add(role_id, visor.id)

    visor = visor_service.get_by_id(visor.id)
    
    include = ["id", "main_title", "auxiliary_title", "description", "type", "visor_url", "updated_at"]
    response = visor.to_dict(include=include)
    response["roles"] = [role.name for role in getattr(visor, "roles", [])]
    return jsonify(response), 201

@visor_bp.get("/all")
def get_visor():
    """Retreive all visors available for preview
    Returns:
        list: A list of visors with their basic information (id, main_title, auxiliary_title, type, updated_at).
    """
    full = request.args.get("full") == "true"
    visors = VisorService.get_all()
    if not full:
        payload = []
        for visor in visors:
            item = visor.to_dict(include=["id", "main_title", "auxiliary_title", "type", "updated_at"])
            item["roles"] = [role.name for role in getattr(visor, "roles", [])]
            payload.append(item)
        return jsonify(payload), 200

    payload = [_visor_to_dict_with_roles(visor) for visor in visors]
    return jsonify(payload), 200

@visor_bp.get("/<int:visor_id>")
#@jwt_required()
def get_visor_by_id(visor_id):
    """Retreive specific information of visor by id
    Returns:
        list: A list of visors with their basic information (id, main_title, auxiliary_title, description, visor_url).
    """

    #TODO: validate user permissions to delete files

    visor = VisorService.get_by_id(visor_id)

    return jsonify(visor.to_dict(include=["id",
                                          "main_title",
                                          "auxiliary_title",
                                          "description",
                                          "visor_url"])), 200

@visor_bp.delete("/<int:visor_id>")
@jwt_required()
def delete_visor(visor_id):
    user_email = get_jwt_identity()
    if not AccessChecker.is_admin(user_email):
        raise UnauthorizedError("El usuario no tiene permiso para eliminar visores")
    
    #TODO: validate user permissions to delete files

    cascade = request.args.get("cascade", "false").lower() == "true"
    
    if cascade:
        VisorDataSourceRelation.remove_all_b_for_a(visor_id)
        RoleVisorRelation.remove_all_a_for_b(visor_id)
        
    VisorService.delete(visor_id)

    return "" , 204



