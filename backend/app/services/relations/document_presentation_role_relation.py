"""Relationship management for DocumentPresentation and Role."""

from app.models.documents_presentation import DocumentPresentation
from app.models.role import Role
from app.services.relations.base_relation import BaseRelation


class DocumentPresentationRoleRelation(BaseRelation):
    """Manage many-to-many relationships between DocumentPresentation and Role."""
    
    model_a = DocumentPresentation
    model_b = Role
    relationship_a = 'roles'
    relationship_b = 'documents_presentations'
    
    @classmethod
    def add_role_to_document_presentation(cls, document_presentation_id, role_id):
        """Add a role to a document presentation.
        
        Args:
            document_presentation_id (int): The ID of the document presentation.
            role_id (int): The ID of the role to add.
        
        Returns:
            tuple: (document_presentation_instance, role_instance)
        """
        return cls.add(document_presentation_id, role_id)
    
    @classmethod
    def remove_role_from_document_presentation(cls, document_presentation_id, role_id):
        """Remove a role from a document presentation.
        
        Args:
            document_presentation_id (int): The ID of the document presentation.
            role_id (int): The ID of the role to remove.
        
        Returns:
            tuple: (document_presentation_instance, role_instance)
        """
        return cls.remove(document_presentation_id, role_id)
