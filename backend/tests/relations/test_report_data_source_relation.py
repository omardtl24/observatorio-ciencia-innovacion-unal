"""Unit tests for ReportDataSourceRelation."""

import pytest
from app.services.relations.report_data_source_relation import ReportDataSourceRelation
from app.services.report_service import ReportService
from app.services.data_source_service import DataSourceService
from app.domain.exceptions import NotFoundError, IllegalOperationError


class TestReportDataSourceRelationAdd:
    """Tests for adding data source to report."""
    
    def test_add_data_source_to_report(self, app, test_file):
        """Test adding a data source to a report."""
        with app.app_context():
            report = ReportService.create(title="Analytics Report")
            data_source = DataSourceService.create(name="API Source", file_id=test_file.id)
            
            report_result, ds_result = ReportDataSourceRelation.add_data_source_to_report(report.id, data_source.id)
            
            assert report_result.id == report.id
            assert ds_result.id == data_source.id
            assert data_source in report.data_sources
    
    def test_add_duplicate_data_source_raises_error(self, app, test_file):
        """Test that adding duplicate data source raises error."""
        with app.app_context():
            report = ReportService.create(title="Test Report")
            data_source = DataSourceService.create(name="DB Source", file_id=test_file.id)
            
            ReportDataSourceRelation.add_data_source_to_report(report.id, data_source.id)
            
            with pytest.raises(IllegalOperationError):
                ReportDataSourceRelation.add_data_source_to_report(report.id, data_source.id)
    
    def test_add_data_source_to_nonexistent_report_raises_error(self, app, test_file):
        """Test that adding data source to nonexistent report raises error."""
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=test_file.id)
            
            with pytest.raises(NotFoundError):
                ReportDataSourceRelation.add_data_source_to_report(9999, data_source.id)
    
    def test_add_nonexistent_data_source_to_report_raises_error(self, app):
        """Test that adding nonexistent data source raises error."""
        with app.app_context():
            report = ReportService.create(title="Report")
            
            with pytest.raises(NotFoundError):
                ReportDataSourceRelation.add_data_source_to_report(report.id, 9999)


class TestReportDataSourceRelationRemove:
    """Tests for removing data source from report."""
    
    def test_remove_data_source_from_report(self, app, test_file):
        """Test removing a data source from a report."""
        with app.app_context():
            report = ReportService.create(title="Report")
            data_source = DataSourceService.create(name="Source", file_id=test_file.id)
            ReportDataSourceRelation.add_data_source_to_report(report.id, data_source.id)
            
            report_result, ds_result = ReportDataSourceRelation.remove_data_source_from_report(report.id, data_source.id)
            
            assert data_source not in report.data_sources
    
    def test_remove_nonexistent_data_source_from_report_raises_error(self, app, test_file):
        """Test that removing unassigned data source raises error."""
        with app.app_context():
            report = ReportService.create(title="Report")
            data_source = DataSourceService.create(name="Source", file_id=test_file.id)
            
            with pytest.raises(IllegalOperationError):
                ReportDataSourceRelation.remove_data_source_from_report(report.id, data_source.id)


class TestReportDataSourceRelationGet:
    """Tests for getting relationships."""
    
    def test_get_all_data_sources_for_report(self, app, test_file):
        """Test getting all data sources for a report."""
        with app.app_context():
            report = ReportService.create(title="Multi-source Report")
            ds1 = DataSourceService.create(name="Source 1", file_id=test_file.id)
            ds2 = DataSourceService.create(name="Source 2", file_id=test_file.id)
            
            ReportDataSourceRelation.add_data_source_to_report(report.id, ds1.id)
            ReportDataSourceRelation.add_data_source_to_report(report.id, ds2.id)
            
            data_sources = ReportDataSourceRelation.get_all_b_for_a(report.id)
            
            assert len(data_sources) == 2
            assert ds1 in data_sources
            assert ds2 in data_sources
    
    def test_get_all_reports_for_data_source(self, app, test_file):
        """Test getting all reports for a data source."""
        with app.app_context():
            report1 = ReportService.create(title="Report 1")
            report2 = ReportService.create(title="Report 2")
            data_source = DataSourceService.create(name="Shared Source", file_id=test_file.id)
            
            ReportDataSourceRelation.add_data_source_to_report(report1.id, data_source.id)
            ReportDataSourceRelation.add_data_source_to_report(report2.id, data_source.id)
            
            reports = ReportDataSourceRelation.get_all_a_for_b(data_source.id)
            
            assert len(reports) == 2
            assert report1 in reports
            assert report2 in reports


class TestReportDataSourceRelationRemoveAll:
    """Tests for removing all relationships."""
    
    def test_remove_all_data_sources_for_report(self, app, test_file):
        """Test removing all data sources from a report."""
        with app.app_context():
            report = ReportService.create(title="Report")
            ds1 = DataSourceService.create(name="DS1", file_id=test_file.id)
            ds2 = DataSourceService.create(name="DS2", file_id=test_file.id)
            
            ReportDataSourceRelation.add_data_source_to_report(report.id, ds1.id)
            ReportDataSourceRelation.add_data_source_to_report(report.id, ds2.id)
            
            ReportDataSourceRelation.remove_all_b_for_a(report.id)
            
            data_sources = ReportDataSourceRelation.get_all_b_for_a(report.id)
            assert len(data_sources) == 0
    
    def test_remove_all_reports_for_data_source(self, app, test_file):
        """Test removing all reports from a data source."""
        with app.app_context():
            report1 = ReportService.create(title="R1")
            report2 = ReportService.create(title="R2")
            data_source = DataSourceService.create(name="DS", file_id=test_file.id)
            
            ReportDataSourceRelation.add_data_source_to_report(report1.id, data_source.id)
            ReportDataSourceRelation.add_data_source_to_report(report2.id, data_source.id)
            
            ReportDataSourceRelation.remove_all_a_for_b(data_source.id)
            
            reports = ReportDataSourceRelation.get_all_a_for_b(data_source.id)
            assert len(reports) == 0


class TestReportDataSourceRelationIntegration:
    """Integration tests for ReportDataSourceRelation."""
    
    def test_complete_relationship_lifecycle(self, app, test_file):
        """Test complete lifecycle of report-datasource relationship."""
        with app.app_context():
            report = ReportService.create(title="Dashboard")
            ds1 = DataSourceService.create(name="API", file_id=test_file.id)
            ds2 = DataSourceService.create(name="DB", file_id=test_file.id)
            
            # Add data sources
            ReportDataSourceRelation.add_data_source_to_report(report.id, ds1.id)
            ReportDataSourceRelation.add_data_source_to_report(report.id, ds2.id)
            
            # Verify
            sources = ReportDataSourceRelation.get_all_b_for_a(report.id)
            assert len(sources) == 2
            
            # Remove one
            ReportDataSourceRelation.remove_data_source_from_report(report.id, ds1.id)
            sources = ReportDataSourceRelation.get_all_b_for_a(report.id)
            assert len(sources) == 1
            
            # Remove all
            ReportDataSourceRelation.remove_all_b_for_a(report.id)
            sources = ReportDataSourceRelation.get_all_b_for_a(report.id)
            assert len(sources) == 0
