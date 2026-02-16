from flask import current_app
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.domain.exceptions import NotFoundError
from app.services.relations.user_role_relation import UserRoleRelation

class BootstrapService:
    @staticmethod
    def initialize_minimals():
        # Create default roles
        roles = {
            "admin": "Usuarios con permisos administrativos para gestionar el sistema y sus contenidos",
            "community": "Cualquier usuario perteneciente a la comunidad académica de la UNAL (Cualquier individuo con correo @unal.edu.co)"
        }
        for role, description in roles.items():
            try:
                RoleService.get_by_name(role)
            except NotFoundError:
                RoleService.create(name=role, description=description)
        
        # Create default admin user with email from environment variable or fallback to a default email
        default_admin_email = current_app.config.get("DEFAULT_ADMIN_EMAIL")
        if default_admin_email:
            try:
                UserService.get_by_id(default_admin_email)
            except NotFoundError:
                admin_user = UserService.create(
                    email=default_admin_email,
                    names="Admin",
                    last_names="User"
                )
                admin_role = RoleService.get_by_name("admin")
                UserRoleRelation.add_role_to_user(user_email=admin_user.email, role_id=admin_role.id)