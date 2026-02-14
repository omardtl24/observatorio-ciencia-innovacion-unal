from app.models.role import Role
from app.models.simulator import Simulator
from app.services.relations.base_relation import BaseRelation


class RoleSimulatorRelation(BaseRelation):
    """Manage many-to-many relationships between Role and Simulator."""
    
    model_a = Role
    model_b = Simulator
    relationship_a = 'simulators'
    relationship_b = 'roles'
    
    @classmethod
    def add_simulator_to_role(cls, role_id, simulator_id):
        """Add a simulator to a role.
        
        Args:
            role_id (int): The ID of the role.
            simulator_id (int): The ID of the simulator to add.
        
        Returns:
            tuple: (role_instance, simulator_instance)
        """
        return cls.add(role_id, simulator_id)
    
    @classmethod
    def remove_simulator_from_role(cls, role_id, simulator_id):
        """Remove a simulator from a role.
        
        Args:
            role_id (int): The ID of the role.
            simulator_id (int): The ID of the simulator to remove.
        
        Returns:
            tuple: (role_instance, simulator_instance)
        """
        return cls.remove(role_id, simulator_id)
