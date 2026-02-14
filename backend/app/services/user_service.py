from app.models.user import User
from app.services.base_service import BaseService

class UserService(BaseService):
    model = User
    