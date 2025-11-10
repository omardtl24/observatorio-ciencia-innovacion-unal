from app.models.base import db
from app.services.exceptions import NotFoundError, IllegalOperationError

class BaseService:
    model = None  # must be set by child class

    @classmethod
    def create(cls, **data):
        try:
            instance = cls.model.create(**data)
            return instance
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))

    @classmethod
    def get_all(cls):
        return cls.model.query.all()

    @classmethod
    def get_by_id(cls, resource_id):
        instance = cls.model.query.get(resource_id)
        if not instance:
            raise NotFoundError(f"{cls.model.__name__} with id={resource_id} not found")
        return instance

    @classmethod
    def update(cls, resource_id, **data):
        instance = cls.get_by_id(resource_id)

        try:
            instance.update(**data)
            return instance
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))

    @classmethod
    def delete(cls, resource_id):
        instance = cls.get_by_id(resource_id)

        try:
            instance.delete()
            return True
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
