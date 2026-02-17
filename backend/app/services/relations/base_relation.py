from app.models.base import db
from app.domain.exceptions import NotFoundError, IllegalOperationError


class BaseRelation:
    """Base class for managing many-to-many relationships between two entities.
    
    Subclasses must define:
    - model_a: The first model class
    - model_b: The second model class
    - relationship_a: The relationship name on model_a pointing to model_b
    - relationship_b: The relationship name on model_b pointing to model_a
    """
    
    model_a = None
    model_b = None
    relationship_a = None  # e.g., 'roles' on User
    relationship_b = None  # e.g., 'users' on Role
    
    @classmethod
    def get_a_by_id(cls, resource_id):
        """Get an instance of model_a by its ID."""
        instance = db.session.get(cls.model_a, resource_id)
        if not instance:
            raise NotFoundError(f"{cls.model_a.__name__} with id={resource_id} not found")
        return instance
    
    @classmethod
    def get_b_by_id(cls, resource_id):
        """Get an instance of model_b by its ID."""
        instance = db.session.get(cls.model_b, resource_id)
        if not instance:
            raise NotFoundError(f"{cls.model_b.__name__} with id={resource_id} not found")
        return instance
    
    @classmethod
    def add(cls, a_id, b_id):
        """Add a relationship between model_a and model_b.
        
        Args:
            a_id: The ID of the model_a instance.
            b_id: The ID of the model_b instance.
        
        Returns:
            tuple: (model_a_instance, model_b_instance)
        
        Raises:
            NotFoundError: If either instance does not exist.
            IllegalOperationError: If the relationship is already established or if the operation fails.
        """
        instance_a = cls.get_a_by_id(a_id)
        instance_b = cls.get_b_by_id(b_id)
        
        # Check if relationship already exists
        relationship_collection = getattr(instance_a, cls.relationship_a)
        if instance_b in relationship_collection:
            raise IllegalOperationError(
                f"{cls.model_b.__name__} {b_id} is already assigned to {cls.model_a.__name__} {a_id}"
            )
        
        try:
            relationship_collection.append(instance_b)
            db.session.commit()
            return instance_a, instance_b
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def remove(cls, a_id, b_id):
        """Remove a relationship between model_a and model_b.
        
        Args:
            a_id: The ID of the model_a instance.
            b_id: The ID of the model_b instance.
        
        Returns:
            tuple: (model_a_instance, model_b_instance)
        
        Raises:
            NotFoundError: If either instance does not exist.
            IllegalOperationError: If the relationship is not established or if the operation fails.
        """
        instance_a = cls.get_a_by_id(a_id)
        instance_b = cls.get_b_by_id(b_id)
        
        # Check if relationship exists
        relationship_collection = getattr(instance_a, cls.relationship_a)
        if instance_b not in relationship_collection:
            raise IllegalOperationError(
                f"{cls.model_b.__name__} {b_id} is not assigned to {cls.model_a.__name__} {a_id}"
            )
        
        try:
            relationship_collection.remove(instance_b)
            db.session.commit()
            return instance_a, instance_b
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def get_all_b_for_a(cls, a_id):
        """Get all instances of model_b associated with an instance of model_a.
        
        Args:
            a_id: The ID of the model_a instance.
        
        Returns:
            list: All associated instances of model_b.
        
        Raises:
            NotFoundError: If the model_a instance does not exist.
        """
        instance_a = cls.get_a_by_id(a_id)
        return getattr(instance_a, cls.relationship_a)
    
    @classmethod
    def get_all_a_for_b(cls, b_id):
        """Get all instances of model_a associated with an instance of model_b.
        
        Args:
            b_id: The ID of the model_b instance.
        
        Returns:
            list: All associated instances of model_a.
        
        Raises:
            NotFoundError: If the model_b instance does not exist.
        """
        instance_b = cls.get_b_by_id(b_id)
        return getattr(instance_b, cls.relationship_b)
    
    @classmethod
    def exists(cls, a_id, b_id):
        """Check if a relationship exists between a model_a instance and a model_b instance.
        
        Args:
            a_id: The ID of the model_a instance.
            b_id: The ID of the model_b instance.
        
        Returns:
            bool: True if the relationship exists, False otherwise.
        
        Raises:
            NotFoundError: If either instance does not exist.
        """
        instance_a = cls.get_a_by_id(a_id)
        instance_b = cls.get_b_by_id(b_id)
        
        relationship_collection = getattr(instance_a, cls.relationship_a)
        return instance_b in relationship_collection
    
    @classmethod
    def remove_all_b_for_a(cls, a_id):
        """Remove all instances of model_b associated with an instance of model_a.
        
        Args:
            a_id: The ID of the model_a instance.
        
        Returns:
            model_a_instance: The model_a instance with all relationships cleared.
        
        Raises:
            NotFoundError: If the model_a instance does not exist.
            IllegalOperationError: If the operation fails.
        """
        instance_a = cls.get_a_by_id(a_id)
        
        try:
            relationship_collection = getattr(instance_a, cls.relationship_a)
            relationship_collection.clear()
            db.session.commit()
            return instance_a
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def remove_all_a_for_b(cls, b_id):
        """Remove all instances of model_a associated with an instance of model_b.
        
        Args:
            b_id: The ID of the model_b instance.
        
        Returns:
            model_b_instance: The model_b instance with all relationships cleared.
        
        Raises:
            NotFoundError: If the model_b instance does not exist.
            IllegalOperationError: If the operation fails.
        """
        instance_b = cls.get_b_by_id(b_id)
        
        try:
            relationship_collection = getattr(instance_b, cls.relationship_b)
            relationship_collection.clear()
            db.session.commit()
            return instance_b
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
