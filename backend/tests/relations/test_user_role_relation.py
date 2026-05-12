"""Unit tests for UserRoleRelation."""

import pytest # type: ignore
from app.services.relations.user_role_relation import UserRoleRelation
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.domain.exceptions import NotFoundError, IllegalOperationError


class TestUserRoleRelationAdd:
    """Tests for adding role to user."""
    
    def test_add_role_to_user(self, app):
        """Test adding a role to a user."""
        with app.app_context():
            user = UserService.create(email="test@example.com", names="Test", last_names="User")
            role = RoleService.create(name="Admin")
            
            user_result, role_result = UserRoleRelation.add_role_to_user(user.email, role.id)
            
            assert user_result.email == user.email
            assert role_result.id == role.id
            assert role in user.roles
    
    def test_add_role_to_user_by_id(self, app):
        """Test adding a role to a user using base add method."""
        with app.app_context():
            user = UserService.create(email="test2@example.com", names="Test", last_names="User")
            role = RoleService.create(name="Editor")
            
            user_result, role_result = UserRoleRelation.add(user.email, role.id)
            
            assert role_result in user_result.roles
    
    def test_add_duplicate_role_raises_error(self, app):
        """Test that adding duplicate role raises error."""
        with app.app_context():
            user = UserService.create(email="test3@example.com", names="Test", last_names="User")
            role = RoleService.create(name="Viewer")
            
            UserRoleRelation.add_role_to_user(user.email, role.id)
            
            with pytest.raises(IllegalOperationError):
                UserRoleRelation.add_role_to_user(user.email, role.id)
    
    def test_add_role_to_nonexistent_user_raises_error(self, app):
        """Test that adding role to nonexistent user raises error."""
        with app.app_context():
            role = RoleService.create(name="Admin")
            
            with pytest.raises(NotFoundError):
                UserRoleRelation.add_role_to_user("nonexistent@example.com", role.id)
    
    def test_add_nonexistent_role_to_user_raises_error(self, app):
        """Test that adding nonexistent role raises error."""
        with app.app_context():
            user = UserService.create(email="test4@example.com", names="Test", last_names="User")
            
            with pytest.raises(NotFoundError):
                UserRoleRelation.add_role_to_user(user.email, 9999)


class TestUserRoleRelationRemove:
    """Tests for removing role from user."""
    
    def test_remove_role_from_user(self, app):
        """Test removing a role from a user."""
        with app.app_context():
            user = UserService.create(email="test5@example.com", names="Test", last_names="User")
            role = RoleService.create(name="Manager")
            UserRoleRelation.add_role_to_user(user.email, role.id)
            
            role_result, user_result = UserRoleRelation.remove_role_from_user(user.email, role.id)
            
            assert role not in user.roles
    
    def test_remove_nonexistent_role_from_user_raises_error(self, app):
        """Test that removing unassigned role raises error."""
        with app.app_context():
            user = UserService.create(email="test6@example.com", names="Test", last_names="User")
            role = RoleService.create(name="Support")
            
            with pytest.raises(IllegalOperationError):
                UserRoleRelation.remove_role_from_user(user.email, role.id)


class TestUserRoleRelationGet:
    """Tests for getting relationships."""
    
    def test_get_all_roles_for_user(self, app):
        """Test getting all roles for a user."""
        with app.app_context():
            user = UserService.create(email="test7@example.com", names="Test", last_names="User")
            role1 = RoleService.create(name="Admin")
            role2 = RoleService.create(name="Editor")
            
            UserRoleRelation.add_role_to_user(user.email, role1.id)
            UserRoleRelation.add_role_to_user(user.email, role2.id)
            
            roles = UserRoleRelation.get_all_b_for_a(user.email)
            
            assert len(roles) == 2
            assert role1 in roles
            assert role2 in roles
    
    def test_get_all_users_for_role(self, app):
        """Test getting all users for a role."""
        with app.app_context():
            user1 = UserService.create(email="user1@example.com", names="User", last_names="One")
            user2 = UserService.create(email="user2@example.com", names="User", last_names="Two")
            role = RoleService.create(name="Developer")
            
            UserRoleRelation.add_role_to_user(user1.email, role.id)
            UserRoleRelation.add_role_to_user(user2.email, role.id)
            
            users = UserRoleRelation.get_all_a_for_b(role.id)
            
            assert len(users) == 2
            assert user1 in users
            assert user2 in users
    
    def test_get_user_by_email(self, app):
        """Test getting a user by email."""
        with app.app_context():
            user = UserService.create(email="findme@example.com", names="Find", last_names="Me")
            
            found_user = UserRoleRelation.get_user_by_email(user.email)
            
            assert found_user.email == user.email
    
    def test_get_user_by_nonexistent_email_raises_error(self, app):
        """Test that getting nonexistent user by email raises error."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                UserRoleRelation.get_user_by_email("nonexistent@example.com")


class TestUserRoleRelationRemoveAll:
    """Tests for removing all relationships."""
    
    def test_remove_all_roles_for_user(self, app):
        """Test removing all roles from a user."""
        with app.app_context():
            user = UserService.create(email="test8@example.com", names="Test", last_names="User")
            role1 = RoleService.create(name="Role1")
            role2 = RoleService.create(name="Role2")
            
            UserRoleRelation.add_role_to_user(user.email, role1.id)
            UserRoleRelation.add_role_to_user(user.email, role2.id)
            
            UserRoleRelation.remove_all_b_for_a(user.email)
            
            roles = UserRoleRelation.get_all_b_for_a(user.email)
            assert len(roles) == 0
    
    def test_remove_all_users_for_role(self, app):
        """Test removing all users from a role."""
        with app.app_context():
            user1 = UserService.create(email="user3@example.com", names="User", last_names="Three")
            user2 = UserService.create(email="user4@example.com", names="User", last_names="Four")
            role = RoleService.create(name="Team")
            
            UserRoleRelation.add_role_to_user(user1.email, role.id)
            UserRoleRelation.add_role_to_user(user2.email, role.id)
            
            UserRoleRelation.remove_all_a_for_b(role.id)
            
            users = UserRoleRelation.get_all_a_for_b(role.id)
            assert len(users) == 0


class TestUserRoleRelationIntegration:
    """Integration tests for UserRoleRelation."""
    
    def test_complete_relationship_lifecycle(self, app):
        """Test complete lifecycle of user-role relationship."""
        with app.app_context():
            # Create entities
            user = UserService.create(email="lifecycle@example.com", names="Life", last_names="Cycle")
            role1 = RoleService.create(name="Junior")
            role2 = RoleService.create(name="Senior")
            
            # Add roles
            UserRoleRelation.add_role_to_user(user.email, role1.id)
            UserRoleRelation.add_role_to_user(user.email, role2.id)
            
            # Verify
            roles = UserRoleRelation.get_all_b_for_a(user.email)
            assert len(roles) == 2
            
            # Remove one
            UserRoleRelation.remove_role_from_user(user.email, role1.id)
            roles = UserRoleRelation.get_all_b_for_a(user.email)
            assert len(roles) == 1
            assert role2 in roles
            
            # Remove all
            UserRoleRelation.remove_all_b_for_a(user.email)
            roles = UserRoleRelation.get_all_b_for_a(user.email)
            assert len(roles) == 0
