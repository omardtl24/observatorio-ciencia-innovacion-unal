from app.models.user import User
from app.models.role import Role
from app.services.relations.base_relation import BaseRelation


class UserRoleRelation(BaseRelation):
    """Manage many-to-many relationships between User and Role."""
    
    model_a = User
    model_b = Role
    relationship_a = 'roles'
    relationship_b = 'users'
    
    @classmethod
    def get_user_by_email(cls, email):
        """Get a user by email address.
        
        Args:
            email (str): The email address of the user.
        
        Returns:
            User: The user instance.
        
        Raises:
            NotFoundError: If the user does not exist.
        """
        from app.domain.exceptions import NotFoundError
        user = User.query.filter_by(email=email).first()
        if not user:
            raise NotFoundError(f"User {email} not found")
        return user
    
    @classmethod
    def add_role_to_user(cls, user_email, role_id):
        """Add a role to a user.
        
        Args:
            user_email (str): The email address of the user.
            role_id (int): The ID of the role to add.
        
        Returns:
            tuple: (user_instance, role_instance)
        
        Raises:
            NotFoundError: If the user or role does not exist.
            IllegalOperationError: If already assigned or operation fails.
        """
        user = cls.get_user_by_email(user_email)
        role = cls.get_b_by_id(role_id)
        
        from app.domain.exceptions import IllegalOperationError
        if role in user.roles:
            raise IllegalOperationError(f"Role {role_id} is already assigned to user {user_email}")
        
        return cls.add(user.id, role_id)
    
    @classmethod
    def remove_role_from_user(cls, user_email, role_id):
        """Remove a role from a user.
        
        Args:
            user_email (str): The email address of the user.
            role_id (int): The ID of the role to remove.
        
        Returns:
            tuple: (user_instance, role_instance)
        
        Raises:
            NotFoundError: If the user or role does not exist.
            IllegalOperationError: If not assigned or operation fails.
        """
        user = cls.get_user_by_email(user_email)
        return cls.remove(user.id, role_id)
