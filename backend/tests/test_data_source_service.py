
import pytest
from datetime import datetime
from app.models.data_source import DataSource
from app.services.data_source_service import DataSourceService
from app.domain.exceptions import NotFoundError, IllegalOperationError


class TestDataSourceServiceCreate:
    """Tests for DataSourceService.create() method."""
    
    def test_create_data_source_with_all_fields(self, app, test_file):
        """Test creating a data source with all fields provided."""
        with app.app_context():
            data_source = DataSourceService.create(
                name="External API",
                description="Third-party API endpoint",
                file_id=test_file.id
            )
            
            assert data_source.id is not None
            assert data_source.name == "External API"
            assert data_source.description == "Third-party API endpoint"
            assert data_source.created_at is not None
    
    def test_create_data_source_with_minimal_fields(self, app, test_file):
        """Test creating a data source with only required field (name)."""
        with app.app_context():
            data_source = DataSourceService.create(name="Database", file_id=test_file.id)
            
            assert data_source.id is not None
            assert data_source.name == "Database"
            assert data_source.description is None
    
    def test_create_data_source_without_name_fails(self, app, test_file):
        """Test that creating a data source without a name raises an error."""
        with app.app_context():
            with pytest.raises(IllegalOperationError):
                DataSourceService.create(description="No name source", file_id=test_file.id)
    
    def test_create_data_source_sets_created_at_timestamp(self, app, test_file):
        """Test that created_at is automatically set."""
        with app.app_context():
            before = datetime.utcnow()
            data_source = DataSourceService.create(name="Timestamp Source", file_id=test_file.id)
            data_source = DataSourceService.get_by_id(data_source.id)
            after = datetime.utcnow()
            before = before.replace(microsecond=0)
            after = after.replace(microsecond=0)
            assert data_source.created_at is not None
            assert isinstance(data_source.created_at, datetime)
            assert before <= data_source.created_at <= after


class TestDataSourceServiceRead:
    """Tests for DataSourceService read methods."""
    
    def test_get_all_data_sources_empty(self, app):
        """Test getting all data sources when the database is empty."""
        with app.app_context():
            data_sources = DataSourceService.get_all()
            assert data_sources == []
    
    def test_get_all_data_sources(self, app, test_file):
        """Test getting all data sources."""
        with app.app_context():
            ds1 = DataSourceService.create(name="Source 1", file_id=test_file.id)
            ds2 = DataSourceService.create(name="Source 2", description="Second source", file_id=test_file.id)
            
            data_sources = DataSourceService.get_all()
            
            assert len(data_sources) == 2
            assert ds1 in data_sources
            assert ds2 in data_sources
    
    def test_get_all_data_sources_as_dict(self, app, test_file):
        """Test getting all data sources as dictionaries."""
        with app.app_context():
            DataSourceService.create(name="Dict Source", description="Test description", file_id=test_file.id)
            
            sources_dict = DataSourceService.get_all_dict()
            
            assert len(sources_dict) == 1
            assert sources_dict[0]["name"] == "Dict Source"
    
    def test_get_data_source_by_id(self, app, test_file):
        """Test getting a data source by its ID."""
        with app.app_context():
            data_source = DataSourceService.create(name="Get By ID Source", file_id=test_file.id)
            
            retrieved = DataSourceService.get_by_id(data_source.id)
            
            assert retrieved.id == data_source.id
            assert retrieved.name == "Get By ID Source"
    
    def test_get_data_source_by_nonexistent_id_raises_error(self, app):
        """Test that getting a nonexistent data source raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                DataSourceService.get_by_id(9999)


class TestDataSourceServiceUpdate:
    """Tests for DataSourceService.update() method."""
    
    def test_update_data_source_name(self, app, test_file):
        """Test updating a data source's name."""
        with app.app_context():
            data_source = DataSourceService.create(name="Old Name", description="Test", file_id=test_file.id)
            
            updated = DataSourceService.update(data_source.id, name="New Name")
            
            assert updated.name == "New Name"
            assert updated.description == "Test"
    
    def test_update_data_source_multiple_fields(self, app, test_file):
        """Test updating multiple fields."""
        with app.app_context():
            data_source = DataSourceService.create(name="Original", file_id=test_file.id)
            
            updated = DataSourceService.update(
                data_source.id,
                name="Updated Source",
                description="Updated description"
            )
            
            assert updated.name == "Updated Source"
            assert updated.description == "Updated description"
    
    def test_update_nonexistent_data_source_raises_error(self, app):
        """Test that updating a nonexistent data source raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                DataSourceService.update(9999, name="New")
    
    def test_update_preserves_created_at(self, app, test_file):
        """Test that updating preserves created_at timestamp."""
        with app.app_context():
            data_source = DataSourceService.create(name="Test Source", file_id=test_file.id)
            original_created_at = data_source.created_at
            
            DataSourceService.update(data_source.id, name="Updated Source")
            updated = DataSourceService.get_by_id(data_source.id)
            
            assert updated.created_at == original_created_at


class TestDataSourceServiceDelete:
    """Tests for DataSourceService.delete() method."""
    
    def test_delete_data_source(self, app, test_file):
        """Test deleting a data source."""
        with app.app_context():
            data_source = DataSourceService.create(name="Temp Source", file_id=test_file.id)
            source_id = data_source.id
            
            result = DataSourceService.delete(source_id)
            
            assert result is True
            with pytest.raises(NotFoundError):
                DataSourceService.get_by_id(source_id)
    
    def test_delete_nonexistent_data_source_raises_error(self, app):
        """Test that deleting a nonexistent data source raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                DataSourceService.delete(9999)
    
    def test_delete_removes_from_database(self, app, test_file):
        """Test that deleting removes the data source from the database."""
        with app.app_context():
            ds1 = DataSourceService.create(name="Source 1", file_id=test_file.id)
            ds2 = DataSourceService.create(name="Source 2", file_id=test_file.id)
            
            DataSourceService.delete(ds1.id)
            
            data_sources = DataSourceService.get_all()
            assert len(data_sources) == 1
            assert data_sources[0].id == ds2.id


class TestDataSourceServiceIntegration:
    """Integration tests for DataSourceService."""
    
    def test_complete_crud_cycle(self, app, test_file):
        """Test a complete CRUD cycle."""
        with app.app_context():
            # Create
            data_source = DataSourceService.create(name="CRUD Source", description="For testing", file_id=test_file.id)
            source_id = data_source.id
            
            # Read
            retrieved = DataSourceService.get_by_id(source_id)
            assert retrieved.name == "CRUD Source"
            
            # Update
            updated = DataSourceService.update(source_id, name="Updated Source")
            assert updated.name == "Updated Source"
            
            # Verify update
            verified = DataSourceService.get_by_id(source_id)
            assert verified.name == "Updated Source"
            
            # Delete
            DataSourceService.delete(source_id)
            with pytest.raises(NotFoundError):
                DataSourceService.get_by_id(source_id)
    
    def test_multiple_data_sources_lifecycle(self, app, test_file):
        """Test creating and managing multiple data sources."""
        with app.app_context():
            sources = [
                DataSourceService.create(name=f"Source {i}", description=f"Description {i}", file_id=test_file.id)
                for i in range(1, 4)
            ]
            
            assert len(DataSourceService.get_all()) == 3
            
            DataSourceService.delete(sources[0].id)
            assert len(DataSourceService.get_all()) == 2
            
            DataSourceService.create(name="New Source", file_id=test_file.id)
            assert len(DataSourceService.get_all()) == 3

