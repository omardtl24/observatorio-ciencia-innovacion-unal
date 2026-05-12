from app.services.relations.user_role_relation import UserRoleRelation
from app.services.relations.document_presentation_role_relation import DocumentPresentationRoleRelation
from app.services.relations.role_report_relation import RoleReportRelation
from app.services.relations.role_simulator_relation import RoleSimulatorRelation
from app.services.relations.role_data_source_relation import RoleDataSourceRelation
from app.services.relations.role_visor_relation import RoleVisorRelation
from app.services.role_service import RoleService
from app.domain.exceptions import NotFoundError, UnauthorizedError
from flask_jwt_extended import get_jwt_identity # type: ignore


class AccessChecker:
    """Utility class to check user access to various resources based on roles."""

    @staticmethod
    def is_admin(user_email):
        """Check if the user has the 'Administrador' role."""
        try:
            user_roles = UserRoleRelation.get_all_b_for_a(user_email)
            return any(role.name == "Administrador" for role in user_roles)
        except NotFoundError:
            return False
    
    @staticmethod
    def _normalize_resource_type(resource_type):
        normalized = str(resource_type).strip().lower().replace("-", "_")
        if normalized == "datasource":
            return "data_source"
        return normalized

    @staticmethod
    def check_access(user_email, resource_id, resource_type):
        """Check if user has access to a resource based on its type.
        
        Args:
            user_email: The email of the user.
            resource_id: The ID of the resource.
            resource_type: The type of resource ('report', 'simulator', 'visor', 'document').
        
        Returns:
            bool: True if user has access through a role, False otherwise.
        
        Raises:
            ValueError: If resource_type is not recognized.
        """
        resource_type = AccessChecker._normalize_resource_type(resource_type)
        
        if resource_type == "report":
            return AccessChecker._check_report_access(user_email, resource_id)
        elif resource_type == "simulator":
            return AccessChecker._check_simulator_access(user_email, resource_id)
        elif resource_type == "visor":
            return AccessChecker._check_visor_access(user_email, resource_id)
        elif resource_type == "document":
            return AccessChecker._check_document_presentation_access(user_email, resource_id)
        elif resource_type == "data_source":
            return AccessChecker._check_data_source_access(user_email, resource_id)
        else:
            raise ValueError(f"Tipo de recurso no válido: {resource_type}")
    
    @staticmethod
    def _check_report_access(user_email, report_id):
        """Check if user has a role that grants access to a report.
        
        Args:
            user_email: The email of the user.
            report_id: The ID of the report.
        
        Returns:
            bool: True if user has access through a role, False otherwise.
        """
        try:
            user_roles = UserRoleRelation.get_all_b_for_a(user_email)
            for role in user_roles:
                try:
                    if RoleReportRelation.exists(role.id, report_id):
                        return True
                except NotFoundError:
                    continue
            return False
        except NotFoundError:
            return False
    
    @staticmethod
    def _check_simulator_access(user_email, simulator_id):
        """Check if user has a role that grants access to a simulator.
        
        Args:
            user_email: The email of the user.
            simulator_id: The ID of the simulator.
        
        Returns:
            bool: True if user has access through a role, False otherwise.
        """
        try:
            user_roles = UserRoleRelation.get_all_b_for_a(user_email)
            for role in user_roles:
                try:
                    if RoleSimulatorRelation.exists(role.id, simulator_id):
                        return True
                except NotFoundError:
                    continue
            return False
        except NotFoundError:
            return False
    
    @staticmethod
    def _check_visor_access(user_email, visor_id):
        """Check if user has a role that grants access to a visor.
        
        Args:
            user_email: The email of the user.
            visor_id: The ID of the visor.
        
        Returns:
            bool: True if user has access through a role, False otherwise.
        """
        try:
            user_roles = UserRoleRelation.get_all_b_for_a(user_email)
            for role in user_roles:
                try:
                    if RoleVisorRelation.exists(role.id, visor_id):
                        return True
                except NotFoundError:
                    continue
            return False
        except NotFoundError:
            return False
    
    @staticmethod
    def _check_document_presentation_access(user_email, document_id):
        """Check if user has a role that grants access to a document presentation.
        
        Args:
            user_email: The email of the user.
            document_id: The ID of the document presentation.
        
        Returns:
            bool: True if user has access through a role, False otherwise.
        """
        try:
            user_roles = UserRoleRelation.get_all_b_for_a(user_email)
            for role in user_roles:
                try:
                    if DocumentPresentationRoleRelation.exists(document_id, role.id):
                        return True
                except NotFoundError:
                    continue
            return False
        except NotFoundError:
            return False

    @staticmethod
    def _check_data_source_access(user_email, data_source_id):
        """Check if user has a role that grants access to a data source.

        Args:
            user_email: The email of the user.
            data_source_id: The ID of the data source.

        Returns:
            bool: True if user has access through a role, False otherwise.
        """
        try:
            user_roles = UserRoleRelation.get_all_b_for_a(user_email)
            for role in user_roles:
                try:
                    if RoleDataSourceRelation.exists(role.id, data_source_id):
                        return True
                except NotFoundError:
                    continue
            return False
        except NotFoundError:
            return False
    
    @staticmethod
    def grant_admin_access(resource_id, resource_type):
        """Grant admin role access to a resource based on its type.
        
        Args:
            resource_id: The ID of the resource.
            resource_type: The type of resource ('report', 'simulator', 'visor', 'document').
        
        Returns:
            tuple: (admin_role_instance, resource_instance)
        
        Raises:
            ValueError: If resource_type is not recognized.
            NotFoundError: If admin role or resource does not exist.
            IllegalOperationError: If the relationship already exists or operation fails.
        """
        resource_type = AccessChecker._normalize_resource_type(resource_type)
        admin_role = RoleService.get_by_name("Administrador")
        
        if resource_type == "report":
            return AccessChecker._grant_report_admin_access(admin_role.id, resource_id)
        elif resource_type == "simulator":
            return AccessChecker._grant_simulator_admin_access(admin_role.id, resource_id)
        elif resource_type == "visor":
            return AccessChecker._grant_visor_admin_access(admin_role.id, resource_id)
        elif resource_type == "document":
            return AccessChecker._grant_document_presentation_admin_access(admin_role.id, resource_id)
        elif resource_type == "data_source":
            return AccessChecker._grant_data_source_admin_access(admin_role.id, resource_id)
        else:
            raise ValueError(f"Tipo de recurso no válido: {resource_type}")
    
    @staticmethod
    def _grant_report_admin_access(admin_role_id, report_id):
        """Grant admin role access to a report.
        
        Args:
            admin_role_id: The ID of the admin role.
            report_id: The ID of the report.
        
        Returns:
            tuple: (admin_role_instance, report_instance)
        """
        return RoleReportRelation.add(admin_role_id, report_id)
    
    @staticmethod
    def _grant_simulator_admin_access(admin_role_id, simulator_id):
        """Grant admin role access to a simulator.
        
        Args:
            admin_role_id: The ID of the admin role.
            simulator_id: The ID of the simulator.
        
        Returns:
            tuple: (admin_role_instance, simulator_instance)
        """
        return RoleSimulatorRelation.add(admin_role_id, simulator_id)
    
    @staticmethod
    def _grant_visor_admin_access(admin_role_id, visor_id):
        """Grant admin role access to a visor.
        
        Args:
            admin_role_id: The ID of the admin role.
            visor_id: The ID of the visor.
        
        Returns:
            tuple: (admin_role_instance, visor_instance)
        """
        return RoleVisorRelation.add(admin_role_id, visor_id)
    
    @staticmethod
    def _grant_document_presentation_admin_access(admin_role_id, document_id):
        """Grant admin role access to a document presentation.
        
        Args:
            admin_role_id: The ID of the admin role.
            document_id: The ID of the document presentation.
        
        Returns:
            tuple: (document_instance, admin_role_instance)
        """
        return DocumentPresentationRoleRelation.add(document_id, admin_role_id)

    @staticmethod
    def _grant_data_source_admin_access(admin_role_id, data_source_id):
        """Grant admin role access to a data source.

        Args:
            admin_role_id: The ID of the admin role.
            data_source_id: The ID of the data source.

        Returns:
            tuple: (admin_role_instance, data_source_instance)
        """
        return RoleDataSourceRelation.add(admin_role_id, data_source_id)


def assert_admin(error_message="El usuario no tiene permiso para realizar esta acción"):
    """Assert that the current user has admin permissions.
    
    Args:
        error_message (str): Custom error message to display if user lacks permissions.
    
    Raises:
        UnauthorizedError: If the user is not an admin.
    """
    user_email = get_jwt_identity()
    if not AccessChecker.is_admin(user_email):
        raise UnauthorizedError(error_message)




