from urllib.parse import urlencode
from flask import Blueprint, jsonify, current_app, redirect, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.report_service import ReportService
from app.services.relations.report_data_source_relation import ReportDataSourceRelation
from app.services.relations.role_report_relation import RoleReportRelation
from app.domain.exceptions import DomainError, SchemaValidationError, UnauthorizedError
from app.schemas.report_schema import ReportCreateRequest, ReportUpdateRequest
from app.middleware import schema_validator
from app.api.utils.check_roles import AccessChecker

report_bp = Blueprint("report", __name__, url_prefix="/report")

@report_bp.post("")
@jwt_required()
@schema_validator(ReportCreateRequest)
def create_report():
    """Create a new report.
    
    Payload:
        main_title (str, required): The main title of the report.
        auxiliary_title (str, optional): The auxiliary title of the report.
        description (str, optional): The description of the report.
        document_file_id (int, optional): The ID of the associated document file.
        updated_at (datetime, required): The last update timestamp.
    
    Returns:
        dict: The created report with status code 201.
    
    Raises:
        400: If validation fails.
        401: If not authenticated.
    """
    user_email = get_jwt_identity()
    if not AccessChecker.is_admin(user_email):
        raise UnauthorizedError("El usuario no tiene permiso para crear reportes")

    report_service = ReportService()
    report_data = request.validated_data.dict()
    report = report_service.create(**report_data)
    report = report_service.get_by_id(report.id)
    
    AccessChecker.grant_admin_access(report.id, "report")
    
    include = ["id", "main_title", "auxiliary_title", "description", "document_file_id", "updated_at"]
    return jsonify(report.to_dict(include=include)), 201

@report_bp.get("/all")
def get_reports():
    """Retrieve all reports available for preview.
    
    Query Parameters:
        full (str, optional): Set to 'true' to get full report information.
    
    Returns:
        list: A list of reports with their basic information (id, main_title, auxiliary_title, updated_at).
              If full=true, returns all fields.
    """
    full = request.args.get("full") == "true"
    reports = ReportService.get_all_dict(include=["id",
                                                   "main_title",
                                                   "auxiliary_title",
                                                   "updated_at"]) if not full else ReportService.get_all_dict()
    return jsonify(reports), 200

@report_bp.get("/<int:report_id>")
@jwt_required()
def get_report_by_id(report_id):
    """Retrieve specific information of report by id.
    
    Path Parameters:
        report_id (int): The ID of the report.
    
    Returns:
        dict: The report with basic information (id, main_title, auxiliary_title, description, document_file_id).
    
    Raises:
        401: If not authenticated (when JWT is enabled).
        404: If report_id does not exist.
    """

    user_email = get_jwt_identity()
    if not AccessChecker.check_access(user_email, report_id, "report"):
        raise UnauthorizedError("El usuario no tiene permiso para acceder a este reporte")

    report = ReportService.get_by_id(report_id)

    return jsonify(report.to_dict(include=["id",
                                           "main_title",
                                           "auxiliary_title",
                                           "description",
                                           "document_file_id"])), 200

@report_bp.patch("/<int:report_id>")
@jwt_required()
@schema_validator(ReportUpdateRequest)
def update_report(report_id):
    """Update an existing report with a partial payload.
    
    Only the fields provided in the payload will be updated.
    
    Path Parameters:
        report_id (int): The ID of the report to update.
    
    Payload:
        main_title (str, optional): The main title of the report.
        auxiliary_title (str, optional): The auxiliary title of the report.
        description (str, optional): The description of the report.
        document_file_id (int, optional): The ID of the associated document file.
        updated_at (datetime, optional): The last update timestamp.
    
    Returns:
        dict: The updated report with status code 200.
    
    Raises:
        400: If validation fails or payload is empty.
        401: If not authenticated (when JWT is enabled).
        404: If report_id does not exist.
    """

    user_email = get_jwt_identity()
    if not AccessChecker.is_admin(user_email):
        raise UnauthorizedError("El usuario no tiene permiso para actualizar este reporte")

    update_data = request.validated_data.dict(exclude_unset=True)
    if not update_data:
        raise SchemaValidationError("At least one field must be provided")

    report = ReportService.update(report_id, **update_data)

    return jsonify(report.to_dict(include=["id",
                                           "main_title",
                                           "auxiliary_title",
                                           "description",
                                           "document_file_id",
                                           "updated_at"])), 200

@report_bp.delete("/<int:report_id>")
@jwt_required()
def delete_report(report_id):
    """Delete a report from the system.
    
    Path Parameters:
        report_id (int): The ID of the report to delete.
    
    Query Parameters:
        cascade (str, optional): Set to 'true' to also remove all relationship entries.
    
    Returns:
        Empty response with status 204 (No Content).
    
    Raises:
        401: If not authenticated (when JWT is enabled).
        404: If report_id does not exist.
    """
    
    user_email = get_jwt_identity()
    if not AccessChecker.is_admin(user_email):
        raise UnauthorizedError("El usuario no tiene permiso para eliminar este reporte")

    cascade = request.args.get("cascade", "false").lower() == "true"
    
    if cascade:
        ReportDataSourceRelation.remove_all_b_for_a(report_id)
        RoleReportRelation.remove_all_a_for_b(report_id)
        
    ReportService.delete(report_id)

    return "" , 204
