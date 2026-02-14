from app.models.visor import Visor
from app.services.base_service import BaseService


class VisorService(BaseService):
    """Service for managing Visor CRUD operations.
    
    Note: Relationship operations (add/remove data_source, add/remove role) are
    handled by domain-level functions in app.domain.relations to prevent circular
    service dependencies.
    """
    model = Visor
