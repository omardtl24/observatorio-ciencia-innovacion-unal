"""Unit tests for RoleDataSourceRelation."""

import pytest # type: ignore
from app.services.relations.role_data_source_relation import RoleDataSourceRelation
from app.services.role_service import RoleService
from app.services.data_source_service import DataSourceService
from app.domain.exceptions import NotFoundError, IllegalOperationError


class TestRoleDataSourceRelationAdd:
    """Tests for adding data source to role."""

    def test_add_data_source_to_role(self, app, test_file):
        """Test adding a data source to a role."""
        with app.app_context():
            role = RoleService.create(name="Analyst")
            data_source = DataSourceService.create(name="API Source", file_id=test_file.id)

            role_result, data_source_result = RoleDataSourceRelation.add_data_source_to_role(role.id, data_source.id)

            assert role_result.id == role.id
            assert data_source_result.id == data_source.id
            assert data_source in role.data_sources

    def test_add_duplicate_data_source_raises_error(self, app, test_file):
        """Test that adding duplicate data source raises error."""
        with app.app_context():
            role = RoleService.create(name="Manager")
            data_source = DataSourceService.create(name="DB Source", file_id=test_file.id)

            RoleDataSourceRelation.add_data_source_to_role(role.id, data_source.id)

            with pytest.raises(IllegalOperationError):
                RoleDataSourceRelation.add_data_source_to_role(role.id, data_source.id)

    def test_add_data_source_to_nonexistent_role_raises_error(self, app, test_file):
        """Test that adding data source to nonexistent role raises error."""
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=test_file.id)

            with pytest.raises(NotFoundError):
                RoleDataSourceRelation.add_data_source_to_role(9999, data_source.id)

    def test_add_nonexistent_data_source_to_role_raises_error(self, app):
        """Test that adding nonexistent data source raises error."""
        with app.app_context():
            role = RoleService.create(name="Viewer")

            with pytest.raises(NotFoundError):
                RoleDataSourceRelation.add_data_source_to_role(role.id, 9999)


class TestRoleDataSourceRelationRemove:
    """Tests for removing data source from role."""

    def test_remove_data_source_from_role(self, app, test_file):
        """Test removing a data source from a role."""
        with app.app_context():
            role = RoleService.create(name="Reviewer")
            data_source = DataSourceService.create(name="Warehouse", file_id=test_file.id)
            RoleDataSourceRelation.add_data_source_to_role(role.id, data_source.id)

            RoleDataSourceRelation.remove_data_source_from_role(role.id, data_source.id)

            assert data_source not in role.data_sources

    def test_remove_nonexistent_data_source_from_role_raises_error(self, app, test_file):
        """Test that removing unassigned data source raises error."""
        with app.app_context():
            role = RoleService.create(name="Guest")
            data_source = DataSourceService.create(name="Public DS", file_id=test_file.id)

            with pytest.raises(IllegalOperationError):
                RoleDataSourceRelation.remove_data_source_from_role(role.id, data_source.id)


class TestRoleDataSourceRelationGet:
    """Tests for getting relationships."""

    def test_get_all_data_sources_for_role(self, app, test_file):
        """Test getting all data sources for a role."""
        with app.app_context():
            role = RoleService.create(name="Power User")
            ds1 = DataSourceService.create(name="Source 1", file_id=test_file.id)
            ds2 = DataSourceService.create(name="Source 2", file_id=test_file.id)

            RoleDataSourceRelation.add_data_source_to_role(role.id, ds1.id)
            RoleDataSourceRelation.add_data_source_to_role(role.id, ds2.id)

            data_sources = RoleDataSourceRelation.get_all_b_for_a(role.id)

            assert len(data_sources) == 2
            assert ds1 in data_sources
            assert ds2 in data_sources

    def test_get_all_roles_for_data_source(self, app, test_file):
        """Test getting all roles for a data source."""
        with app.app_context():
            role1 = RoleService.create(name="Role 1")
            role2 = RoleService.create(name="Role 2")
            data_source = DataSourceService.create(name="Shared Source", file_id=test_file.id)

            RoleDataSourceRelation.add_data_source_to_role(role1.id, data_source.id)
            RoleDataSourceRelation.add_data_source_to_role(role2.id, data_source.id)

            roles = RoleDataSourceRelation.get_all_a_for_b(data_source.id)

            assert len(roles) == 2
            assert role1 in roles
            assert role2 in roles


class TestRoleDataSourceRelationRemoveAll:
    """Tests for removing all relationships."""

    def test_remove_all_data_sources_for_role(self, app, test_file):
        """Test removing all data sources from a role."""
        with app.app_context():
            role = RoleService.create(name="Coordinator")
            ds1 = DataSourceService.create(name="DS1", file_id=test_file.id)
            ds2 = DataSourceService.create(name="DS2", file_id=test_file.id)

            RoleDataSourceRelation.add_data_source_to_role(role.id, ds1.id)
            RoleDataSourceRelation.add_data_source_to_role(role.id, ds2.id)

            RoleDataSourceRelation.remove_all_b_for_a(role.id)

            data_sources = RoleDataSourceRelation.get_all_b_for_a(role.id)
            assert len(data_sources) == 0

    def test_remove_all_roles_for_data_source(self, app, test_file):
        """Test removing all roles from a data source."""
        with app.app_context():
            role1 = RoleService.create(name="R1")
            role2 = RoleService.create(name="R2")
            data_source = DataSourceService.create(name="DS", file_id=test_file.id)

            RoleDataSourceRelation.add_data_source_to_role(role1.id, data_source.id)
            RoleDataSourceRelation.add_data_source_to_role(role2.id, data_source.id)

            RoleDataSourceRelation.remove_all_a_for_b(data_source.id)

            roles = RoleDataSourceRelation.get_all_a_for_b(data_source.id)
            assert len(roles) == 0


class TestRoleDataSourceRelationIntegration:
    """Integration tests for RoleDataSourceRelation."""

    def test_complete_relationship_lifecycle(self, app, test_file):
        """Test complete lifecycle of role-data_source relationship."""
        with app.app_context():
            role = RoleService.create(name="Data Analyst")
            ds1 = DataSourceService.create(name="API", file_id=test_file.id)
            ds2 = DataSourceService.create(name="DB", file_id=test_file.id)

            RoleDataSourceRelation.add_data_source_to_role(role.id, ds1.id)
            RoleDataSourceRelation.add_data_source_to_role(role.id, ds2.id)

            data_sources = RoleDataSourceRelation.get_all_b_for_a(role.id)
            assert len(data_sources) == 2

            RoleDataSourceRelation.remove_data_source_from_role(role.id, ds1.id)
            data_sources = RoleDataSourceRelation.get_all_b_for_a(role.id)
            assert len(data_sources) == 1

            RoleDataSourceRelation.remove_all_b_for_a(role.id)
            data_sources = RoleDataSourceRelation.get_all_b_for_a(role.id)
            assert len(data_sources) == 0
