
import pytest
from datetime import datetime
from app.models.simulator import Simulator
from app.services.simulator_service import SimulatorService
from app.domain.exceptions import NotFoundError, IllegalOperationError


class TestSimulatorServiceCreate:
    """Tests for SimulatorService.create() method."""
    
    def test_create_simulator_with_all_fields(self, app):
        """Test creating a simulator with all fields provided."""
        with app.app_context():
            simulator = SimulatorService.create(
                title="Sales Simulator",
                description="Monte Carlo sales projection"
            )
            
            assert simulator.id is not None
            assert simulator.title == "Sales Simulator"
            assert simulator.description == "Monte Carlo sales projection"
            assert simulator.created_at is not None
    
    def test_create_simulator_with_minimal_fields(self, app):
        """Test creating a simulator with only required field (title)."""
        with app.app_context():
            simulator = SimulatorService.create(title="Simple Simulator")
            
            assert simulator.id is not None
            assert simulator.title == "Simple Simulator"
            assert simulator.description is None
    
    def test_create_simulator_without_name_fails(self, app):
        """Test that creating a simulator without a title raises an error."""
        with app.app_context():
            with pytest.raises(IllegalOperationError):
                SimulatorService.create(description="No name simulator")
    
    def test_create_simulator_sets_created_at_timestamp(self, app):
        """Test that created_at is automatically set."""
        with app.app_context():
            before = datetime.utcnow()
            simulator = SimulatorService.create(title="Timestamp Simulator")
            simulator = SimulatorService.get_by_id(simulator.id)
            after = datetime.utcnow()
            before = before.replace(microsecond=0)
            after = after.replace(microsecond=0)
            assert simulator.created_at is not None
            assert isinstance(simulator.created_at, datetime)
            assert before <= simulator.created_at <= after


class TestSimulatorServiceRead:
    """Tests for SimulatorService read methods."""
    
    def test_get_all_simulators_empty(self, app):
        """Test getting all simulators when the database is empty."""
        with app.app_context():
            simulators = SimulatorService.get_all()
            assert simulators == []
    
    def test_get_all_simulators(self, app):
        """Test getting all simulators."""
        with app.app_context():
            sim1 = SimulatorService.create(title="Simulator 1")
            sim2 = SimulatorService.create(title="Simulator 2", description="Second simulator")
            
            simulators = SimulatorService.get_all()
            
            assert len(simulators) == 2
            assert sim1 in simulators
            assert sim2 in simulators
    
    def test_get_all_simulators_as_dict(self, app):
        """Test getting all simulators as dictionaries."""
        with app.app_context():
            SimulatorService.create(title="Dict Simulator", description="Test description")
            
            simulators_dict = SimulatorService.get_all_dict()
            
            assert len(simulators_dict) == 1
            assert simulators_dict[0]["title"] == "Dict Simulator"
    
    def test_get_simulator_by_id(self, app):
        """Test getting a simulator by its ID."""
        with app.app_context():
            simulator = SimulatorService.create(title="Get By ID Simulator")
            
            retrieved = SimulatorService.get_by_id(simulator.id)
            
            assert retrieved.id == simulator.id
            assert retrieved.title == "Get By ID Simulator"
    
    def test_get_simulator_by_nonexistent_id_raises_error(self, app):
        """Test that getting a nonexistent simulator raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                SimulatorService.get_by_id(9999)


class TestSimulatorServiceUpdate:
    """Tests for SimulatorService.update() method."""
    
    def test_update_simulator_name(self, app):
        """Test updating a simulator's name."""
        with app.app_context():
            simulator = SimulatorService.create(title="Old Name", description="Test")
            
            updated = SimulatorService.update(simulator.id, title="New Name")
            
            assert updated.title == "New Name"
            assert updated.description == "Test"
    
    def test_update_simulator_multiple_fields(self, app):
        """Test updating multiple fields."""
        with app.app_context():
            simulator = SimulatorService.create(title="Original")
            
            updated = SimulatorService.update(
                simulator.id,
                title="Updated Simulator",
                description="Updated description"
            )
            
            assert updated.title == "Updated Simulator"
            assert updated.description == "Updated description"
    
    def test_update_nonexistent_simulator_raises_error(self, app):
        """Test that updating a nonexistent simulator raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                SimulatorService.update(9999, title="New")
    
    def test_update_preserves_created_at(self, app):
        """Test that updating preserves created_at timestamp."""
        with app.app_context():
            simulator = SimulatorService.create(title="Test Simulator")
            original_created_at = simulator.created_at
            
            SimulatorService.update(simulator.id, title="Updated Simulator")
            updated = SimulatorService.get_by_id(simulator.id)
            
            assert updated.created_at == original_created_at


class TestSimulatorServiceDelete:
    """Tests for SimulatorService.delete() method."""
    
    def test_delete_simulator(self, app):
        """Test deleting a simulator."""
        with app.app_context():
            simulator = SimulatorService.create(title="Temp Simulator")
            simulator_id = simulator.id
            
            result = SimulatorService.delete(simulator_id)
            
            assert result is True
            with pytest.raises(NotFoundError):
                SimulatorService.get_by_id(simulator_id)
    
    def test_delete_nonexistent_simulator_raises_error(self, app):
        """Test that deleting a nonexistent simulator raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                SimulatorService.delete(9999)
    
    def test_delete_removes_from_database(self, app):
        """Test that deleting removes the simulator from the database."""
        with app.app_context():
            sim1 = SimulatorService.create(title="Simulator 1")
            sim2 = SimulatorService.create(title="Simulator 2")
            
            SimulatorService.delete(sim1.id)
            
            simulators = SimulatorService.get_all()
            assert len(simulators) == 1
            assert simulators[0].id == sim2.id


class TestSimulatorServiceIntegration:
    """Integration tests for SimulatorService."""
    
    def test_complete_crud_cycle(self, app):
        """Test a complete CRUD cycle."""
        with app.app_context():
            # Create
            simulator = SimulatorService.create(title="CRUD Simulator", description="For testing")
            simulator_id = simulator.id
            
            # Read
            retrieved = SimulatorService.get_by_id(simulator_id)
            assert retrieved.title == "CRUD Simulator"
            
            # Update
            updated = SimulatorService.update(simulator_id, title="Updated Simulator")
            assert updated.title == "Updated Simulator"
            
            # Verify update
            verified = SimulatorService.get_by_id(simulator_id)
            assert verified.title == "Updated Simulator"
            
            # Delete
            SimulatorService.delete(simulator_id)
            with pytest.raises(NotFoundError):
                SimulatorService.get_by_id(simulator_id)
    
    def test_multiple_simulators_lifecycle(self, app):
        """Test creating and managing multiple simulators."""
        with app.app_context():
            simulators = [
                SimulatorService.create(title=f"Simulator {i}", description=f"Description {i}")
                for i in range(1, 4)
            ]
            
            assert len(SimulatorService.get_all()) == 3
            
            SimulatorService.delete(simulators[0].id)
            assert len(SimulatorService.get_all()) == 2
            
            SimulatorService.create(title="New Simulator")
            assert len(SimulatorService.get_all()) == 3
