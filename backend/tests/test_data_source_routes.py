from unittest.mock import patch

from flask_jwt_extended import create_access_token

from app.services.data_source_service import DataSourceService
from app.services.report_service import ReportService
from app.services.simulator_service import SimulatorService
from app.services.visor_service import VisorService


def _auth_headers(app, identity="admin@unal.edu.co"):
    with app.app_context():
        token = create_access_token(identity=identity)
    return {"Authorization": f"Bearer {token}"}


class TestDataSourceRoutes:
    def test_create_data_source_success(self, app, client, test_file):
        headers = _auth_headers(app)

        with (
            patch("app.api.data_source_routes.AccessChecker.is_admin", return_value=True),
            patch("app.api.data_source_routes.AccessChecker.grant_admin_access", return_value=(None, None)),
        ):
            response = client.post(
                "/data-source",
                json={
                    "name": "Indicadores",
                    "description": "Fuente principal",
                    "file_id": test_file.id,
                    "updated_at": "2026-04-16T10:30:00",
                },
                headers=headers,
            )

        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "Indicadores"
        assert data["file_id"] == test_file.id

    def test_associate_data_source_to_report(self, app, client, test_file):
        headers = _auth_headers(app)

        with app.app_context():
            report = ReportService.create(title="Reporte A")
            data_source = DataSourceService.create(name="Fuente A", file_id=test_file.id)
            report_id = report.id
            data_source_id = data_source.id

        with patch("app.api.data_source_routes.AccessChecker.is_admin", return_value=True):
            response = client.post(
                f"/data-source/{data_source_id}/report/{report_id}",
                headers=headers,
            )

        assert response.status_code == 200
        data = response.get_json()
        assert data_source_id in data["data_source_ids"]

    def test_associate_data_source_to_visor(self, app, client, test_file):
        headers = _auth_headers(app)

        with app.app_context():
            visor = VisorService.create(
                title="Visor A",
                description="Visor",
                visor_url="https://example.com/visor-a",
            )
            data_source = DataSourceService.create(name="Fuente B", file_id=test_file.id)
            visor_id = visor.id
            data_source_id = data_source.id

        with patch("app.api.data_source_routes.AccessChecker.is_admin", return_value=True):
            response = client.post(
                f"/data-source/{data_source_id}/visor/{visor_id}",
                headers=headers,
            )

        assert response.status_code == 200
        data = response.get_json()
        assert data_source_id in data["data_source_ids"]

    def test_associate_data_source_to_simulator(self, app, client, test_file):
        headers = _auth_headers(app)

        with app.app_context():
            simulator = SimulatorService.create(title="Simulador A")
            data_source = DataSourceService.create(name="Fuente C", file_id=test_file.id)
            simulator_id = simulator.id
            data_source_id = data_source.id

        with patch("app.api.data_source_routes.AccessChecker.is_admin", return_value=True):
            response = client.post(
                f"/data-source/{data_source_id}/simulator/{simulator_id}",
                headers=headers,
            )

        assert response.status_code == 200
        data = response.get_json()
        assert data_source_id in data["data_source_ids"]
