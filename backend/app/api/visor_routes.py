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

visor_bp = Blueprint("visor", __name__, url_prefix="/visor")

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
    visor = visor_service.create(**visor_data)
    visor = visor_service.get_by_id(visor.id)
    
    # Grant admin role access to the newly created visor
    AccessChecker.grant_admin_access(visor.id, "visor")
    
    include = ["id", "name", "description", "type", "visor_url", "updated_at"]
    return jsonify(visor.to_dict(include=include)), 201

@visor_bp.get("/all")
def get_visor():
    """Retreive all visors available for preview
    Returns:
        list: A list of visors with their basic information (id, main_title, auxiliary_title, type, updated_at).
    """
    full = request.args.get("full") == "true"
    visors = VisorService.get_all_dict(include=["id",
                                                "main_title",
                                                "auxiliary_title",
                                                "type", 
                                                "updated_at"]) if not full else VisorService.get_all_dict()
    return jsonify(visors), 200

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



