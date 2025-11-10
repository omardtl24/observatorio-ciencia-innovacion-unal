from app.services.base_service import BaseService
from app.services.exceptions import NotFoundError
from app.models.user import User
from app.models.base import db

class UserService(BaseService):
    model = User

    @classmethod
    def get_by_email(cls, email):
        user = User.query.filter_by(email=email).first()
        if not user:
            raise NotFoundError(f"User with email={email} not found")
        return user

    @classmethod
    def update(cls, email, **data):
        user = cls.get_by_email(email)
        try:
            user.update(**data)
            return user
        except Exception as e:
            db.session.rollback()
            raise

    @classmethod
    def delete(cls, email):
        user = cls.get_by_email(email)
        try:
            user.delete()
            return True
        except Exception as e:
            db.session.rollback()
            raise