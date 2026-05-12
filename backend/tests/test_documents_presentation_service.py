
import pytest # type: ignore
from datetime import datetime
from app.models.documents_presentation import DocumentPresentation
from app.services.documents_presentation_service import DocumentPresentationService
from app.domain.exceptions import NotFoundError, IllegalOperationError


class TestDocumentPresentationServiceCreate:
    """Tests for DocumentPresentationService.create() method."""
    
    def test_create_document_presentation_with_all_fields(self, app):
        """Test creating a document presentation with all fields provided."""
        with app.app_context():
            doc = DocumentPresentationService.create(
                title="Q4 Report",
                description="Fourth quarter financial report"
            )
            
            assert doc.id is not None
            assert doc.title == "Q4 Report"
            assert doc.description == "Fourth quarter financial report"
            assert doc.created_at is not None
    
    def test_create_document_presentation_with_minimal_fields(self, app):
        """Test creating a document presentation with only required field (title)."""
        with app.app_context():
            doc = DocumentPresentationService.create(title="Presentation")
            
            assert doc.id is not None
            assert doc.title == "Presentation"
            assert doc.description is None
    
    def test_create_document_presentation_without_name_fails(self, app):
        """Test that creating without a title raises an error."""
        with app.app_context():
            with pytest.raises(IllegalOperationError):
                DocumentPresentationService.create(description="No name doc")
    
    def test_create_document_presentation_sets_created_at_timestamp(self, app):
        """Test that created_at is automatically set."""
        with app.app_context():
            before = datetime.utcnow()
            doc = DocumentPresentationService.create(title="Timestamp Doc")
            doc = DocumentPresentationService.get_by_id(doc.id)
            after = datetime.utcnow()
            before = before.replace(microsecond=0)
            after = after.replace(microsecond=0)
            assert doc.created_at is not None
            assert isinstance(doc.created_at, datetime)
            assert before <= doc.created_at <= after


class TestDocumentPresentationServiceRead:
    """Tests for DocumentPresentationService read methods."""
    
    def test_get_all_documents_empty(self, app):
        """Test getting all documents when the database is empty."""
        with app.app_context():
            docs = DocumentPresentationService.get_all()
            assert docs == []
    
    def test_get_all_documents(self, app):
        """Test getting all documents."""
        with app.app_context():
            doc1 = DocumentPresentationService.create(title="Doc 1")
            doc2 = DocumentPresentationService.create(title="Doc 2", description="Second doc")
            
            docs = DocumentPresentationService.get_all()
            
            assert len(docs) == 2
            assert doc1 in docs
            assert doc2 in docs
    
    def test_get_all_documents_as_dict(self, app):
        """Test getting all documents as dictionaries."""
        with app.app_context():
            DocumentPresentationService.create(title="Dict Doc", description="Test description")
            
            docs_dict = DocumentPresentationService.get_all_dict()
            
            assert len(docs_dict) == 1
            assert docs_dict[0]["title"] == "Dict Doc"
    
    def test_get_document_by_id(self, app):
        """Test getting a document by its ID."""
        with app.app_context():
            doc = DocumentPresentationService.create(title="Get By ID Doc")
            
            retrieved = DocumentPresentationService.get_by_id(doc.id)
            
            assert retrieved.id == doc.id
            assert retrieved.title == "Get By ID Doc"
    
    def test_get_document_by_nonexistent_id_raises_error(self, app):
        """Test that getting a nonexistent document raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                DocumentPresentationService.get_by_id(9999)


class TestDocumentPresentationServiceUpdate:
    """Tests for DocumentPresentationService.update() method."""
    
    def test_update_document_name(self, app):
        """Test updating a document's name."""
        with app.app_context():
            doc = DocumentPresentationService.create(title="Old Name", description="Test")
            
            updated = DocumentPresentationService.update(doc.id, title="New Name")
            
            assert updated.title == "New Name"
            assert updated.description == "Test"
    
    def test_update_document_multiple_fields(self, app):
        """Test updating multiple fields."""
        with app.app_context():
            doc = DocumentPresentationService.create(title="Original")
            
            updated = DocumentPresentationService.update(
                doc.id,
                title="Updated Document",
                description="Updated description"
            )
            
            assert updated.title == "Updated Document"
            assert updated.description == "Updated description"
    
    def test_update_nonexistent_document_raises_error(self, app):
        """Test that updating a nonexistent document raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                DocumentPresentationService.update(9999, title="New")
    
    def test_update_preserves_created_at(self, app):
        """Test that updating preserves created_at timestamp."""
        with app.app_context():
            doc = DocumentPresentationService.create(title="Test Doc")
            original_created_at = doc.created_at
            
            DocumentPresentationService.update(doc.id, title="Updated Doc")
            updated = DocumentPresentationService.get_by_id(doc.id)
            
            assert updated.created_at == original_created_at


class TestDocumentPresentationServiceDelete:
    """Tests for DocumentPresentationService.delete() method."""
    
    def test_delete_document(self, app):
        """Test deleting a document."""
        with app.app_context():
            doc = DocumentPresentationService.create(title="Temp Doc")
            doc_id = doc.id
            
            result = DocumentPresentationService.delete(doc_id)
            
            assert result is True
            with pytest.raises(NotFoundError):
                DocumentPresentationService.get_by_id(doc_id)
    
    def test_delete_nonexistent_document_raises_error(self, app):
        """Test that deleting a nonexistent document raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                DocumentPresentationService.delete(9999)
    
    def test_delete_removes_from_database(self, app):
        """Test that deleting removes the document from the database."""
        with app.app_context():
            doc1 = DocumentPresentationService.create(title="Doc 1")
            doc2 = DocumentPresentationService.create(title="Doc 2")
            
            DocumentPresentationService.delete(doc1.id)
            
            docs = DocumentPresentationService.get_all()
            assert len(docs) == 1
            assert docs[0].id == doc2.id


class TestDocumentPresentationServiceIntegration:
    """Integration tests for DocumentPresentationService."""
    
    def test_complete_crud_cycle(self, app):
        """Test a complete CRUD cycle."""
        with app.app_context():
            # Create
            doc = DocumentPresentationService.create(title="CRUD Doc", description="For testing")
            doc_id = doc.id
            
            # Read
            retrieved = DocumentPresentationService.get_by_id(doc_id)
            assert retrieved.title == "CRUD Doc"
            
            # Update
            updated = DocumentPresentationService.update(doc_id, title="Updated Doc")
            assert updated.title == "Updated Doc"
            
            # Verify update
            verified = DocumentPresentationService.get_by_id(doc_id)
            assert verified.title == "Updated Doc"
            
            # Delete
            DocumentPresentationService.delete(doc_id)
            with pytest.raises(NotFoundError):
                DocumentPresentationService.get_by_id(doc_id)
    
    def test_multiple_documents_lifecycle(self, app):
        """Test creating and managing multiple documents."""
        with app.app_context():
            docs = [
                DocumentPresentationService.create(title=f"Doc {i}", description=f"Description {i}")
                for i in range(1, 4)
            ]
            
            assert len(DocumentPresentationService.get_all()) == 3
            
            DocumentPresentationService.delete(docs[0].id)
            assert len(DocumentPresentationService.get_all()) == 2
            
            DocumentPresentationService.create(title="New Doc")
            assert len(DocumentPresentationService.get_all()) == 3
