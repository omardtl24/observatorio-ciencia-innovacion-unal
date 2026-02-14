from app.models.role import Role
from app.models.report import Report
from app.services.relations.base_relation import BaseRelation


class RoleReportRelation(BaseRelation):
    """Manage many-to-many relationships between Role and Report."""
    
    model_a = Role
    model_b = Report
    relationship_a = 'reports'
    relationship_b = 'roles'
    
    @classmethod
    def add_report_to_role(cls, role_id, report_id):
        """Add a report to a role.
        
        Args:
            role_id (int): The ID of the role.
            report_id (int): The ID of the report to add.
        
        Returns:
            tuple: (role_instance, report_instance)
        """
        return cls.add(role_id, report_id)
    
    @classmethod
    def remove_report_from_role(cls, role_id, report_id):
        """Remove a report from a role.
        
        Args:
            role_id (int): The ID of the role.
            report_id (int): The ID of the report to remove.
        
        Returns:
            tuple: (role_instance, report_instance)
        """
        return cls.remove(role_id, report_id)
