
import pytest
from datetime import datetime
from app.models.visor import Visor
from app.services.visor_service import VisorService
from app.domain.exceptions import NotFoundError, IllegalOperationError
from app.models.base import db


class TestVisorServiceCreate:
    """Tests for VisorService.create() method."""
    
    def test_create_visor_with_all_fields(self, app):
        """Test creating a visor with all fields provided."""
        with app.app_context():
            visor_data = {
                "main_title": "Test Visor",
                "auxiliary_title": "Test Aux Title",
                "description": "A test visor",
                "type": "analytics",
                "visor_url": "http://example.com/visor",
                "updated_at": datetime.utcnow()
            }
            
            visor = VisorService.create(**visor_data)
            
            assert visor.id is not None
            assert visor.main_title == "Test Visor"
            assert visor.auxiliary_title == "Test Aux Title"
            assert visor.description == "A test visor"
            assert visor.type == "analytics"
            assert visor.visor_url == "http://example.com/visor"
            assert visor.created_at is not None
            assert isinstance(visor.created_at, datetime)
    
    def test_create_visor_with_minimal_fields(self, app):
        """Test creating a visor with only required field (main_title)."""
        with app.app_context():
            visor_data = {
                "main_title": "Minimal Visor",
                "updated_at": datetime.utcnow()
            }
            
            visor = VisorService.create(**visor_data)
            
            assert visor.id is not None
            assert visor.main_title == "Minimal Visor"
            assert visor.auxiliary_title is None
            assert visor.description is None
            assert visor.type is None
            assert visor.visor_url is None
            assert visor.created_at is not None
    
    def test_create_visor_without_name_fails(self, app):
        """Test that creating a visor without a main_title raises an error."""
        with app.app_context():
            visor_data = {
                "description": "A visor without name",
                "updated_at": datetime.utcnow()
            }
            
            with pytest.raises(IllegalOperationError):
                VisorService.create(**visor_data)
    
    def test_create_visor_sets_created_at_timestamp(self, app):
        """Test that created_at is automatically set when creating a visor."""
        with app.app_context():
            before_creation = datetime.utcnow()
            
            visor_data = {
                "main_title": "Timestamp Test Visor",
                "updated_at": datetime.utcnow()
            }
            visor = VisorService.create(**visor_data)
            # Reload from database to get actual datetime values
            visor = VisorService.get_by_id(visor.id)
            
            after_creation = datetime.utcnow()

            before_creation = before_creation.replace(microsecond=0)
            after_creation = after_creation.replace(microsecond=0)
            
            assert visor.created_at is not None
            assert isinstance(visor.created_at, datetime)
            assert before_creation <= visor.created_at <= after_creation


class TestVisorServiceRead:
    """Tests for VisorService read methods (get_all, get_by_id)."""
    
    def test_get_all_visors_empty(self, app):
        """Test getting all visors when the database is empty."""
        with app.app_context():
            visors = VisorService.get_all()
            assert visors == []
    
    def test_get_all_visors(self, app):
        """Test getting all visors."""
        with app.app_context():
            # Create multiple visors
            visor1 = VisorService.create(
                main_title="Visor 1",
                updated_at=datetime.utcnow()
            )
            visor2 = VisorService.create(
                main_title="Visor 2",
                description="Second visor",
                updated_at=datetime.utcnow()
            )
            
            visors = VisorService.get_all()
            
            assert len(visors) == 2
            assert visor1 in visors
            assert visor2 in visors
    
    def test_get_all_visors_as_dict(self, app):
        """Test getting all visors as dictionaries."""
        with app.app_context():
            visor = VisorService.create(
                main_title="Dict Visor",
                type="analytics",
                updated_at=datetime.utcnow()
            )
            
            visors_dict = VisorService.get_all_dict()
            
            assert len(visors_dict) == 1
            assert visors_dict[0]["main_title"] == "Dict Visor"
            assert visors_dict[0]["type"] == "analytics"
            assert "id" in visors_dict[0]
            assert "created_at" in visors_dict[0]
    
    def test_get_all_visors_dict_with_include(self, app):
        """Test getting all visors as dictionaries with field filtering."""
        with app.app_context():
            VisorService.create(
                main_title="Include Test Visor",
                description="Test description",
                type="report",
                updated_at=datetime.utcnow()
            )
            
            visors_dict = VisorService.get_all_dict(include=["id", "main_title", "type"])
            
            assert len(visors_dict) == 1
            assert "id" in visors_dict[0]
            assert "main_title" in visors_dict[0]
            assert "type" in visors_dict[0]
            assert "description" not in visors_dict[0]
    
    def test_get_all_visors_dict_with_exclude(self, app):
        """Test getting all visors as dictionaries with field exclusion."""
        with app.app_context():
            VisorService.create(
                main_title="Exclude Test Visor",
                description="Test description",
                updated_at=datetime.utcnow()
            )
            
            visors_dict = VisorService.get_all_dict(exclude=["created_at", "updated_at"])
            
            assert len(visors_dict) == 1
            assert "main_title" in visors_dict[0]
            assert "description" in visors_dict[0]
            assert "created_at" not in visors_dict[0]
            assert "updated_at" not in visors_dict[0]
    
    def test_get_visor_by_id(self, app):
        """Test getting a visor by its ID."""
        with app.app_context():
            visor = VisorService.create(
                main_title="Get By ID Visor",
                updated_at=datetime.utcnow()
            )
            
            retrieved_visor = VisorService.get_by_id(visor.id)
            
            assert retrieved_visor.id == visor.id
            assert retrieved_visor.main_title == "Get By ID Visor"
    
    def test_get_visor_by_nonexistent_id_raises_error(self, app):
        """Test that getting a visor with a nonexistent ID raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                VisorService.get_by_id(9999)


class TestVisorServiceUpdate:
    """Tests for VisorService.update() method."""
    
    def test_update_visor_single_field(self, app):
        """Test updating a single field of a visor."""
        with app.app_context():
            visor = VisorService.create(
                main_title="Original Name",
                updated_at=datetime.utcnow()
            )
            original_id = visor.id
            
            updated_visor = VisorService.update(
                visor.id,
                main_title="Updated Name",
                updated_at=datetime.utcnow()
            )
            
            assert updated_visor.id == original_id
            assert updated_visor.main_title == "Updated Name"
    
    def test_update_visor_multiple_fields(self, app):
        """Test updating multiple fields of a visor."""
        with app.app_context():
            visor = VisorService.create(
                main_title="Original Visor",
                description="Original description",
                type="old_type",
                updated_at=datetime.utcnow()
            )
            
            updated_visor = VisorService.update(
                visor.id,
                main_title="New Visor Name",
                description="New description",
                type="new_type",
                visor_url="http://new-url.com",
                updated_at=datetime.utcnow()
            )
            
            assert updated_visor.main_title == "New Visor Name"
            assert updated_visor.description == "New description"
            assert updated_visor.type == "new_type"
            assert updated_visor.visor_url == "http://new-url.com"
    
    def test_update_nonexistent_visor_raises_error(self, app):
        """Test that updating a nonexistent visor raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                VisorService.update(9999, main_title="New Name")
    
    def test_update_preserves_created_at(self, app):
        """Test that updating a visor preserves its created_at timestamp."""
        with app.app_context():
            visor = VisorService.create(
                main_title="Test Visor",
                updated_at=datetime.utcnow()
            )
            original_created_at = visor.created_at
            
            VisorService.update(visor.id, main_title="Updated Name")
            updated_visor = VisorService.get_by_id(visor.id)
            
            assert updated_visor.created_at == original_created_at


