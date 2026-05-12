
import pytest # type: ignore
from datetime import datetime
from app.models.report import Report
from app.services.report_service import ReportService
from app.domain.exceptions import NotFoundError, IllegalOperationError


class TestReportServiceCreate:
    """Tests for ReportService.create() method."""
    
    def test_create_report_with_all_fields(self, app):
        """Test creating a report with all fields provided."""
        with app.app_context():
            report = ReportService.create(
                title="Sales Report",
                description="Monthly sales metrics"
            )
            
            assert report.id is not None
            assert report.title == "Sales Report"
            assert report.description == "Monthly sales metrics"
            assert report.created_at is not None
    
    def test_create_report_with_minimal_fields(self, app):
        """Test creating a report with only required field (title)."""
        with app.app_context():
            report = ReportService.create(title="Quick Report")
            
            assert report.id is not None
            assert report.title == "Quick Report"
            assert report.description is None
    
    def test_create_report_without_name_fails(self, app):
        """Test that creating a report without a title raises an error."""
        with app.app_context():
            with pytest.raises(IllegalOperationError):
                ReportService.create(description="No name report")
    
    def test_create_report_sets_created_at_timestamp(self, app):
        """Test that created_at is automatically set."""
        with app.app_context():
            before = datetime.utcnow()
            report = ReportService.create(title="Timestamp Report")
            report = ReportService.get_by_id(report.id)
            after = datetime.utcnow()
            before = before.replace(microsecond=0)
            after = after.replace(microsecond=0)
            assert report.created_at is not None
            assert isinstance(report.created_at, datetime)
            assert before <= report.created_at <= after


class TestReportServiceRead:
    """Tests for ReportService read methods."""
    
    def test_get_all_reports_empty(self, app):
        """Test getting all reports when the database is empty."""
        with app.app_context():
            reports = ReportService.get_all()
            assert reports == []
    
    def test_get_all_reports(self, app):
        """Test getting all reports."""
        with app.app_context():
            report1 = ReportService.create(title="Report 1")
            report2 = ReportService.create(title="Report 2", description="Second report")
            
            reports = ReportService.get_all()
            
            assert len(reports) == 2
            assert report1 in reports
            assert report2 in reports
    
    def test_get_all_reports_as_dict(self, app):
        """Test getting all reports as dictionaries."""
        with app.app_context():
            ReportService.create(title="Dict Report", description="Test description")
            
            reports_dict = ReportService.get_all_dict()
            
            assert len(reports_dict) == 1
            assert reports_dict[0]["title"] == "Dict Report"
    
    def test_get_report_by_id(self, app):
        """Test getting a report by its ID."""
        with app.app_context():
            report = ReportService.create(title="Get By ID Report")
            
            retrieved = ReportService.get_by_id(report.id)
            
            assert retrieved.id == report.id
            assert retrieved.title == "Get By ID Report"
    
    def test_get_report_by_nonexistent_id_raises_error(self, app):
        """Test that getting a nonexistent report raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                ReportService.get_by_id(9999)


class TestReportServiceUpdate:
    """Tests for ReportService.update() method."""
    
    def test_update_report_name(self, app):
        """Test updating a report's name."""
        with app.app_context():
            report = ReportService.create(title="Old Name", description="Test")
            
            updated = ReportService.update(report.id, title="New Name")
            
            assert updated.title == "New Name"
            assert updated.description == "Test"
    
    def test_update_report_multiple_fields(self, app):
        """Test updating multiple fields."""
        with app.app_context():
            report = ReportService.create(title="Original")
            
            updated = ReportService.update(
                report.id,
                title="Updated Report",
                description="Updated description"
            )
            
            assert updated.title == "Updated Report"
            assert updated.description == "Updated description"
    
    def test_update_nonexistent_report_raises_error(self, app):
        """Test that updating a nonexistent report raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                ReportService.update(9999, title="New")
    
    def test_update_preserves_created_at(self, app):
        """Test that updating preserves created_at timestamp."""
        with app.app_context():
            report = ReportService.create(title="Test Report")
            original_created_at = report.created_at
            
            ReportService.update(report.id, title="Updated Report")
            updated = ReportService.get_by_id(report.id)
            
            assert updated.created_at == original_created_at


class TestReportServiceDelete:
    """Tests for ReportService.delete() method."""
    
    def test_delete_report(self, app):
        """Test deleting a report."""
        with app.app_context():
            report = ReportService.create(title="Temp Report")
            report_id = report.id
            
            result = ReportService.delete(report_id)
            
            assert result is True
            with pytest.raises(NotFoundError):
                ReportService.get_by_id(report_id)
    
    def test_delete_nonexistent_report_raises_error(self, app):
        """Test that deleting a nonexistent report raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                ReportService.delete(9999)
    
    def test_delete_removes_from_database(self, app):
        """Test that deleting removes the report from the database."""
        with app.app_context():
            report1 = ReportService.create(title="Report 1")
            report2 = ReportService.create(title="Report 2")
            
            ReportService.delete(report1.id)
            
            reports = ReportService.get_all()
            assert len(reports) == 1
            assert reports[0].id == report2.id


class TestReportServiceIntegration:
    """Integration tests for ReportService."""
    
    def test_complete_crud_cycle(self, app):
        """Test a complete CRUD cycle."""
        with app.app_context():
            # Create
            report = ReportService.create(title="CRUD Report", description="For testing")
            report_id = report.id
            
            # Read
            retrieved = ReportService.get_by_id(report_id)
            assert retrieved.title == "CRUD Report"
            
            # Update
            updated = ReportService.update(report_id, title="Updated Report")
            assert updated.title == "Updated Report"
            
            # Verify update
            verified = ReportService.get_by_id(report_id)
            assert verified.title == "Updated Report"
            
            # Delete
            ReportService.delete(report_id)
            with pytest.raises(NotFoundError):
                ReportService.get_by_id(report_id)
    
    def test_multiple_reports_lifecycle(self, app):
        """Test creating and managing multiple reports."""
        with app.app_context():
            reports = [
                ReportService.create(title=f"Report {i}", description=f"Description {i}")
                for i in range(1, 4)
            ]
            
            assert len(ReportService.get_all()) == 3
            
            ReportService.delete(reports[0].id)
            assert len(ReportService.get_all()) == 2
            
            ReportService.create(title="New Report")
            assert len(ReportService.get_all()) == 3
