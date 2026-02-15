"""Unit tests for DocumentPresentationRoleRelation."""

import pytest
from app.services.relations.document_presentation_role_relation import DocumentPresentationRoleRelation
from app.services.documents_presentation_service import DocumentPresentationService
from app.services.role_service import RoleService
from app.domain.exceptions import NotFoundError, IllegalOperationError


class TestDocumentPresentationRoleRelationAdd:
    """Tests for adding role to document presentation."""
    
    def test_add_role_to_document_presentation(self, app):
        """Test adding a role to a document presentation."""
        with app.app_context():
            doc = DocumentPresentationService.create(main_title="Q3 Presentation")
            role = RoleService.create(name="Viewer")
            
            doc_result, role_result = DocumentPresentationRoleRelation.add_role_to_document_presentation(doc.id, role.id)
            
            assert doc_result.id == doc.id
            assert role_result.id == role.id
            assert role in doc.roles
    
    def test_add_duplicate_role_raises_error(self, app):
        """Test that adding duplicate role raises error."""
        with app.app_context():
            doc = DocumentPresentationService.create(main_title="Annual Report")
            role = RoleService.create(name="Admin")
            
            DocumentPresentationRoleRelation.add_role_to_document_presentation(doc.id, role.id)
            
            with pytest.raises(IllegalOperationError):
                DocumentPresentationRoleRelation.add_role_to_document_presentation(doc.id, role.id)
    
    def test_add_role_to_nonexistent_document_raises_error(self, app):
        """Test that adding role to nonexistent document raises error."""
        with app.app_context():
            role = RoleService.create(name="Manager")
            
            with pytest.raises(NotFoundError):
                DocumentPresentationRoleRelation.add_role_to_document_presentation(9999, role.id)
    
    def test_add_nonexistent_role_to_document_raises_error(self, app):
        """Test that adding nonexistent role raises error."""
        with app.app_context():
            doc = DocumentPresentationService.create(main_title="Document")
            
            with pytest.raises(NotFoundError):
                DocumentPresentationRoleRelation.add_role_to_document_presentation(doc.id, 9999)


class TestDocumentPresentationRoleRelationRemove:
    """Tests for removing role from document presentation."""
    
    def test_remove_role_from_document_presentation(self, app):
        """Test removing a role from a document presentation."""
        with app.app_context():
            doc = DocumentPresentationService.create(main_title="Quarterly Review")
            role = RoleService.create(name="Analyst")
            DocumentPresentationRoleRelation.add_role_to_document_presentation(doc.id, role.id)
            
            doc_result, role_result = DocumentPresentationRoleRelation.remove_role_from_document_presentation(doc.id, role.id)
            
            assert role not in doc.roles
    
    def test_remove_nonexistent_role_from_document_raises_error(self, app):
        """Test that removing unassigned role raises error."""
        with app.app_context():
            doc = DocumentPresentationService.create(main_title="Report")
            role = RoleService.create(name="Guest")
            
            with pytest.raises(IllegalOperationError):
                DocumentPresentationRoleRelation.remove_role_from_document_presentation(doc.id, role.id)


class TestDocumentPresentationRoleRelationGet:
    """Tests for getting relationships."""
    
    def test_get_all_roles_for_document_presentation(self, app):
        """Test getting all roles for a document presentation."""
        with app.app_context():
            doc = DocumentPresentationService.create(main_title="Shared Document")
            role1 = RoleService.create(name="Role 1")
            role2 = RoleService.create(name="Role 2")
            
            DocumentPresentationRoleRelation.add_role_to_document_presentation(doc.id, role1.id)
            DocumentPresentationRoleRelation.add_role_to_document_presentation(doc.id, role2.id)
            
            roles = DocumentPresentationRoleRelation.get_all_b_for_a(doc.id)
            
            assert len(roles) == 2
            assert role1 in roles
            assert role2 in roles
    
    def test_get_all_document_presentations_for_role(self, app):
        """Test getting all document presentations for a role."""
        with app.app_context():
            doc1 = DocumentPresentationService.create(main_title="Doc 1")
            doc2 = DocumentPresentationService.create(main_title="Doc 2")
            role = RoleService.create(name="PowerUser")
            
            DocumentPresentationRoleRelation.add_role_to_document_presentation(doc1.id, role.id)
            DocumentPresentationRoleRelation.add_role_to_document_presentation(doc2.id, role.id)
            
            docs = DocumentPresentationRoleRelation.get_all_a_for_b(role.id)
            
            assert len(docs) == 2
            assert doc1 in docs
            assert doc2 in docs


class TestDocumentPresentationRoleRelationRemoveAll:
    """Tests for removing all relationships."""
    
    def test_remove_all_roles_for_document_presentation(self, app):
        """Test removing all roles from a document presentation."""
        with app.app_context():
            doc = DocumentPresentationService.create(main_title="Document")
            role1 = RoleService.create(name="R1")
            role2 = RoleService.create(name="R2")
            
            DocumentPresentationRoleRelation.add_role_to_document_presentation(doc.id, role1.id)
            DocumentPresentationRoleRelation.add_role_to_document_presentation(doc.id, role2.id)
            
            DocumentPresentationRoleRelation.remove_all_b_for_a(doc.id)
            
            roles = DocumentPresentationRoleRelation.get_all_b_for_a(doc.id)
            assert len(roles) == 0
    
    def test_remove_all_document_presentations_for_role(self, app):
        """Test removing all document presentations from a role."""
        with app.app_context():
            doc1 = DocumentPresentationService.create(main_title="D1")
            doc2 = DocumentPresentationService.create(main_title="D2")
            role = RoleService.create(name="R")
            
            DocumentPresentationRoleRelation.add_role_to_document_presentation(doc1.id, role.id)
            DocumentPresentationRoleRelation.add_role_to_document_presentation(doc2.id, role.id)
            
            DocumentPresentationRoleRelation.remove_all_a_for_b(role.id)
            
            docs = DocumentPresentationRoleRelation.get_all_a_for_b(role.id)
            assert len(docs) == 0


class TestDocumentPresentationRoleRelationIntegration:
    """Integration tests for DocumentPresentationRoleRelation."""
    
    def test_complete_relationship_lifecycle(self, app):
        """Test complete lifecycle of document-role relationship."""
        with app.app_context():
            doc = DocumentPresentationService.create(main_title="Company Presentation")
            role1 = RoleService.create(name="Executive")
            role2 = RoleService.create(name="Manager")
            
            # Add roles
            DocumentPresentationRoleRelation.add_role_to_document_presentation(doc.id, role1.id)
            DocumentPresentationRoleRelation.add_role_to_document_presentation(doc.id, role2.id)
            
            # Verify
            roles = DocumentPresentationRoleRelation.get_all_b_for_a(doc.id)
            assert len(roles) == 2
            
            # Remove one
            DocumentPresentationRoleRelation.remove_role_from_document_presentation(doc.id, role1.id)
            roles = DocumentPresentationRoleRelation.get_all_b_for_a(doc.id)
            assert len(roles) == 1
            
            # Remove all
            DocumentPresentationRoleRelation.remove_all_b_for_a(doc.id)
            roles = DocumentPresentationRoleRelation.get_all_b_for_a(doc.id)
            assert len(roles) == 0
