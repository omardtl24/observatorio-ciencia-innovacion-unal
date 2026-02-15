"""Unit tests for SimulatorDataSourceRelation."""

import pytest
from app.services.relations.simulator_data_source_relation import SimulatorDataSourceRelation
from app.services.simulator_service import SimulatorService
from app.services.data_source_service import DataSourceService
from app.domain.exceptions import NotFoundError, IllegalOperationError


class TestSimulatorDataSourceRelationAdd:
    """Tests for adding data source to simulator."""
    
    def test_add_data_source_to_simulator(self, app, test_file):
        """Test adding a data source to a simulator."""
        with app.app_context():
            simulator = SimulatorService.create(main_title="Budget Simulator")
            data_source = DataSourceService.create(name="API Source", file_id=test_file.id)
            
            sim_result, ds_result = SimulatorDataSourceRelation.add_data_source_to_simulator(simulator.id, data_source.id)
            
            assert sim_result.id == simulator.id
            assert ds_result.id == data_source.id
            assert data_source in simulator.data_sources
    
    def test_add_duplicate_data_source_raises_error(self, app, test_file):
        """Test that adding duplicate data source raises error."""
        with app.app_context():
            simulator = SimulatorService.create(main_title="Test Simulator")
            data_source = DataSourceService.create(name="DB Source", file_id=test_file.id)
            
            SimulatorDataSourceRelation.add_data_source_to_simulator(simulator.id, data_source.id)
            
            with pytest.raises(IllegalOperationError):
                SimulatorDataSourceRelation.add_data_source_to_simulator(simulator.id, data_source.id)
    
    def test_add_data_source_to_nonexistent_simulator_raises_error(self, app, test_file):
        """Test that adding data source to nonexistent simulator raises error."""
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=test_file.id)
            
            with pytest.raises(NotFoundError):
                SimulatorDataSourceRelation.add_data_source_to_simulator(9999, data_source.id)
    
    def test_add_nonexistent_data_source_to_simulator_raises_error(self, app):
        """Test that adding nonexistent data source raises error."""
        with app.app_context():
            simulator = SimulatorService.create(main_title="Simulator")
            
            with pytest.raises(NotFoundError):
                SimulatorDataSourceRelation.add_data_source_to_simulator(simulator.id, 9999)


class TestSimulatorDataSourceRelationRemove:
    """Tests for removing data source from simulator."""
    
    def test_remove_data_source_from_simulator(self, app, test_file):
        """Test removing a data source from a simulator."""
        with app.app_context():
            simulator = SimulatorService.create(main_title="Simulator")
            data_source = DataSourceService.create(name="Source", file_id=test_file.id)
            SimulatorDataSourceRelation.add_data_source_to_simulator(simulator.id, data_source.id)
            
            sim_result, ds_result = SimulatorDataSourceRelation.remove_data_source_from_simulator(simulator.id, data_source.id)
            
            assert data_source not in simulator.data_sources
    
    def test_remove_nonexistent_data_source_from_simulator_raises_error(self, app, test_file):
        """Test that removing unassigned data source raises error."""
        with app.app_context():
            simulator = SimulatorService.create(main_title="Simulator")
            data_source = DataSourceService.create(name="Source", file_id=test_file.id)
            
            with pytest.raises(IllegalOperationError):
                SimulatorDataSourceRelation.remove_data_source_from_simulator(simulator.id, data_source.id)


