from app.models.simulator import Simulator
from app.services.base_service import BaseService
from app.models.base import db
from app.domain.exceptions import NotFoundError, IllegalOperationError
from app.services.data_source_service import DataSourceService
from app.services.role_service import RoleService

class SimulatorService(BaseService):
    model = Simulator
    
    @classmethod
    def add_data_source(cls, simulator_id, data_source_id):
        """Add a data source to a simulator.
        
        Args:
            simulator_id (int): The ID of the simulator.
            data_source_id (int): The ID of the data source to add.
        
        Returns:
            Simulator: The updated simulator instance with the new data source.
        
        Raises:
            NotFoundError: If the simulator or data source does not exist.
            IllegalOperationError: If the data source is already assigned to the simulator or if the operation fails.
        """
        simulator = cls.get_by_id(simulator_id)
        data_source = DataSourceService.get_by_id(data_source_id)
        
        if data_source in simulator.data_sources:
            raise IllegalOperationError(f"Data source {data_source_id} is already assigned to simulator {simulator_id}")
        
        try:
            simulator.data_sources.append(data_source)
            db.session.commit()
            return simulator
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def remove_data_source(cls, simulator_id, data_source_id):
        """Remove a data source from a simulator.
        
        Args:
            simulator_id (int): The ID of the simulator.
            data_source_id (int): The ID of the data source to remove.
        
        Returns:
            Simulator: The updated simulator instance without the data source.
        
        Raises:
            NotFoundError: If the simulator or data source does not exist.
            IllegalOperationError: If the data source is not assigned to the simulator or if the operation fails.
        """
        simulator = cls.get_by_id(simulator_id)
        data_source = DataSourceService.get_by_id(data_source_id)
        
        if data_source not in simulator.data_sources:
            raise IllegalOperationError(f"Data source {data_source_id} is not assigned to simulator {simulator_id}")
        
        try:
            simulator.data_sources.remove(data_source)
            db.session.commit()
            return simulator
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def add_role(cls, simulator_id, role_id):
        """Add a role to a simulator to grant access.
        
        Args:
            simulator_id (int): The ID of the simulator.
            role_id (int): The ID of the role to grant access.
        
        Returns:
            Simulator: The updated simulator instance with the new role permission.
        
        Raises:
            NotFoundError: If the simulator or role does not exist.
            IllegalOperationError: If the role already has access to the simulator or if the operation fails.
        """
        simulator = cls.get_by_id(simulator_id)
        role = RoleService.get_by_id(role_id)
        
        if role in simulator.roles:
            raise IllegalOperationError(f"Role {role_id} is already assigned to simulator {simulator_id}")
        
        try:
            simulator.roles.append(role)
            db.session.commit()
            return simulator
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def remove_role(cls, simulator_id, role_id):
        """Remove a role from a simulator to revoke access.
        
        Args:
            simulator_id (int): The ID of the simulator.
            role_id (int): The ID of the role to revoke access from.
        
        Returns:
            Simulator: The updated simulator instance without the role permission.
        
        Raises:
            NotFoundError: If the simulator or role does not exist.
            IllegalOperationError: If the role does not have access to the simulator or if the operation fails.
        """
        simulator = cls.get_by_id(simulator_id)
        role = RoleService.get_by_id(role_id)
        
        if role not in simulator.roles:
            raise IllegalOperationError(f"Role {role_id} is not assigned to simulator {simulator_id}")
        
        try:
            simulator.roles.remove(role)
            db.session.commit()
            return simulator
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
