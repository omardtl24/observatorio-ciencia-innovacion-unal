from app.models.documents_presentation import DocumentPresentation
from app.services.base_service import BaseService


class DocumentPresentationService(BaseService):
    """Service for managing DocumentPresentation CRUD operations.
    
    Note: Relationship operations (add/remove role) are handled by domain-level
    functions in app.domain.relations to prevent circular service dependencies.
    """
    model = DocumentPresentation
