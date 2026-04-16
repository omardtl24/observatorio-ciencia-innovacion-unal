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


class TestReportDataSourceEndpoints:
    def test_report_data_sources_add_get_delete(self, app, client, test_file):
        headers = _auth_headers(app)

        with app.app_context():
            report = ReportService.create(title="Reporte DS")
            data_source = DataSourceService.create(name="DS Reporte", file_id=test_file.id)
            report_id = report.id
            data_source_id = data_source.id

        with (
            patch("app.api.report_routes.AccessChecker.is_admin", return_value=True),
            patch("app.api.report_routes.AccessChecker.check_access", return_value=True),
        ):
            add_response = client.post(
                f"/report/{report_id}/data-sources/{data_source_id}",
                headers=headers,
            )
            assert add_response.status_code == 200

            get_response = client.get(
                f"/report/{report_id}/data-sources",
                headers=headers,
            )
            assert get_response.status_code == 200
            get_payload = get_response.get_json()
            assert any(item["id"] == data_source_id for item in get_payload)

            delete_response = client.delete(
                f"/report/{report_id}/data-sources/{data_source_id}",
                headers=headers,
            )
            assert delete_response.status_code == 200
            delete_payload = delete_response.get_json()
            assert all(item["id"] != data_source_id for item in delete_payload)


class TestVisorDataSourceEndpoints:
    def test_visor_data_sources_add_get_delete(self, app, client, test_file):
        headers = _auth_headers(app)

        with app.app_context():
            visor = VisorService.create(
                title="Visor DS",
                description="descripcion",
                visor_url="https://example.com/visor-ds",
            )
            data_source = DataSourceService.create(name="DS Visor", file_id=test_file.id)
            visor_id = visor.id
            data_source_id = data_source.id

        with (
            patch("app.api.visor_routes.AccessChecker.is_admin", return_value=True),
            patch("app.api.visor_routes.AccessChecker.check_access", return_value=True),
        ):
            add_response = client.post(
                f"/visor/{visor_id}/data-sources/{data_source_id}",
                headers=headers,
            )
            assert add_response.status_code == 200

            get_response = client.get(
                f"/visor/{visor_id}/data-sources",
                headers=headers,
            )
            assert get_response.status_code == 200
            get_payload = get_response.get_json()
            assert any(item["id"] == data_source_id for item in get_payload)

            delete_response = client.delete(
                f"/visor/{visor_id}/data-sources/{data_source_id}",
                headers=headers,
            )
            assert delete_response.status_code == 200
            delete_payload = delete_response.get_json()
            assert all(item["id"] != data_source_id for item in delete_payload)


class TestSimulatorDataSourceEndpoints:
    def test_simulator_data_sources_add_get_delete(self, app, client, test_file):
        headers = _auth_headers(app)

        with app.app_context():
            simulator = SimulatorService.create(title="Simulador DS")
            data_source = DataSourceService.create(name="DS Simulador", file_id=test_file.id)
            simulator_id = simulator.id
            data_source_id = data_source.id

        with (
            patch("app.api.simulator_routes.AccessChecker.is_admin", return_value=True),
            patch("app.api.simulator_routes.AccessChecker.check_access", return_value=True),
        ):
            add_response = client.post(
                f"/simulator/{simulator_id}/data-sources/{data_source_id}",
                headers=headers,
            )
            assert add_response.status_code == 200

            get_response = client.get(
                f"/simulator/{simulator_id}/data-sources",
                headers=headers,
            )
            assert get_response.status_code == 200
            get_payload = get_response.get_json()
            assert any(item["id"] == data_source_id for item in get_payload)

            delete_response = client.delete(
                f"/simulator/{simulator_id}/data-sources/{data_source_id}",
                headers=headers,
            )
            assert delete_response.status_code == 200
            delete_payload = delete_response.get_json()
            assert all(item["id"] != data_source_id for item in delete_payload)