class TestSimulatorDataSourceRelationGet:
    """Tests for getting relationships."""
    
    def test_get_all_data_sources_for_simulator(self, app, test_file):
        """Test getting all data sources for a simulator."""
        with app.app_context():
            simulator = SimulatorService.create(main_title="Multi-source Simulator")
            ds1 = DataSourceService.create(name="Source 1", file_id=test_file.id)
            ds2 = DataSourceService.create(name="Source 2", file_id=test_file.id)
            
            SimulatorDataSourceRelation.add_data_source_to_simulator(simulator.id, ds1.id)
            SimulatorDataSourceRelation.add_data_source_to_simulator(simulator.id, ds2.id)
            
            data_sources = SimulatorDataSourceRelation.get_all_b_for_a(simulator.id)
            
            assert len(data_sources) == 2
            assert ds1 in data_sources
            assert ds2 in data_sources
    
    def test_get_all_simulators_for_data_source(self, app, test_file):
        """Test getting all simulators for a data source."""
        with app.app_context():
            sim1 = SimulatorService.create(main_title="Simulator 1")
            sim2 = SimulatorService.create(main_title="Simulator 2")
            data_source = DataSourceService.create(name="Shared Source", file_id=test_file.id)
            
            SimulatorDataSourceRelation.add_data_source_to_simulator(sim1.id, data_source.id)
            SimulatorDataSourceRelation.add_data_source_to_simulator(sim2.id, data_source.id)
            
            simulators = SimulatorDataSourceRelation.get_all_a_for_b(data_source.id)
            
            assert len(simulators) == 2
            assert sim1 in simulators
            assert sim2 in simulators


class TestSimulatorDataSourceRelationRemoveAll:
    """Tests for removing all relationships."""
    
    def test_remove_all_data_sources_for_simulator(self, app, test_file):
        """Test removing all data sources from a simulator."""
        with app.app_context():
            simulator = SimulatorService.create(main_title="Simulator")
            ds1 = DataSourceService.create(name="DS1", file_id=test_file.id)
            ds2 = DataSourceService.create(name="DS2", file_id=test_file.id)
            
            SimulatorDataSourceRelation.add_data_source_to_simulator(simulator.id, ds1.id)
            SimulatorDataSourceRelation.add_data_source_to_simulator(simulator.id, ds2.id)
            
            SimulatorDataSourceRelation.remove_all_b_for_a(simulator.id)
            
            data_sources = SimulatorDataSourceRelation.get_all_b_for_a(simulator.id)
            assert len(data_sources) == 0
    
    def test_remove_all_simulators_for_data_source(self, app, test_file):
        """Test removing all simulators from a data source."""
        with app.app_context():
            sim1 = SimulatorService.create(main_title="S1")
            sim2 = SimulatorService.create(main_title="S2")
            data_source = DataSourceService.create(name="DS", file_id=test_file.id)
            
            SimulatorDataSourceRelation.add_data_source_to_simulator(sim1.id, data_source.id)
            SimulatorDataSourceRelation.add_data_source_to_simulator(sim2.id, data_source.id)
            
            SimulatorDataSourceRelation.remove_all_a_for_b(data_source.id)
            
            simulators = SimulatorDataSourceRelation.get_all_a_for_b(data_source.id)
            assert len(simulators) == 0


class TestSimulatorDataSourceRelationIntegration:
    """Integration tests for SimulatorDataSourceRelation."""
    
    def test_complete_relationship_lifecycle(self, app, test_file):
        """Test complete lifecycle of simulator-datasource relationship."""
        with app.app_context():
            simulator = SimulatorService.create(main_title="Forecast Model")
            ds1 = DataSourceService.create(name="API", file_id=test_file.id)
            ds2 = DataSourceService.create(name="DB", file_id=test_file.id)
            
            # Add data sources
            SimulatorDataSourceRelation.add_data_source_to_simulator(simulator.id, ds1.id)
            SimulatorDataSourceRelation.add_data_source_to_simulator(simulator.id, ds2.id)
            
            # Verify
            sources = SimulatorDataSourceRelation.get_all_b_for_a(simulator.id)
            assert len(sources) == 2
            
            # Remove one
            SimulatorDataSourceRelation.remove_data_source_from_simulator(simulator.id, ds1.id)
            sources = SimulatorDataSourceRelation.get_all_b_for_a(simulator.id)
            assert len(sources) == 1
            
            # Remove all
            SimulatorDataSourceRelation.remove_all_b_for_a(simulator.id)
            sources = SimulatorDataSourceRelation.get_all_b_for_a(simulator.id)
            assert len(sources) == 0
