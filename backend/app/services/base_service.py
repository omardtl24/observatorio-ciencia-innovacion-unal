from app.models.base import db
from app.domain.exceptions import NotFoundError, IllegalOperationError

class BaseService:
    model = None  # must be set by child class

    @classmethod
    def create(cls, **data):
        """Create a new resource instance.
        
        Args:
            **data: Arbitrary keyword arguments containing the fields for the new instance.
        
        Returns:
            The created model instance.
        
        Raises:
            IllegalOperationError: If the creation fails or data validation errors occur.
        """
        try:
            instance = cls.model.create(**data)
            return instance
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))

    @classmethod
    def get_all(cls):
        """Retrieve all instances of the resource.
        
        Returns:
            list: A list of all model instances.
        """
        return cls.model.query.all()

    @classmethod
    def get_by_id(cls, resource_id):
        """Retrieve a resource instance by its ID.
        
        Args:
            resource_id: The unique identifier of the resource.
        
        Returns:
            The model instance with the specified ID.
        
        Raises:
            NotFoundError: If no instance with the given ID exists.
        """
        instance = cls.model.query.get(resource_id)
        if not instance:
            raise NotFoundError(f"{cls.model.__name__} with id={resource_id} not found")
        return instance

    @classmethod
    def update(cls, resource_id, **data):
        """Update an existing resource instance.
        
        Args:
            resource_id: The unique identifier of the resource to update.
            **data: Arbitrary keyword arguments containing the fields to update.
        
        Returns:
            The updated model instance.
        
        Raises:
            NotFoundError: If no instance with the given ID exists.
            IllegalOperationError: If the update fails or data validation errors occur.
        """
        instance = cls.get_by_id(resource_id)

        try:
            instance.update(**data)
            return instance
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))

    @classmethod
    def delete(cls, resource_id):
        """Delete a resource instance.
        
        Args:
            resource_id: The unique identifier of the resource to delete.
        
        Returns:
            bool: True if deletion was successful.
        
        Raises:
            NotFoundError: If no instance with the given ID exists.
            IllegalOperationError: If the deletion fails.
        """
        instance = cls.get_by_id(resource_id)
        try:
            instance.delete()
            return True
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
