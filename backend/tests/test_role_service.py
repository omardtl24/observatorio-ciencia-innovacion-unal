
import pytest
from datetime import datetime
from app.models.role import Role
from app.services.role_service import RoleService
from app.domain.exceptions import NotFoundError, IllegalOperationError


class TestRoleServiceCreate:
    """Tests for RoleService.create() method."""
    
    def test_create_role_with_all_fields(self, app):
        """Test creating a role with all fields provided."""
        with app.app_context():
            role = RoleService.create(
                name="Admin",
                description="Administrator role with full access"
            )
            
            assert role.id is not None
            assert role.name == "Admin"
            assert role.description == "Administrator role with full access"
            assert role.created_at is not None
    
    def test_create_role_with_minimal_fields(self, app):
        """Test creating a role with only required field (name)."""
        with app.app_context():
            role = RoleService.create(name="User")
            
            assert role.id is not None
            assert role.name == "User"
            assert role.description is None
    
    def test_create_role_without_name_fails(self, app):
        """Test that creating a role without a name raises an error."""
        with app.app_context():
            with pytest.raises(IllegalOperationError):
                RoleService.create(description="No name role")
    
    def test_create_role_sets_created_at_timestamp(self, app):
        """Test that created_at is automatically set."""
        with app.app_context():
            before = datetime.utcnow()
            role = RoleService.create(name="Editor")
            role = RoleService.get_by_id(role.id)
            after = datetime.utcnow()
            before = before.replace(microsecond=0)
            after = after.replace(microsecond=0)
            assert role.created_at is not None
            assert isinstance(role.created_at, datetime)
            assert before <= role.created_at <= after


class TestRoleServiceRead:
    """Tests for RoleService read methods."""
    
    def test_get_all_roles_empty(self, app):
        """Test getting all roles when the database is empty."""
        with app.app_context():
            roles = RoleService.get_all()
            assert roles == []
    
    def test_get_all_roles(self, app):
        """Test getting all roles."""
        with app.app_context():
            role1 = RoleService.create(name="Admin")
            role2 = RoleService.create(name="User")
            
            roles = RoleService.get_all()
            
            assert len(roles) == 2
            assert role1 in roles
            assert role2 in roles
    
    def test_get_all_roles_as_dict(self, app):
        """Test getting all roles as dictionaries."""
        with app.app_context():
            RoleService.create(name="Editor", description="Editing role")
            
            roles_dict = RoleService.get_all_dict()
            
            assert len(roles_dict) == 1
            assert roles_dict[0]["name"] == "Editor"
    
    def test_get_role_by_id(self, app):
        """Test getting a role by its ID."""
        with app.app_context():
            role = RoleService.create(name="Viewer")
            
            retrieved = RoleService.get_by_id(role.id)
            
            assert retrieved.id == role.id
            assert retrieved.name == "Viewer"
    
    def test_get_role_by_nonexistent_id_raises_error(self, app):
        """Test that getting a nonexistent role raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                RoleService.get_by_id(9999)


class TestRoleServiceUpdate:
    """Tests for RoleService.update() method."""
    
    def test_update_role_name(self, app):
        """Test updating a role's name."""
        with app.app_context():
            role = RoleService.create(name="Old Name", description="Test")
            
            updated = RoleService.update(role.id, name="New Name")
            
            assert updated.name == "New Name"
            assert updated.description == "Test"
    
    def test_update_role_multiple_fields(self, app):
        """Test updating multiple fields."""
        with app.app_context():
            role = RoleService.create(name="Admin")
            
            updated = RoleService.update(
                role.id,
                name="Administrator",
                description="Full system access"
            )
            
            assert updated.name == "Administrator"
            assert updated.description == "Full system access"
    
    def test_update_nonexistent_role_raises_error(self, app):
        """Test that updating a nonexistent role raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                RoleService.update(9999, name="New")
    
    def test_update_preserves_created_at(self, app):
        """Test that updating preserves created_at timestamp."""
        with app.app_context():
            role = RoleService.create(name="Test Role")
            original_created_at = role.created_at
            
            RoleService.update(role.id, name="Updated Role")
            updated = RoleService.get_by_id(role.id)
            
            assert updated.created_at == original_created_at


class TestRoleServiceDelete:
    """Tests for RoleService.delete() method."""
    
    def test_delete_role(self, app):
        """Test deleting a role."""
        with app.app_context():
            role = RoleService.create(name="Temp Role")
            role_id = role.id
            
            result = RoleService.delete(role_id)
            
            assert result is True
            with pytest.raises(NotFoundError):
                RoleService.get_by_id(role_id)
    
    def test_delete_nonexistent_role_raises_error(self, app):
        """Test that deleting a nonexistent role raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                RoleService.delete(9999)
    
    def test_delete_removes_from_database(self, app):
        """Test that deleting removes the role from the database."""
        with app.app_context():
            role1 = RoleService.create(name="Role 1")
            role2 = RoleService.create(name="Role 2")
            
            RoleService.delete(role1.id)
            
            roles = RoleService.get_all()
            assert len(roles) == 1
            assert roles[0].id == role2.id


class TestRoleServiceIntegration:
    """Integration tests for RoleService."""
    
    def test_complete_crud_cycle(self, app):
        """Test a complete CRUD cycle."""
        with app.app_context():
            # Create
            role = RoleService.create(name="Test Role", description="For testing")
            role_id = role.id
            
            # Read
            retrieved = RoleService.get_by_id(role_id)
            assert retrieved.name == "Test Role"
            
            # Update
            updated = RoleService.update(role_id, name="Updated Role")
            assert updated.name == "Updated Role"
            
            # Verify update
            verified = RoleService.get_by_id(role_id)
            assert verified.name == "Updated Role"
            
            # Delete
            RoleService.delete(role_id)
            with pytest.raises(NotFoundError):
                RoleService.get_by_id(role_id)
    
    def test_multiple_roles_lifecycle(self, app):
        """Test creating and managing multiple roles."""
        with app.app_context():
            roles = [
                RoleService.create(name=f"Role {i}", description=f"Description {i}")
                for i in range(1, 4)
            ]
            
            assert len(RoleService.get_all()) == 3
            
            RoleService.delete(roles[0].id)
            assert len(RoleService.get_all()) == 2
            
            RoleService.create(name="New Role")
            assert len(RoleService.get_all()) == 3
