from app.models.report import Report
from app.services.base_service import BaseService


class ReportService(BaseService):
    """Service for managing Report CRUD operations.
    
    Note: Relationship operations (add/remove data_source, add/remove role) are
    handled by domain-level functions in app.domain.relations to prevent circular
    service dependencies.
    """
    model = Report