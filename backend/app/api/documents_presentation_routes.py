from flask import Blueprint, jsonify, request # type: ignore
from flask_jwt_extended import get_jwt_identity, jwt_required # type: ignore

from app.api.utils.check_roles import AccessChecker, assert_admin
from app.api.utils.serializers import serialize_resource_with_roles
from app.domain.exceptions import SchemaValidationError, UnauthorizedError
from app.middleware import schema_validator
from app.schemas.documents_presentation_schema import (
    DocumentPresentationCreateRequest,
    DocumentPresentationUpdateRequest,
)
from app.services.documents_presentation_service import DocumentPresentationService
from app.services.relations.document_presentation_role_relation import DocumentPresentationRoleRelation
from app.services.role_service import RoleService


documents_presentation_bp = Blueprint(
    "documents_presentation", __name__, url_prefix="/document"
)


@documents_presentation_bp.post("")
@jwt_required()
@schema_validator(DocumentPresentationCreateRequest)
def create_document_presentation():
    assert_admin("El usuario no tiene permiso para crear documentos de presentacion")

    document_data = request.validated_data.dict()
    role_ids = document_data.pop("role_ids", [])
    selected_role_ids = list({int(role_id) for role_id in role_ids})
    admin_role = RoleService.get_by_name("Administrador")

    for role_id in selected_role_ids:
        RoleService.get_by_id(role_id)

    document_presentation = DocumentPresentationService.create(**document_data)
    document_presentation = DocumentPresentationService.get_by_id(document_presentation.id)

    AccessChecker.grant_admin_access(document_presentation.id, "document")
    for role_id in selected_role_ids:
        if role_id != admin_role.id:
            DocumentPresentationRoleRelation.add(document_presentation.id, role_id)

    document_presentation = DocumentPresentationService.get_by_id(document_presentation.id)

    include = ["id", "title", "description", "file_id", "updated_at"]
    response = document_presentation.to_dict(include=include)
    response["roles"] = [role.name for role in getattr(document_presentation, "roles", [])]
    return jsonify(response), 201


@documents_presentation_bp.get("/all")
def get_documents_presentations():
    full = request.args.get("full") == "true"
    documents_presentations = DocumentPresentationService.get_all()
    if not full:
        payload = []
        for document_presentation in documents_presentations:
            item = document_presentation.to_dict(include=["id", "title", "updated_at"])
            item["roles"] = [role.name for role in getattr(document_presentation, "roles", [])]
            payload.append(item)
        return jsonify(payload), 200

    payload = [serialize_resource_with_roles(document_presentation) for document_presentation in documents_presentations]
    return jsonify(payload), 200


@documents_presentation_bp.get("/<int:document_id>")
@jwt_required()
def get_document_presentation_by_id(document_id):
    user_email = get_jwt_identity()
    if not AccessChecker.check_access(user_email, document_id, "document"):
        raise UnauthorizedError("El usuario no tiene permiso para acceder a este documento de presentacion")

    document_presentation = DocumentPresentationService.get_by_id(document_id)
    response = document_presentation.to_dict(
        include=["id", "title", "description", "file_id", "updated_at"]
    )
    response["roles"] = [role.name for role in getattr(document_presentation, "roles", [])]
    response["role_ids"] = [role.id for role in getattr(document_presentation, "roles", [])]
    return jsonify(response), 200


@documents_presentation_bp.patch("/<int:document_id>")
@jwt_required()
@schema_validator(DocumentPresentationUpdateRequest)
def update_document_presentation(document_id):
    assert_admin("El usuario no tiene permiso para actualizar este documento de presentacion")

    update_data = request.validated_data.dict(exclude_unset=True)
    if not update_data:
        raise SchemaValidationError("Debes enviar al menos un campo para actualizar")

    document_presentation = DocumentPresentationService.update(document_id, **update_data)

    return jsonify(
        document_presentation.to_dict(
            include=["id", "title", "description", "file_id", "updated_at"]
        )
    ), 200


@documents_presentation_bp.patch("/<int:document_id>/roles")
@jwt_required()
def update_document_presentation_roles(document_id):
    assert_admin("El usuario no tiene permiso para actualizar roles de este documento de presentacion")

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

    DocumentPresentationRoleRelation.remove_all_b_for_a(document_id)
    AccessChecker.grant_admin_access(document_id, "document")
    for role_id in selected_role_ids:
        if role_id != admin_role.id:
            DocumentPresentationRoleRelation.add(document_id, role_id)

    document_presentation = DocumentPresentationService.get_by_id(document_id)
    response = document_presentation.to_dict(include=["id", "title", "description", "file_id", "updated_at"])
    response["roles"] = [role.name for role in getattr(document_presentation, "roles", [])]
    response["role_ids"] = [role.id for role in getattr(document_presentation, "roles", [])]
    return jsonify(response), 200


@documents_presentation_bp.delete("/<int:document_id>")
@jwt_required()
def delete_document_presentation(document_id):
    assert_admin("El usuario no tiene permiso para eliminar este documento de presentacion")

    cascade = request.args.get("cascade", "false").lower() == "true"

    if cascade:
        DocumentPresentationRoleRelation.remove_all_b_for_a(document_id)

    DocumentPresentationService.delete(document_id)

    return "", 204
