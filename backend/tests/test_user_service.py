
import pytest
from datetime import datetime
from app.models.user import User
from app.services.user_service import UserService
from app.domain.exceptions import NotFoundError, IllegalOperationError


class TestUserServiceCreate:
    """Tests for UserService.create() method."""
    
    def test_create_user_with_all_fields(self, app):
        """Test creating a user with all fields provided."""
        with app.app_context():
            user = UserService.create(
                email="user@example.com",
                names="John",
                last_names="Doe"
            )
            
            assert user.email == "user@example.com"
            assert user.names == "John"
            assert user.last_names == "Doe"
            assert user.created_at is not None
    
    def test_create_user_with_minimal_fields(self, app):
        """Test creating a user with required fields."""
        with app.app_context():
            user = UserService.create(
                email="test@example.com",
                names="Test",
                last_names="User"
            )
            
            assert user.email == "test@example.com"
            assert user.names == "Test"
            assert user.last_names == "User"
    
    def test_create_user_without_required_field_fails(self, app):
        """Test that creating a user without required fields raises an error."""
        with app.app_context():
            with pytest.raises(IllegalOperationError):
                UserService.create(email="incomplete@example.com")
    
    def test_create_user_sets_created_at_timestamp(self, app):
        """Test that created_at is automatically set."""
        with app.app_context():
            before = datetime.utcnow()
            user = UserService.create(
                email="timestamp@example.com",
                names="Tim",
                last_names="Stamp"
            )
            user = UserService.get_by_id(user.email)
            after = datetime.utcnow()
            before = before.replace(microsecond=0)
            after = after.replace(microsecond=0)
            assert user.created_at is not None
            assert isinstance(user.created_at, datetime)
            assert before <= user.created_at <= after


class TestUserServiceRead:
    """Tests for UserService read methods."""
    
    def test_get_all_users_empty(self, app):
        """Test getting all users when the database is empty."""
        with app.app_context():
            users = UserService.get_all()
            assert users == []
    
    def test_get_all_users(self, app):
        """Test getting all users."""
        with app.app_context():
            user1 = UserService.create(email="user1@example.com", names="User", last_names="One")
            user2 = UserService.create(email="user2@example.com", names="User", last_names="Two")
            
            users = UserService.get_all()
            
            assert len(users) == 2
            assert user1 in users
            assert user2 in users
    
    def test_get_all_users_as_dict(self, app):
        """Test getting all users as dictionaries."""
        with app.app_context():
            UserService.create(email="dict@example.com", names="Dict", last_names="User")
            
            users_dict = UserService.get_all_dict()
            
            assert len(users_dict) == 1
            assert users_dict[0]["email"] == "dict@example.com"
            assert users_dict[0]["names"] == "Dict"
    
    def test_get_user_by_email(self, app):
        """Test getting a user by email."""
        with app.app_context():
            user = UserService.create(email="find@example.com", names="Find", last_names="Me")
            
            retrieved = UserService.get_by_id(user.email)
            
            assert retrieved.email == user.email
            assert retrieved.names == "Find"
    
    def test_get_user_by_nonexistent_email_raises_error(self, app):
        """Test that getting a nonexistent user raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                UserService.get_by_id("nonexistent@example.com")


class TestUserServiceUpdate:
    """Tests for UserService.update() method."""
    
    def test_update_user_names(self, app):
        """Test updating a user's names."""
        with app.app_context():
            user = UserService.create(email="update@example.com", names="Old", last_names="Name")
            
            updated = UserService.update(user.email, names="New")
            
            assert updated.names == "New"
            assert updated.last_names == "Name"
    
    def test_update_user_multiple_fields(self, app):
        """Test updating multiple fields."""
        with app.app_context():
            user = UserService.create(email="multi@example.com", names="First", last_names="Last")
            
            updated = UserService.update(
                user.email,
                names="Updated First",
                last_names="Updated Last"
            )
            
            assert updated.names == "Updated First"
            assert updated.last_names == "Updated Last"
    
    def test_update_nonexistent_user_raises_error(self, app):
        """Test that updating a nonexistent user raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                UserService.update("nonexistent@example.com", names="New")
    
    def test_update_preserves_created_at(self, app):
        """Test that updating preserves created_at timestamp."""
        with app.app_context():
            user = UserService.create(email="preserve@example.com", names="Test", last_names="User")
            original_created_at = user.created_at
            
            UserService.update(user.email, names="Updated")
            updated = UserService.get_by_id(user.email)
            
            assert updated.created_at == original_created_at


class TestUserServiceDelete:
    """Tests for UserService.delete() method."""
    
    def test_delete_user(self, app):
        """Test deleting a user."""
        with app.app_context():
            user = UserService.create(email="delete@example.com", names="Delete", last_names="Me")
            user_email = user.email
            
            result = UserService.delete(user_email)
            
            assert result is True
            with pytest.raises(NotFoundError):
                UserService.get_by_id(user_email)
    
    def test_delete_nonexistent_user_raises_error(self, app):
        """Test that deleting a nonexistent user raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                UserService.delete("nonexistent@example.com")
    
    def test_delete_removes_from_database(self, app):
        """Test that deleting removes the user from the database."""
        with app.app_context():
            user1 = UserService.create(email="user1@delete.com", names="User", last_names="One")
            user2 = UserService.create(email="user2@delete.com", names="User", last_names="Two")
            
            UserService.delete(user1.email)
            
            users = UserService.get_all()
            assert len(users) == 1
            assert users[0].email == user2.email


class TestUserServiceIntegration:
    """Integration tests for UserService."""
    
    def test_complete_crud_cycle(self, app):
        """Test a complete CRUD cycle."""
        with app.app_context():
            # Create
            user = UserService.create(
                email="crud@example.com",
                names="John",
                last_names="Doe"
            )
            user_email = user.email
            
            # Read
            retrieved = UserService.get_by_id(user_email)
            assert retrieved.names == "John"
            
            # Update
            updated = UserService.update(user_email, names="Jane")
            assert updated.names == "Jane"
            
            # Verify update
            verified = UserService.get_by_id(user_email)
            assert verified.names == "Jane"
            
            # Delete
            UserService.delete(user_email)
            with pytest.raises(NotFoundError):
                UserService.get_by_id(user_email)
    
    def test_multiple_users_lifecycle(self, app):
        """Test creating and managing multiple users."""
        with app.app_context():
            users = [
                UserService.create(
                    email=f"user{i}@example.com",
                    names=f"User{i}",
                    last_names=f"Last{i}"
                )
                for i in range(1, 4)
            ]
            
            assert len(UserService.get_all()) == 3
            
            UserService.delete(users[0].email)
            assert len(UserService.get_all()) == 2
            
            UserService.create(email="user4@example.com", names="User4", last_names="Last4")
            assert len(UserService.get_all()) == 3
