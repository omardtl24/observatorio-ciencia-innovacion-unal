from app.models.role import Role
from app.services.base_service import BaseService
from app.domain.exceptions import NotFoundError


class RoleService(BaseService):
    """Service for managing Role CRUD operations.
    
    Note: Relationship operations (add/remove user, report, visor, etc.) are
    handled by domain-level functions in app.domain.relations to prevent
    circular service dependencies.
    """
    model = Role

    @staticmethod
    def get_by_name(name):
        """Retrieve a role by its name.
        
        Args:
            name (str): The name of the role to retrieve.
        
        Returns:
            Role: The Role instance with the specified name, or None if not found.
        """
        instance = Role.query.filter_by(name=name).first()
        if not instance:
            raise NotFoundError(f"Role with name={name} not found")
        return instance
