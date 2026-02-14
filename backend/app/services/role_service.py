from app.models.role import Role
from app.services.base_service import BaseService


class RoleService(BaseService):
    """Service for managing Role CRUD operations.
    
    Note: Relationship operations (add/remove user, report, visor, etc.) are
    handled by domain-level functions in app.domain.relations to prevent
    circular service dependencies.
    """
    model = Role
