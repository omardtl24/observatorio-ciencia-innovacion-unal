from app.models.report import Report
from app.services.base_service import BaseService
from app.models.base import db
from app.domain.exceptions import NotFoundError, IllegalOperationError
from app.services.data_source_service import DataSourceService
from app.services.role_service import RoleService

class ReportService(BaseService):
    model = Report
    
    @classmethod
    def add_data_source(cls, report_id, data_source_id):
        """Add a data source to a report.
        
        Args:
            report_id (int): The ID of the report.
            data_source_id (int): The ID of the data source to add.
        
        Returns:
            Report: The updated report instance with the new data source.
        
        Raises:
            NotFoundError: If the report or data source does not exist.
            IllegalOperationError: If the data source is already assigned to the report or if the operation fails.
        """
        report = cls.get_by_id(report_id)
        data_source = DataSourceService.get_by_id(data_source_id)
        
        if data_source in report.data_sources:
            raise IllegalOperationError(f"Data source {data_source_id} is already assigned to report {report_id}")
        
        try:
            report.data_sources.append(data_source)
            db.session.commit()
            return report
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def remove_data_source(cls, report_id, data_source_id):
        """Remove a data source from a report.
        
        Args:
            report_id (int): The ID of the report.
            data_source_id (int): The ID of the data source to remove.
        
        Returns:
            Report: The updated report instance without the data source.
        
        Raises:
            NotFoundError: If the report or data source does not exist.
            IllegalOperationError: If the data source is not assigned to the report or if the operation fails.
        """
        report = cls.get_by_id(report_id)
        data_source = DataSourceService.get_by_id(data_source_id)
        
        if data_source not in report.data_sources:
            raise IllegalOperationError(f"Data source {data_source_id} is not assigned to report {report_id}")
        
        try:
            report.data_sources.remove(data_source)
            db.session.commit()
            return report
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def add_role(cls, report_id, role_id):
        """Add a role to a report to grant access.
        
        Args:
            report_id (int): The ID of the report.
            role_id (int): The ID of the role to grant access.
        
        Returns:
            Report: The updated report instance with the new role permission.
        
        Raises:
            NotFoundError: If the report or role does not exist.
            IllegalOperationError: If the role already has access to the report or if the operation fails.
        """
        report = cls.get_by_id(report_id)
        role = RoleService.get_by_id(role_id)
        
        if role in report.roles:
            raise IllegalOperationError(f"Role {role_id} is already assigned to report {report_id}")
        
        try:
            report.roles.append(role)
            db.session.commit()
            return report
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def remove_role(cls, report_id, role_id):
        """Remove a role from a report to revoke access.
        
        Args:
            report_id (int): The ID of the report.
            role_id (int): The ID of the role to revoke access from.
        
        Returns:
            Report: The updated report instance without the role permission.
        
        Raises:
            NotFoundError: If the report or role does not exist.
            IllegalOperationError: If the role does not have access to the report or if the operation fails.
        """
        report = cls.get_by_id(report_id)
        role = RoleService.get_by_id(role_id)
        
        if role not in report.roles:
            raise IllegalOperationError(f"Role {role_id} is not assigned to report {report_id}")
        
        try:
            report.roles.remove(role)
            db.session.commit()
            return report
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))