"""Unit tests for RoleSimulatorRelation."""

import pytest
from app.services.relations.role_simulator_relation import RoleSimulatorRelation
from app.services.role_service import RoleService
from app.services.simulator_service import SimulatorService
from app.domain.exceptions import NotFoundError, IllegalOperationError


class TestRoleSimulatorRelationAdd:
    """Tests for adding simulator to role."""
    
    def test_add_simulator_to_role(self, app):
        """Test adding a simulator to a role."""
        with app.app_context():
            role = RoleService.create(name="Analyst")
            simulator = SimulatorService.create(main_title="Budget Simulator")
            
            role_result, sim_result = RoleSimulatorRelation.add_simulator_to_role(role.id, simulator.id)
            
            assert role_result.id == role.id
            assert sim_result.id == simulator.id
            assert simulator in role.simulators
    
    def test_add_duplicate_simulator_raises_error(self, app):
        """Test that adding duplicate simulator raises error."""
        with app.app_context():
            role = RoleService.create(name="Manager")
            simulator = SimulatorService.create(main_title="Cost Simulator")
            
            RoleSimulatorRelation.add_simulator_to_role(role.id, simulator.id)
            
            with pytest.raises(IllegalOperationError):
                RoleSimulatorRelation.add_simulator_to_role(role.id, simulator.id)
    
    def test_add_simulator_to_nonexistent_role_raises_error(self, app):
        """Test that adding simulator to nonexistent role raises error."""
        with app.app_context():
            simulator = SimulatorService.create(main_title="Risk Simulator")
            
            with pytest.raises(NotFoundError):
                RoleSimulatorRelation.add_simulator_to_role(9999, simulator.id)
    
    def test_add_nonexistent_simulator_to_role_raises_error(self, app):
        """Test that adding nonexistent simulator raises error."""
        with app.app_context():
            role = RoleService.create(name="Admin")
            
            with pytest.raises(NotFoundError):
                RoleSimulatorRelation.add_simulator_to_role(role.id, 9999)


class TestRoleSimulatorRelationRemove:
    """Tests for removing simulator from role."""
    
    def test_remove_simulator_from_role(self, app):
        """Test removing a simulator from a role."""
        with app.app_context():
            role = RoleService.create(name="Viewer")
            simulator = SimulatorService.create(main_title="Forecast Simulator")
            RoleSimulatorRelation.add_simulator_to_role(role.id, simulator.id)
            
            role_result, sim_result = RoleSimulatorRelation.remove_simulator_from_role(role.id, simulator.id)
            
            assert simulator not in role.simulators
    
    def test_remove_nonexistent_simulator_from_role_raises_error(self, app):
        """Test that removing unassigned simulator raises error."""
        with app.app_context():
            role = RoleService.create(name="Guest")
            simulator = SimulatorService.create(main_title="Test Simulator")
            
            with pytest.raises(IllegalOperationError):
                RoleSimulatorRelation.remove_simulator_from_role(role.id, simulator.id)


class TestRoleSimulatorRelationGet:
    """Tests for getting relationships."""
    
    def test_get_all_simulators_for_role(self, app):
        """Test getting all simulators for a role."""
        with app.app_context():
            role = RoleService.create(name="Power User")
            sim1 = SimulatorService.create(main_title="Simulator 1")
            sim2 = SimulatorService.create(main_title="Simulator 2")
            
            RoleSimulatorRelation.add_simulator_to_role(role.id, sim1.id)
            RoleSimulatorRelation.add_simulator_to_role(role.id, sim2.id)
            
            simulators = RoleSimulatorRelation.get_all_b_for_a(role.id)
            
            assert len(simulators) == 2
            assert sim1 in simulators
            assert sim2 in simulators
    
    def test_get_all_roles_for_simulator(self, app):
        """Test getting all roles for a simulator."""
        with app.app_context():
            role1 = RoleService.create(name="Role 1")
            role2 = RoleService.create(name="Role 2")
            simulator = SimulatorService.create(main_title="Shared Simulator")
            
            RoleSimulatorRelation.add_simulator_to_role(role1.id, simulator.id)
            RoleSimulatorRelation.add_simulator_to_role(role2.id, simulator.id)
            
            roles = RoleSimulatorRelation.get_all_a_for_b(simulator.id)
            
            assert len(roles) == 2
            assert role1 in roles
            assert role2 in roles


class TestRoleSimulatorRelationRemoveAll:
    """Tests for removing all relationships."""
    
    def test_remove_all_simulators_for_role(self, app):
        """Test removing all simulators from a role."""
        with app.app_context():
            role = RoleService.create(name="Test Role")
            sim1 = SimulatorService.create(main_title="S1")
            sim2 = SimulatorService.create(main_title="S2")
            
            RoleSimulatorRelation.add_simulator_to_role(role.id, sim1.id)
            RoleSimulatorRelation.add_simulator_to_role(role.id, sim2.id)
            
            RoleSimulatorRelation.remove_all_b_for_a(role.id)
            
            simulators = RoleSimulatorRelation.get_all_b_for_a(role.id)
            assert len(simulators) == 0
    
    def test_remove_all_roles_for_simulator(self, app):
        """Test removing all roles from a simulator."""
        with app.app_context():
            role1 = RoleService.create(name="R1")
            role2 = RoleService.create(name="R2")
            simulator = SimulatorService.create(main_title="S")
            
            RoleSimulatorRelation.add_simulator_to_role(role1.id, simulator.id)
            RoleSimulatorRelation.add_simulator_to_role(role2.id, simulator.id)
            
            RoleSimulatorRelation.remove_all_a_for_b(simulator.id)
            
            roles = RoleSimulatorRelation.get_all_a_for_b(simulator.id)
            assert len(roles) == 0


class TestRoleSimulatorRelationIntegration:
    """Integration tests for RoleSimulatorRelation."""
    
    def test_complete_relationship_lifecycle(self, app):
        """Test complete lifecycle of role-simulator relationship."""
        with app.app_context():
            role = RoleService.create(name="SuperUser")
            sim1 = SimulatorService.create(main_title="Scenario 1")
            sim2 = SimulatorService.create(main_title="Scenario 2")
            
            # Add simulators
            RoleSimulatorRelation.add_simulator_to_role(role.id, sim1.id)
            RoleSimulatorRelation.add_simulator_to_role(role.id, sim2.id)
            
            # Verify
            simulators = RoleSimulatorRelation.get_all_b_for_a(role.id)
            assert len(simulators) == 2
            
            # Remove one
            RoleSimulatorRelation.remove_simulator_from_role(role.id, sim1.id)
            simulators = RoleSimulatorRelation.get_all_b_for_a(role.id)
            assert len(simulators) == 1
            
            # Remove all
            RoleSimulatorRelation.remove_all_b_for_a(role.id)
            simulators = RoleSimulatorRelation.get_all_b_for_a(role.id)
            assert len(simulators) == 0
