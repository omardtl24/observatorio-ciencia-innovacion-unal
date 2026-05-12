"""Unit tests for RoleVisorRelation."""

import pytest # type: ignore
from app.services.relations.role_visor_relation import RoleVisorRelation
from app.services.role_service import RoleService
from app.services.visor_service import VisorService
from app.domain.exceptions import NotFoundError, IllegalOperationError


class TestRoleVisorRelationAdd:
    """Tests for adding visor to role."""
    
    def test_add_visor_to_role(self, app):
        """Test adding a visor to a role."""
        with app.app_context():
            role = RoleService.create(name="Analyst")
            visor = VisorService.create(title="Sales Visor")
            
            role_result, visor_result = RoleVisorRelation.add_visor_to_role(role.id, visor.id)
            
            assert role_result.id == role.id
            assert visor_result.id == visor.id
            assert visor in role.visors
    
    def test_add_duplicate_visor_raises_error(self, app):
        """Test that adding duplicate visor raises error."""
        with app.app_context():
            role = RoleService.create(name="Manager")
            visor = VisorService.create(title="Marketing Visor")
            
            RoleVisorRelation.add_visor_to_role(role.id, visor.id)
            
            with pytest.raises(IllegalOperationError):
                RoleVisorRelation.add_visor_to_role(role.id, visor.id)
    
    def test_add_visor_to_nonexistent_role_raises_error(self, app):
        """Test that adding visor to nonexistent role raises error."""
        with app.app_context():
            visor = VisorService.create(title="Data Visor")
            
            with pytest.raises(NotFoundError):
                RoleVisorRelation.add_visor_to_role(9999, visor.id)
    
    def test_add_nonexistent_visor_to_role_raises_error(self, app):
        """Test that adding nonexistent visor raises error."""
        with app.app_context():
            role = RoleService.create(name="Admin")
            
            with pytest.raises(NotFoundError):
                RoleVisorRelation.add_visor_to_role(role.id, 9999)


class TestRoleVisorRelationRemove:
    """Tests for removing visor from role."""
    
    def test_remove_visor_from_role(self, app):
        """Test removing a visor from a role."""
        with app.app_context():
            role = RoleService.create(name="Viewer")
            visor = VisorService.create(title="Dashboard")
            RoleVisorRelation.add_visor_to_role(role.id, visor.id)
            
            role_result, visor_result = RoleVisorRelation.remove_visor_from_role(role.id, visor.id)
            
            assert visor not in role.visors
    
    def test_remove_nonexistent_visor_from_role_raises_error(self, app):
        """Test that removing unassigned visor raises error."""
        with app.app_context():
            role = RoleService.create(name="Guest")
            visor = VisorService.create(title="Public Visor")
            
            with pytest.raises(IllegalOperationError):
                RoleVisorRelation.remove_visor_from_role(role.id, visor.id)


class TestRoleVisorRelationGet:
    """Tests for getting relationships."""
    
    def test_get_all_visors_for_role(self, app):
        """Test getting all visors for a role."""
        with app.app_context():
            role = RoleService.create(name="Power User")
            visor1 = VisorService.create(title="Visor 1")
            visor2 = VisorService.create(title="Visor 2")
            
            RoleVisorRelation.add_visor_to_role(role.id, visor1.id)
            RoleVisorRelation.add_visor_to_role(role.id, visor2.id)
            
            visors = RoleVisorRelation.get_all_b_for_a(role.id)
            
            assert len(visors) == 2
            assert visor1 in visors
            assert visor2 in visors
    
    def test_get_all_roles_for_visor(self, app):
        """Test getting all roles for a visor."""
        with app.app_context():
            role1 = RoleService.create(name="Role 1")
            role2 = RoleService.create(name="Role 2")
            visor = VisorService.create(title="Shared Visor")
            
            RoleVisorRelation.add_visor_to_role(role1.id, visor.id)
            RoleVisorRelation.add_visor_to_role(role2.id, visor.id)
            
            roles = RoleVisorRelation.get_all_a_for_b(visor.id)
            
            assert len(roles) == 2
            assert role1 in roles
            assert role2 in roles


class TestRoleVisorRelationRemoveAll:
    """Tests for removing all relationships."""
    
    def test_remove_all_visors_for_role(self, app):
        """Test removing all visors from a role."""
        with app.app_context():
            role = RoleService.create(name="Test Role")
            visor1 = VisorService.create(title="V1")
            visor2 = VisorService.create(title="V2")
            
            RoleVisorRelation.add_visor_to_role(role.id, visor1.id)
            RoleVisorRelation.add_visor_to_role(role.id, visor2.id)
            
            RoleVisorRelation.remove_all_b_for_a(role.id)
            
            visors = RoleVisorRelation.get_all_b_for_a(role.id)
            assert len(visors) == 0
    
    def test_remove_all_roles_for_visor(self, app):
        """Test removing all roles from a visor."""
        with app.app_context():
            role1 = RoleService.create(name="R1")
            role2 = RoleService.create(name="R2")
            visor = VisorService.create(title="V")
            
            RoleVisorRelation.add_visor_to_role(role1.id, visor.id)
            RoleVisorRelation.add_visor_to_role(role2.id, visor.id)
            
            RoleVisorRelation.remove_all_a_for_b(visor.id)
            
            roles = RoleVisorRelation.get_all_a_for_b(visor.id)
            assert len(roles) == 0


class TestRoleVisorRelationIntegration:
    """Integration tests for RoleVisorRelation."""
    
    def test_complete_relationship_lifecycle(self, app):
        """Test complete lifecycle of role-visor relationship."""
        with app.app_context():
            role = RoleService.create(name="SuperUser")
            visor1 = VisorService.create(title="Dashboard 1")
            visor2 = VisorService.create(title="Dashboard 2")
            
            # Add visors
            RoleVisorRelation.add_visor_to_role(role.id, visor1.id)
            RoleVisorRelation.add_visor_to_role(role.id, visor2.id)
            
            # Verify
            visors = RoleVisorRelation.get_all_b_for_a(role.id)
            assert len(visors) == 2
            
            # Remove one
            RoleVisorRelation.remove_visor_from_role(role.id, visor1.id)
            visors = RoleVisorRelation.get_all_b_for_a(role.id)
            assert len(visors) == 1
            
            # Remove all
            RoleVisorRelation.remove_all_b_for_a(role.id)
            visors = RoleVisorRelation.get_all_b_for_a(role.id)
            assert len(visors) == 0