class TestVisorServiceDelete:
    """Tests for VisorService.delete() method."""
    
    def test_delete_visor(self, app):
        """Test deleting a visor."""
        with app.app_context():
            visor = VisorService.create(
                main_title="Delete Test Visor",
                updated_at=datetime.utcnow()
            )
            visor_id = visor.id
            
            result = VisorService.delete(visor_id)
            
            assert result is True
            with pytest.raises(NotFoundError):
                VisorService.get_by_id(visor_id)
    
    def test_delete_nonexistent_visor_raises_error(self, app):
        """Test that deleting a nonexistent visor raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                VisorService.delete(9999)
    
    def test_delete_removes_from_database(self, app):
        """Test that deleting a visor removes it from the database."""
        with app.app_context():
            visor1 = VisorService.create(
                main_title="Visor 1",
                updated_at=datetime.utcnow()
            )
            visor2 = VisorService.create(
                main_title="Visor 2",
                updated_at=datetime.utcnow()
            )
            
            VisorService.delete(visor1.id)
            
            visors = VisorService.get_all()
            assert len(visors) == 1
            assert visors[0].id == visor2.id


class TestVisorServiceIntegration:
    """Integration tests for VisorService combining multiple operations."""
    
    def test_complete_crud_cycle(self, app):
        """Test a complete CRUD cycle: Create, Read, Update, Delete."""
        with app.app_context():
            # Create
            visor = VisorService.create(
                main_title="CRUD Test Visor",
                description="Test description",
                type="analytics",
                visor_url="http://test.com",
                updated_at=datetime.utcnow()
            )
            visor_id = visor.id
            
            # Read
            retrieved = VisorService.get_by_id(visor_id)
            assert retrieved.main_title == "CRUD Test Visor"
            
            # Update
            updated = VisorService.update(
                visor_id,
                main_title="Updated CRUD Visor",
                updated_at=datetime.utcnow()
            )
            assert updated.main_title == "Updated CRUD Visor"
            
            # Verify update
            verified = VisorService.get_by_id(visor_id)
            assert verified.main_title == "Updated CRUD Visor"
            
            # Delete
            VisorService.delete(visor_id)
            with pytest.raises(NotFoundError):
                VisorService.get_by_id(visor_id)
    
    def test_get_all_after_operations(self, app):
        """Test get_all after creating, updating, and deleting visors."""
        with app.app_context():
            # Create 3 visors
            visors = [
                VisorService.create(main_title=f"Visor {i}", updated_at=datetime.utcnow())
                for i in range(1, 4)
            ]
            
            assert len(VisorService.get_all()) == 3
            
            # Delete one
            VisorService.delete(visors[0].id)
            assert len(VisorService.get_all()) == 2
            
            # Create another
            VisorService.create(main_title="Visor 4", updated_at=datetime.utcnow())
            assert len(VisorService.get_all()) == 3
    
    def test_multiple_visors_with_different_data(self, app):
        """Test creating and retrieving multiple visors with different data."""
        with app.app_context():
            visor_data_list = [
                {"main_title": "Analytics Visor", "type": "analytics", "description": "For analytics"},
                {"main_title": "Report Visor", "type": "report", "description": "For reports"},
                {"main_title": "Dashboard Visor", "type": "dashboard", "description": "For dashboards"},
            ]
            
            created_visors = []
            for data in visor_data_list:
                data["updated_at"] = datetime.utcnow()
                created_visors.append(VisorService.create(**data))
            
            all_visors = VisorService.get_all()
            
            assert len(all_visors) == 3
            titles = [v.main_title for v in all_visors]
            assert "Analytics Visor" in titles
            assert "Report Visor" in titles
            assert "Dashboard Visor" in titles
