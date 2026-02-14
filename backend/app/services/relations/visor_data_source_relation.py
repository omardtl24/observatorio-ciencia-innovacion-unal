from app.models.visor import Visor
from app.models.data_source import DataSource
from app.services.relations.base_relation import BaseRelation


class VisorDataSourceRelation(BaseRelation):
    """Manage many-to-many relationships between Visor and DataSource."""
    
    model_a = Visor
    model_b = DataSource
    relationship_a = 'data_sources'
    relationship_b = 'visors'
    
    @classmethod
    def add_data_source_to_visor(cls, visor_id, data_source_id):
        """Add a data source to a visor.
        
        Args:
            visor_id (int): The ID of the visor.
            data_source_id (int): The ID of the data source to add.
        
        Returns:
            tuple: (visor_instance, data_source_instance)
        """
        return cls.add(visor_id, data_source_id)
    
    @classmethod
    def remove_data_source_from_visor(cls, visor_id, data_source_id):
        """Remove a data source from a visor.
        
        Args:
            visor_id (int): The ID of the visor.
            data_source_id (int): The ID of the data source to remove.
        
        Returns:
            tuple: (visor_instance, data_source_instance)
        """
        return cls.remove(visor_id, data_source_id)
