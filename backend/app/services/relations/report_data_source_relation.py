from app.models.report import Report
from app.models.data_source import DataSource
from app.services.relations.base_relation import BaseRelation


class ReportDataSourceRelation(BaseRelation):
    """Manage many-to-many relationships between Report and DataSource."""
    
    model_a = Report
    model_b = DataSource
    relationship_a = 'data_sources'
    relationship_b = 'reports'
    
    @classmethod
    def add_data_source_to_report(cls, report_id, data_source_id):
        """Add a data source to a report.
        
        Args:
            report_id (int): The ID of the report.
            data_source_id (int): The ID of the data source to add.
        
        Returns:
            tuple: (report_instance, data_source_instance)
        """
        return cls.add(report_id, data_source_id)
    
    @classmethod
    def remove_data_source_from_report(cls, report_id, data_source_id):
        """Remove a data source from a report.
        
        Args:
            report_id (int): The ID of the report.
            data_source_id (int): The ID of the data source to remove.
        
        Returns:
            tuple: (report_instance, data_source_instance)
        """
        return cls.remove(report_id, data_source_id)
