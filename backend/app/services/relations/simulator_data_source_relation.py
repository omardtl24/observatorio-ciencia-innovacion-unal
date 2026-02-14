from app.models.simulator import Simulator
from app.models.data_source import DataSource
from app.services.relations.base_relation import BaseRelation


class SimulatorDataSourceRelation(BaseRelation):
    """Manage many-to-many relationships between Simulator and DataSource."""
    
    model_a = Simulator
    model_b = DataSource
    relationship_a = 'data_sources'
    relationship_b = 'simulators'
    
    @classmethod
    def add_data_source_to_simulator(cls, simulator_id, data_source_id):
        """Add a data source to a simulator.
        
        Args:
            simulator_id (int): The ID of the simulator.
            data_source_id (int): The ID of the data source to add.
        
        Returns:
            tuple: (simulator_instance, data_source_instance)
        """
        return cls.add(simulator_id, data_source_id)
    
    @classmethod
    def remove_data_source_from_simulator(cls, simulator_id, data_source_id):
        """Remove a data source from a simulator.
        
        Args:
            simulator_id (int): The ID of the simulator.
            data_source_id (int): The ID of the data source to remove.
        
        Returns:
            tuple: (simulator_instance, data_source_instance)
        """
        return cls.remove(simulator_id, data_source_id)
