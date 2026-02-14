from app.models.documents_presentation import DocumentPresentation
from app.services.base_service import BaseService
from app.models.base import db
from app.domain.exceptions import NotFoundError, IllegalOperationError
from app.services.role_service import RoleService

class DocumentPresentationService(BaseService):
    model = DocumentPresentation
    
    @classmethod
    def add_role(cls, document_presentation_id, role_id):
        """Add a role to a document presentation to grant access.
        
        Args:
            document_presentation_id (int): The ID of the document presentation.
            role_id (int): The ID of the role to grant access.
        
        Returns:
            DocumentPresentation: The updated document presentation instance with the new role permission.
        
        Raises:
            NotFoundError: If the document presentation or role does not exist.
            IllegalOperationError: If the role already has access to the document presentation or if the operation fails.
        """
        doc = cls.get_by_id(document_presentation_id)
        role = RoleService.get_by_id(role_id)
        
        if role in doc.roles:
            raise IllegalOperationError(f"Role {role_id} is already assigned to document presentation {document_presentation_id}")
        
        try:
            doc.roles.append(role)
            db.session.commit()
            return doc
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
    
    @classmethod
    def remove_role(cls, document_presentation_id, role_id):
        """Remove a role from a document presentation to revoke access.
        
        Args:
            document_presentation_id (int): The ID of the document presentation.
            role_id (int): The ID of the role to revoke access from.
        
        Returns:
            DocumentPresentation: The updated document presentation instance without the role permission.
        
        Raises:
            NotFoundError: If the document presentation or role does not exist.
            IllegalOperationError: If the role does not have access to the document presentation or if the operation fails.
        """
        doc = cls.get_by_id(document_presentation_id)
        role = RoleService.get_by_id(role_id)
        
        if role not in doc.roles:
            raise IllegalOperationError(f"Role {role_id} is not assigned to document presentation {document_presentation_id}")
        
        try:
            doc.roles.remove(role)
            db.session.commit()
            return doc
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))
