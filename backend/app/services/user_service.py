from app.models.user import User
from app.services.base_service import BaseService
from app.services.role_service import RoleService
from app.models.base import db
from app.domain.exceptions import NotFoundError, IllegalOperationError

class UserService(BaseService):
    model = User
    
    @classmethod
    def add_role(cls, user_email, role_id):
        """Add a role to a user.
        
        Args:
            user_email (str): The email address of the user.
            role_id (int): The ID of the role to add.
        
        Returns:
            User: The updated user instance with the new role.
        
        Raises:
            NotFoundError: If the user or role does not exist.
            IllegalOperationError: If the role is already assigned to the user or if the operation fails.
        """
        user = cls.get_by_id(user_email)
        role = RoleService.get_by_id(role_id)
        
        if role in user.roles:
            raise IllegalOperationError(f"Role {role_id} is already assigned to user {user_email}")
        
        try:
            user.roles.append(role)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def remove_role(cls, user_email, role_id):
        """Remove a role from a user.
        
        Args:
            user_email (str): The email address of the user.
            role_id (int): The ID of the role to remove.
        
        Returns:
            User: The updated user instance without the role.
        
        Raises:
            NotFoundError: If the user or role does not exist.
            IllegalOperationError: If the role is not assigned to the user or if the operation fails.
        """
        user = cls.get_by_id(user_email)
        role = RoleService.get_by_id(role_id)
        
        if role not in user.roles:
            raise IllegalOperationError(f"Role {role_id} is not assigned to user {user_email}")
        
        try:
            user.roles.remove(role)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    