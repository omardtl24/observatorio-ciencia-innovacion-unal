from app.models.user import User
from app.services.base_service import BaseService


class UserService(BaseService):
    """Service for managing User CRUD operations.
    
    Note: Relationship operations (add/remove role) are handled by
    domain-level functions in app.domain.relations to prevent circular
    service dependencies.
    """
    model = User
    