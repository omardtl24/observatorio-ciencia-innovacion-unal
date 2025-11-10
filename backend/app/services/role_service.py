from app.services.base_service import BaseService
from app.models.role import Role

class RoleService(BaseService):
    model = Role
