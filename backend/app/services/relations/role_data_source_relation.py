from app.models.role import Role
from app.models.data_source import DataSource
from app.services.relations.base_relation import BaseRelation


class RoleDataSourceRelation(BaseRelation):
    """Manage many-to-many relationships between Role and DataSource."""

    model_a = Role
    model_b = DataSource
    relationship_a = 'data_sources'
    relationship_b = 'roles'

    @classmethod
    def add_data_source_to_role(cls, role_id, data_source_id):
        """Add a data source to a role.

        Args:
            role_id (int): The ID of the role.
            data_source_id (int): The ID of the data source to add.

        Returns:
            tuple: (role_instance, data_source_instance)
        """
        return cls.add(role_id, data_source_id)

    @classmethod
    def remove_data_source_from_role(cls, role_id, data_source_id):
        """Remove a data source from a role.

        Args:
            role_id (int): The ID of the role.
            data_source_id (int): The ID of the data source to remove.

        Returns:
            tuple: (role_instance, data_source_instance)
        """
        return cls.remove(role_id, data_source_id)
