from app.models.visor import Visor
from app.services.base_service import BaseService
from app.models.base import db
from app.domain.exceptions import NotFoundError, IllegalOperationError
from app.services.data_source_service import DataSourceService
from app.services.role_service import RoleService

class VisorService(BaseService):
    model = Visor
    
    @classmethod
    def add_data_source(cls, visor_id, data_source_id):
        """Add a data source to a visor.
        
        Args:
            visor_id (int): The ID of the visor.
            data_source_id (int): The ID of the data source to add.
        
        Returns:
            Visor: The updated visor instance with the new data source.
        
        Raises:
            NotFoundError: If the visor or data source does not exist.
            IllegalOperationError: If the data source is already assigned to the visor or if the operation fails.
        """
        visor = cls.get_by_id(visor_id)
        data_source = DataSourceService.get_by_id(data_source_id)
        
        if data_source in visor.data_sources:
            raise IllegalOperationError(f"Data source {data_source_id} is already assigned to visor {visor_id}")
        
        try:
            visor.data_sources.append(data_source)
            db.session.commit()
            return visor
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def remove_data_source(cls, visor_id, data_source_id):
        """Remove a data source from a visor.
        
        Args:
            visor_id (int): The ID of the visor.
            data_source_id (int): The ID of the data source to remove.
        
        Returns:
            Visor: The updated visor instance without the data source.
        
        Raises:
            NotFoundError: If the visor or data source does not exist.
            IllegalOperationError: If the data source is not assigned to the visor or if the operation fails.
        """
        visor = cls.get_by_id(visor_id)
        data_source = DataSourceService.get_by_id(data_source_id)
        
        if data_source not in visor.data_sources:
            raise IllegalOperationError(f"Data source {data_source_id} is not assigned to visor {visor_id}")
        
        try:
            visor.data_sources.remove(data_source)
            db.session.commit()
            return visor
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def add_role(cls, visor_id, role_id):
        """Add a role to a visor to grant access.
        
        Args:
            visor_id (int): The ID of the visor.
            role_id (int): The ID of the role to grant access.
        
        Returns:
            Visor: The updated visor instance with the new role permission.
        
        Raises:
            NotFoundError: If the visor or role does not exist.
            IllegalOperationError: If the role already has access to the visor or if the operation fails.
        """
        visor = cls.get_by_id(visor_id)
        role = RoleService.get_by_id(role_id)
        
        if role in visor.roles:
            raise IllegalOperationError(f"Role {role_id} is already assigned to visor {visor_id}")
        
        try:
            visor.roles.append(role)
            db.session.commit()
            return visor
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def remove_role(cls, visor_id, role_id):
        """Remove a role from a visor to revoke access.
        
        Args:
            visor_id (int): The ID of the visor.
            role_id (int): The ID of the role to revoke access from.
        
        Returns:
            Visor: The updated visor instance without the role permission.
        
        Raises:
            NotFoundError: If the visor or role does not exist.
            IllegalOperationError: If the role does not have access to the visor or if the operation fails.
        """
        visor = cls.get_by_id(visor_id)
        role = RoleService.get_by_id(role_id)
        
        if role not in visor.roles:
            raise IllegalOperationError(f"Role {role_id} is not assigned to visor {visor_id}")
        
        try:
            visor.roles.remove(role)
            db.session.commit()
            return visor
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
