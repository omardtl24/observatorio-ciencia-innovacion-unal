"""Unit tests for RoleReportRelation."""

import pytest
from app.services.relations.role_report_relation import RoleReportRelation
from app.services.role_service import RoleService
from app.services.report_service import ReportService
from app.domain.exceptions import NotFoundError, IllegalOperationError


class TestRoleReportRelationAdd:
    """Tests for adding report to role."""
    
    def test_add_report_to_role(self, app):
        """Test adding a report to a role."""
        with app.app_context():
            role = RoleService.create(name="Admin")
            report = ReportService.create(name="Sales Report")
            
            role_result, report_result = RoleReportRelation.add_report_to_role(role.id, report.id)
            
            assert role_result.id == role.id
            assert report_result.id == report.id
            assert report in role.reports
    
    def test_add_duplicate_report_raises_error(self, app):
        """Test that adding duplicate report raises error."""
        with app.app_context():
            role = RoleService.create(name="Editor")
            report = ReportService.create(name="Monthly Report")
            
            RoleReportRelation.add_report_to_role(role.id, report.id)
            
            with pytest.raises(IllegalOperationError):
                RoleReportRelation.add_report_to_role(role.id, report.id)
    
    def test_add_report_to_nonexistent_role_raises_error(self, app):
        """Test that adding report to nonexistent role raises error."""
        with app.app_context():
            report = ReportService.create(name="Test Report")
            
            with pytest.raises(NotFoundError):
                RoleReportRelation.add_report_to_role(9999, report.id)
    
    def test_add_nonexistent_report_to_role_raises_error(self, app):
        """Test that adding nonexistent report raises error."""
        with app.app_context():
            role = RoleService.create(name="Viewer")
            
            with pytest.raises(NotFoundError):
                RoleReportRelation.add_report_to_role(role.id, 9999)


class TestRoleReportRelationRemove:
    """Tests for removing report from role."""
    
    def test_remove_report_from_role(self, app):
        """Test removing a report from a role."""
        with app.app_context():
            role = RoleService.create(name="Manager")
            report = ReportService.create(name="Annual Report")
            RoleReportRelation.add_report_to_role(role.id, report.id)
            
            role_result, report_result = RoleReportRelation.remove_report_from_role(role.id, report.id)
            
            assert report not in role.reports
    
    def test_remove_nonexistent_report_from_role_raises_error(self, app):
        """Test that removing unassigned report raises error."""
        with app.app_context():
            role = RoleService.create(name="Support")
            report = ReportService.create(name="Support Report")
            
            with pytest.raises(IllegalOperationError):
                RoleReportRelation.remove_report_from_role(role.id, report.id)


class TestRoleReportRelationGet:
    """Tests for getting relationships."""
    
    def test_get_all_reports_for_role(self, app):
        """Test getting all reports for a role."""
        with app.app_context():
            role = RoleService.create(name="Analyst")
            report1 = ReportService.create(name="Report 1")
            report2 = ReportService.create(name="Report 2")
            
            RoleReportRelation.add_report_to_role(role.id, report1.id)
            RoleReportRelation.add_report_to_role(role.id, report2.id)
            
            reports = RoleReportRelation.get_all_b_for_a(role.id)
            
            assert len(reports) == 2
            assert report1 in reports
            assert report2 in reports
    
    def test_get_all_roles_for_report(self, app):
        """Test getting all roles for a report."""
        with app.app_context():
            role1 = RoleService.create(name="Role1")
            role2 = RoleService.create(name="Role2")
            report = ReportService.create(name="Shared Report")
            
            RoleReportRelation.add_report_to_role(role1.id, report.id)
            RoleReportRelation.add_report_to_role(role2.id, report.id)
            
            roles = RoleReportRelation.get_all_a_for_b(report.id)
            
            assert len(roles) == 2
            assert role1 in roles
            assert role2 in roles


class TestRoleReportRelationRemoveAll:
    """Tests for removing all relationships."""
    
    def test_remove_all_reports_for_role(self, app):
        """Test removing all reports from a role."""
        with app.app_context():
            role = RoleService.create(name="Admin")
            report1 = ReportService.create(name="R1")
            report2 = ReportService.create(name="R2")
            
            RoleReportRelation.add_report_to_role(role.id, report1.id)
            RoleReportRelation.add_report_to_role(role.id, report2.id)
            
            RoleReportRelation.remove_all_b_for_a(role.id)
            
            reports = RoleReportRelation.get_all_b_for_a(role.id)
            assert len(reports) == 0
    
    def test_remove_all_roles_for_report(self, app):
        """Test removing all roles from a report."""
        with app.app_context():
            role1 = RoleService.create(name="R1")
            role2 = RoleService.create(name="R2")
            report = ReportService.create(name="Team Report")
            
            RoleReportRelation.add_report_to_role(role1.id, report.id)
            RoleReportRelation.add_report_to_role(role2.id, report.id)
            
            RoleReportRelation.remove_all_a_for_b(report.id)
            
            roles = RoleReportRelation.get_all_a_for_b(report.id)
            assert len(roles) == 0


class TestRoleReportRelationIntegration:
    """Integration tests for RoleReportRelation."""
    
    def test_complete_relationship_lifecycle(self, app):
        """Test complete lifecycle of role-report relationship."""
        with app.app_context():
            role = RoleService.create(name="Data Analyst")
            report1 = ReportService.create(name="Q1 Report")
            report2 = ReportService.create(name="Q2 Report")
            
            # Add reports
            RoleReportRelation.add_report_to_role(role.id, report1.id)
            RoleReportRelation.add_report_to_role(role.id, report2.id)
            
            # Verify
            reports = RoleReportRelation.get_all_b_for_a(role.id)
            assert len(reports) == 2
            
            # Remove one
            RoleReportRelation.remove_report_from_role(role.id, report1.id)
            reports = RoleReportRelation.get_all_b_for_a(role.id)
            assert len(reports) == 1
            
            # Remove all
            RoleReportRelation.remove_all_b_for_a(role.id)
            reports = RoleReportRelation.get_all_b_for_a(role.id)
            assert len(reports) == 0
