from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.utils.check_roles import AccessChecker, assert_admin
from app.api.utils.serializers import serialize_data_source
from app.domain.exceptions import UnauthorizedError
from app.middleware import schema_validator
from app.schemas.data_source_schema import DataSourceCreateRequest
from app.services.data_source_service import DataSourceService
from app.services.report_service import ReportService
from app.services.simulator_service import SimulatorService
from app.services.visor_service import VisorService
from app.services.relations.report_data_source_relation import ReportDataSourceRelation
from app.services.relations.simulator_data_source_relation import SimulatorDataSourceRelation
from app.services.relations.visor_data_source_relation import VisorDataSourceRelation
from app.services.relations.role_data_source_relation import RoleDataSourceRelation


data_source_bp = Blueprint("data_source", __name__, url_prefix="/data-source")


@data_source_bp.post("")
@jwt_required()
@schema_validator(DataSourceCreateRequest)
def create_data_source():
    assert_admin("El usuario no tiene permiso para gestionar fuentes de datos")

    data_source_data = request.validated_data.model_dump()
    data_source = DataSourceService.create(**data_source_data)
    data_source = DataSourceService.get_by_id(data_source.id)

    AccessChecker.grant_admin_access(data_source.id, "data_source")
    data_source = DataSourceService.get_by_id(data_source.id)

    return jsonify(serialize_data_source(data_source)), 201


@data_source_bp.get("/all")
@jwt_required()
def get_data_sources():
    data_sources = DataSourceService.get_all()
    payload = [serialize_data_source(data_source) for data_source in data_sources]
    return jsonify(payload), 200


@data_source_bp.get("/<int:data_source_id>")
@jwt_required()
def get_data_source_by_id(data_source_id):
    user_email = get_jwt_identity()
    if not AccessChecker.check_access(user_email, data_source_id, "data_source"):
        raise UnauthorizedError("El usuario no tiene permiso para acceder a esta fuente de datos")

    data_source = DataSourceService.get_by_id(data_source_id)
    return jsonify(serialize_data_source(data_source)), 200


@data_source_bp.delete("/<int:data_source_id>")
@jwt_required()
def delete_data_source(data_source_id):
    """Delete a data source from the system.
    
    Path Parameters:
        data_source_id (int): The ID of the data source to delete.
    
    Query Parameters:
        cascade (str, optional): Set to 'true' to also remove all relationship entries.
    
    Returns:
        Empty response with status 204 (No Content).
    
    Raises:
        401: If not authenticated (when JWT is enabled).
        404: If data_source_id does not exist.
    """
    
    assert_admin("El usuario no tiene permiso para eliminar fuentes de datos")
    
    cascade = request.args.get("cascade", "false").lower() == "true"
    
    if cascade:
        # Remove all associations with reports, visors, simulators, and roles
        ReportDataSourceRelation.remove_all_b_for_a(data_source_id)
        VisorDataSourceRelation.remove_all_b_for_a(data_source_id)
        SimulatorDataSourceRelation.remove_all_b_for_a(data_source_id)
        RoleDataSourceRelation.remove_all_b_for_a(data_source_id)
        
    DataSourceService.delete(data_source_id)
    
    return "", 204


@data_source_bp.post("/<int:data_source_id>/report/<int:report_id>")
@jwt_required()
def add_data_source_to_report(data_source_id, report_id):
    assert_admin("El usuario no tiene permiso para actualizar fuentes de datos")

    ReportService.get_by_id(report_id)
    DataSourceService.get_by_id(data_source_id)
    ReportDataSourceRelation.add_data_source_to_report(report_id, data_source_id)

    report = ReportService.get_by_id(report_id)
    response = report.to_dict(include=["id", "title", "description", "document_file_id", "updated_at"])
    response["data_source_ids"] = [data_source.id for data_source in getattr(report, "data_sources", [])]
    return jsonify(response), 200


@data_source_bp.delete("/<int:data_source_id>/report/<int:report_id>")
@jwt_required()
def remove_data_source_from_report(data_source_id, report_id):
    assert_admin("El usuario no tiene permiso para actualizar fuentes de datos")

    ReportService.get_by_id(report_id)
    DataSourceService.get_by_id(data_source_id)
    ReportDataSourceRelation.remove_data_source_from_report(report_id, data_source_id)

    report = ReportService.get_by_id(report_id)
    response = report.to_dict(include=["id", "title", "description", "document_file_id", "updated_at"])
    response["data_source_ids"] = [data_source.id for data_source in getattr(report, "data_sources", [])]
    return jsonify(response), 200


@data_source_bp.post("/<int:data_source_id>/visor/<int:visor_id>")
@jwt_required()
def add_data_source_to_visor(data_source_id, visor_id):
    assert_admin("El usuario no tiene permiso para actualizar fuentes de datos")

    VisorService.get_by_id(visor_id)
    DataSourceService.get_by_id(data_source_id)
    VisorDataSourceRelation.add_data_source_to_visor(visor_id, data_source_id)

    visor = VisorService.get_by_id(visor_id)
    response = visor.to_dict(include=["id", "title", "description", "visor_url", "updated_at"])
    response["data_source_ids"] = [data_source.id for data_source in getattr(visor, "data_sources", [])]
    return jsonify(response), 200


@data_source_bp.delete("/<int:data_source_id>/visor/<int:visor_id>")
@jwt_required()
def remove_data_source_from_visor(data_source_id, visor_id):
    assert_admin("El usuario no tiene permiso para actualizar fuentes de datos")

    VisorService.get_by_id(visor_id)
    DataSourceService.get_by_id(data_source_id)
    VisorDataSourceRelation.remove_data_source_from_visor(visor_id, data_source_id)

    visor = VisorService.get_by_id(visor_id)
    response = visor.to_dict(include=["id", "title", "description", "visor_url", "updated_at"])
    response["data_source_ids"] = [data_source.id for data_source in getattr(visor, "data_sources", [])]
    return jsonify(response), 200


@data_source_bp.post("/<int:data_source_id>/simulator/<int:simulator_id>")
@jwt_required()
def add_data_source_to_simulator(data_source_id, simulator_id):
    assert_admin("El usuario no tiene permiso para actualizar fuentes de datos")

    SimulatorService.get_by_id(simulator_id)
    DataSourceService.get_by_id(data_source_id)
    SimulatorDataSourceRelation.add_data_source_to_simulator(simulator_id, data_source_id)

    simulator = SimulatorService.get_by_id(simulator_id)
    response = simulator.to_dict(include=["id", "title", "description", "simulator_url", "specs_file_id", "updated_at"])
    response["data_source_ids"] = [data_source.id for data_source in getattr(simulator, "data_sources", [])]
    return jsonify(response), 200


@data_source_bp.delete("/<int:data_source_id>/simulator/<int:simulator_id>")
@jwt_required()
def remove_data_source_from_simulator(data_source_id, simulator_id):
    assert_admin("El usuario no tiene permiso para actualizar fuentes de datos")

    SimulatorService.get_by_id(simulator_id)
    DataSourceService.get_by_id(data_source_id)
    SimulatorDataSourceRelation.remove_data_source_from_simulator(simulator_id, data_source_id)

    simulator = SimulatorService.get_by_id(simulator_id)
    response = simulator.to_dict(include=["id", "title", "description", "simulator_url", "specs_file_id", "updated_at"])
    response["data_source_ids"] = [data_source.id for data_source in getattr(simulator, "data_sources", [])]
    return jsonify(response), 200
