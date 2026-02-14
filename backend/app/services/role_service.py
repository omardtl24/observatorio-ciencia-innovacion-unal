from app.models.role import Role
from app.services.base_service import BaseService
from app.models.base import db
from app.domain.exceptions import NotFoundError, IllegalOperationError
from app.services.user_service import UserService
from app.services.report_service import ReportService
from app.services.visor_service import VisorService
from app.services.simulator_service import SimulatorService
from app.services.documents_presentation_service import DocumentPresentationService

class RoleService(BaseService):
    model = Role
    
    @classmethod
    def add_user(cls, role_id, user_email):
        """Add a user to a role.
        
        Args:
            role_id (int): The ID of the role.
            user_email (str): The email address of the user to add.
        
        Returns:
            Role: The updated role instance with the new user.
        
        Raises:
            NotFoundError: If the role or user does not exist.
            IllegalOperationError: If the user is already assigned to the role or if the operation fails.
        """
        role = cls.get_by_id(role_id)
        user = UserService.get_by_id(user_email)
        
        if user in role.users:
            raise IllegalOperationError(f"User {user_email} is already assigned to role {role_id}")
        
        try:
            role.users.append(user)
            db.session.commit()
            return role
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def remove_user(cls, role_id, user_email):
        """Remove a user from a role.
        
        Args:
            role_id (int): The ID of the role.
            user_email (str): The email address of the user to remove.
        
        Returns:
            Role: The updated role instance without the user.
        
        Raises:
            NotFoundError: If the role or user does not exist.
            IllegalOperationError: If the user is not assigned to the role or if the operation fails.
        """
        role = cls.get_by_id(role_id)
        user = UserService.get_by_id(user_email)
        
        if user not in role.users:
            raise IllegalOperationError(f"User {user_email} is not assigned to role {role_id}")
        
        try:
            role.users.remove(user)
            db.session.commit()
            return role
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def add_report(cls, role_id, report_id):
        """Add a report to a role.
        
        Args:
            role_id (int): The ID of the role.
            report_id (int): The ID of the report to add.
        
        Returns:
            Role: The updated role instance with access to the new report.
        
        Raises:
            NotFoundError: If the role or report does not exist.
            IllegalOperationError: If the report is already assigned to the role or if the operation fails.
        """
        role = cls.get_by_id(role_id)
        report = ReportService.get_by_id(report_id)
        
        if report in role.reports:
            raise IllegalOperationError(f"Report {report_id} is already assigned to role {role_id}")
        
        try:
            role.reports.append(report)
            db.session.commit()
            return role
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def remove_report(cls, role_id, report_id):
        """Remove a report from a role.
        
        Args:
            role_id (int): The ID of the role.
            report_id (int): The ID of the report to remove.
        
        Returns:
            Role: The updated role instance without access to the report.
        
        Raises:
            NotFoundError: If the role or report does not exist.
            IllegalOperationError: If the report is not assigned to the role or if the operation fails.
        """
        role = cls.get_by_id(role_id)
        report = ReportService.get_by_id(report_id)
        
        if report not in role.reports:
            raise IllegalOperationError(f"Report {report_id} is not assigned to role {role_id}")
        
        try:
            role.reports.remove(report)
            db.session.commit()
            return role
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def add_visor(cls, role_id, visor_id):
        """Add a visor to a role.
        
        Args:
            role_id (int): The ID of the role.
            visor_id (int): The ID of the visor to add.
        
        Returns:
            Role: The updated role instance with access to the new visor.
        
        Raises:
            NotFoundError: If the role or visor does not exist.
            IllegalOperationError: If the visor is already assigned to the role or if the operation fails.
        """
        role = cls.get_by_id(role_id)
        visor = VisorService.get_by_id(visor_id)
        
        if visor in role.visors:
            raise IllegalOperationError(f"Visor {visor_id} is already assigned to role {role_id}")
        
        try:
            role.visors.append(visor)
            db.session.commit()
            return role
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def remove_visor(cls, role_id, visor_id):
        """Remove a visor from a role.
        
        Args:
            role_id (int): The ID of the role.
            visor_id (int): The ID of the visor to remove.
        
        Returns:
            Role: The updated role instance without access to the visor.
        
        Raises:
            NotFoundError: If the role or visor does not exist.
            IllegalOperationError: If the visor is not assigned to the role or if the operation fails.
        """
        role = cls.get_by_id(role_id)
        visor = VisorService.get_by_id(visor_id)
        
        if visor not in role.visors:
            raise IllegalOperationError(f"Visor {visor_id} is not assigned to role {role_id}")
        
        try:
            role.visors.remove(visor)
            db.session.commit()
            return role
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def add_simulator(cls, role_id, simulator_id):
        """Add a simulator to a role.
        
        Args:
            role_id (int): The ID of the role.
            simulator_id (int): The ID of the simulator to add.
        
        Returns:
            Role: The updated role instance with access to the new simulator.
        
        Raises:
            NotFoundError: If the role or simulator does not exist.
            IllegalOperationError: If the simulator is already assigned to the role or if the operation fails.
        """
        role = cls.get_by_id(role_id)
        simulator = SimulatorService.get_by_id(simulator_id)
        
        if simulator in role.simulators:
            raise IllegalOperationError(f"Simulator {simulator_id} is already assigned to role {role_id}")
        
        try:
            role.simulators.append(simulator)
            db.session.commit()
            return role
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def remove_simulator(cls, role_id, simulator_id):
        """Remove a simulator from a role.
        
        Args:
            role_id (int): The ID of the role.
            simulator_id (int): The ID of the simulator to remove.
        
        Returns:
            Role: The updated role instance without access to the simulator.
        
        Raises:
            NotFoundError: If the role or simulator does not exist.
            IllegalOperationError: If the simulator is not assigned to the role or if the operation fails.
        """
        role = cls.get_by_id(role_id)
        simulator = SimulatorService.get_by_id(simulator_id)
        
        if simulator not in role.simulators:
            raise IllegalOperationError(f"Simulator {simulator_id} is not assigned to role {role_id}")
        
        try:
            role.simulators.remove(simulator)
            db.session.commit()
            return role
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def add_document_presentation(cls, role_id, document_presentation_id):
        """Add a document presentation to a role.
        
        Args:
            role_id (int): The ID of the role.
            document_presentation_id (int): The ID of the document presentation to add.
        
        Returns:
            Role: The updated role instance with access to the new document presentation.
        
        Raises:
            NotFoundError: If the role or document presentation does not exist.
            IllegalOperationError: If the document presentation is already assigned to the role or if the operation fails.
        """
        role = cls.get_by_id(role_id)
        doc = DocumentPresentationService.get_by_id(document_presentation_id)
        
        if doc in role.documents_presentations:
            raise IllegalOperationError(f"Document presentation {document_presentation_id} is already assigned to role {role_id}")
        
        try:
            role.documents_presentations.append(doc)
            db.session.commit()
            return role
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def remove_document_presentation(cls, role_id, document_presentation_id):
        """Remove a document presentation from a role.
        
        Args:
            role_id (int): The ID of the role.
            document_presentation_id (int): The ID of the document presentation to remove.
        
        Returns:
            Role: The updated role instance without access to the document presentation.
        
        Raises:
            NotFoundError: If the role or document presentation does not exist.
            IllegalOperationError: If the document presentation is not assigned to the role or if the operation fails.
        """
        role = cls.get_by_id(role_id)
        doc = DocumentPresentationService.get_by_id(document_presentation_id)
        
        if doc not in role.documents_presentations:
            raise IllegalOperationError(f"Document presentation {document_presentation_id} is not assigned to role {role_id}")
        
        try:
            role.documents_presentations.remove(doc)
            db.session.commit()
            return role
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
