from app.models.role import Role
from app.models.visor import Visor
from app.services.relations.base_relation import BaseRelation


class RoleVisorRelation(BaseRelation):
    """Manage many-to-many relationships between Role and Visor."""
    
    model_a = Role
    model_b = Visor
    relationship_a = 'visors'
    relationship_b = 'roles'
    
    @classmethod
    def add_visor_to_role(cls, role_id, visor_id):
        """Add a visor to a role.
        
        Args:
            role_id (int): The ID of the role.
            visor_id (int): The ID of the visor to add.
        
        Returns:
            tuple: (role_instance, visor_instance)
        """
        return cls.add(role_id, visor_id)
    
    @classmethod
    def remove_visor_from_role(cls, role_id, visor_id):
        """Remove a visor from a role.
        
        Args:
            role_id (int): The ID of the role.
            visor_id (int): The ID of the visor to remove.
        
        Returns:
            tuple: (role_instance, visor_instance)
        """
        return cls.remove(role_id, visor_id)
