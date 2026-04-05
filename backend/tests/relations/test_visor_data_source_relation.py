"""Unit tests for VisorDataSourceRelation."""

import pytest
from app.services.relations.visor_data_source_relation import VisorDataSourceRelation
from app.services.visor_service import VisorService
from app.services.data_source_service import DataSourceService
from app.domain.exceptions import NotFoundError, IllegalOperationError


class TestVisorDataSourceRelationAdd:
    """Tests for adding data source to visor."""
    
    def test_add_data_source_to_visor(self, app, test_file):
        """Test adding a data source to a visor."""
        with app.app_context():
            visor = VisorService.create(title="Dashboard")
            data_source = DataSourceService.create(name="API Source", file_id=test_file.id)
            
            visor_result, ds_result = VisorDataSourceRelation.add_data_source_to_visor(visor.id, data_source.id)
            
            assert visor_result.id == visor.id
            assert ds_result.id == data_source.id
            assert data_source in visor.data_sources
    
    def test_add_duplicate_data_source_raises_error(self, app, test_file):
        """Test that adding duplicate data source raises error."""
        with app.app_context():
            visor = VisorService.create(title="Test Visor")
            data_source = DataSourceService.create(name="DB Source", file_id=test_file.id)
            
            VisorDataSourceRelation.add_data_source_to_visor(visor.id, data_source.id)
            
            with pytest.raises(IllegalOperationError):
                VisorDataSourceRelation.add_data_source_to_visor(visor.id, data_source.id)
    
    def test_add_data_source_to_nonexistent_visor_raises_error(self, app, test_file):
        """Test that adding data source to nonexistent visor raises error."""
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=test_file.id)
            
            with pytest.raises(NotFoundError):
                VisorDataSourceRelation.add_data_source_to_visor(9999, data_source.id)
    
    def test_add_nonexistent_data_source_to_visor_raises_error(self, app):
        """Test that adding nonexistent data source raises error."""
        with app.app_context():
            visor = VisorService.create(title="Visor")
            
            with pytest.raises(NotFoundError):
                VisorDataSourceRelation.add_data_source_to_visor(visor.id, 9999)


class TestVisorDataSourceRelationRemove:
    """Tests for removing data source from visor."""
    
    def test_remove_data_source_from_visor(self, app, test_file):
        """Test removing a data source from a visor."""
        with app.app_context():
            visor = VisorService.create(title="Visor")
            data_source = DataSourceService.create(name="Source", file_id=test_file.id)
            VisorDataSourceRelation.add_data_source_to_visor(visor.id, data_source.id)
            
            visor_result, ds_result = VisorDataSourceRelation.remove_data_source_from_visor(visor.id, data_source.id)
            
            assert data_source not in visor.data_sources
    
    def test_remove_nonexistent_data_source_from_visor_raises_error(self, app, test_file):
        """Test that removing unassigned data source raises error."""
        with app.app_context():
            visor = VisorService.create(title="Visor")
            data_source = DataSourceService.create(name="Source", file_id=test_file.id)
            
            with pytest.raises(IllegalOperationError):
                VisorDataSourceRelation.remove_data_source_from_visor(visor.id, data_source.id)


class TestVisorDataSourceRelationGet:
    """Tests for getting relationships."""
    
    def test_get_all_data_sources_for_visor(self, app, test_file):
        """Test getting all data sources for a visor."""
        with app.app_context():
            visor = VisorService.create(title="Multi-source Visor")
            ds1 = DataSourceService.create(name="Source 1", file_id=test_file.id)
            ds2 = DataSourceService.create(name="Source 2", file_id=test_file.id)
            
            VisorDataSourceRelation.add_data_source_to_visor(visor.id, ds1.id)
            VisorDataSourceRelation.add_data_source_to_visor(visor.id, ds2.id)
            
            data_sources = VisorDataSourceRelation.get_all_b_for_a(visor.id)
            
            assert len(data_sources) == 2
            assert ds1 in data_sources
            assert ds2 in data_sources
    
    def test_get_all_visors_for_data_source(self, app, test_file):
        """Test getting all visors for a data source."""
        with app.app_context():
            visor1 = VisorService.create(title="Visor 1")
            visor2 = VisorService.create(title="Visor 2")
            data_source = DataSourceService.create(name="Shared Source", file_id=test_file.id)
            
            VisorDataSourceRelation.add_data_source_to_visor(visor1.id, data_source.id)
            VisorDataSourceRelation.add_data_source_to_visor(visor2.id, data_source.id)
            
            visors = VisorDataSourceRelation.get_all_a_for_b(data_source.id)
            
            assert len(visors) == 2
            assert visor1 in visors
            assert visor2 in visors


class TestVisorDataSourceRelationRemoveAll:
    """Tests for removing all relationships."""
    
    def test_remove_all_data_sources_for_visor(self, app, test_file):
        """Test removing all data sources from a visor."""
        with app.app_context():
            visor = VisorService.create(title="Visor")
            ds1 = DataSourceService.create(name="DS1", file_id=test_file.id)
            ds2 = DataSourceService.create(name="DS2", file_id=test_file.id)
            
            VisorDataSourceRelation.add_data_source_to_visor(visor.id, ds1.id)
            VisorDataSourceRelation.add_data_source_to_visor(visor.id, ds2.id)
            
            VisorDataSourceRelation.remove_all_b_for_a(visor.id)
            
            data_sources = VisorDataSourceRelation.get_all_b_for_a(visor.id)
            assert len(data_sources) == 0
    
    def test_remove_all_visors_for_data_source(self, app, test_file):
        """Test removing all visors from a data source."""
        with app.app_context():
            visor1 = VisorService.create(title="V1")
            visor2 = VisorService.create(title="V2")
            data_source = DataSourceService.create(name="DS", file_id=test_file.id)
            
            VisorDataSourceRelation.add_data_source_to_visor(visor1.id, data_source.id)
            VisorDataSourceRelation.add_data_source_to_visor(visor2.id, data_source.id)
            
            VisorDataSourceRelation.remove_all_a_for_b(data_source.id)
            
            visors = VisorDataSourceRelation.get_all_a_for_b(data_source.id)
            assert len(visors) == 0


class TestVisorDataSourceRelationIntegration:
    """Integration tests for VisorDataSourceRelation."""
    
    def test_complete_relationship_lifecycle(self, app, test_file):
        """Test complete lifecycle of visor-datasource relationship."""
        with app.app_context():
            visor = VisorService.create(title="Analytics Dashboard")
            ds1 = DataSourceService.create(name="API", file_id=test_file.id)
            ds2 = DataSourceService.create(name="DB", file_id=test_file.id)
            
            # Add data sources
            VisorDataSourceRelation.add_data_source_to_visor(visor.id, ds1.id)
            VisorDataSourceRelation.add_data_source_to_visor(visor.id, ds2.id)
            
            # Verify
            sources = VisorDataSourceRelation.get_all_b_for_a(visor.id)
            assert len(sources) == 2
            
            # Remove one
            VisorDataSourceRelation.remove_data_source_from_visor(visor.id, ds1.id)
            sources = VisorDataSourceRelation.get_all_b_for_a(visor.id)
            assert len(sources) == 1
            
            # Remove all
            VisorDataSourceRelation.remove_all_b_for_a(visor.id)
            sources = VisorDataSourceRelation.get_all_b_for_a(visor.id)
            assert len(sources) == 0
