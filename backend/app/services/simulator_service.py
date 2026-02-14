from app.models.simulator import Simulator
from app.services.base_service import BaseService


class SimulatorService(BaseService):
    """Service for managing Simulator CRUD operations.
    
    Note: Relationship operations (add/remove data_source, add/remove role) are
    handled by domain-level functions in app.domain.relations to prevent circular
    service dependencies.
    """
    model = Simulator
