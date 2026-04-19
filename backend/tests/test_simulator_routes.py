from io import BytesIO
from unittest.mock import patch

from flask_jwt_extended import create_access_token

from app.services.simulator_service import SimulatorService


def _auth_headers(app, identity="admin@unal.edu.co"):
    with app.app_context():
        token = create_access_token(identity=identity)
    return {"Authorization": f"Bearer {token}"}


class _AdminRole:
    id = 1


class TestSimulatorRoutes:
    def test_create_simulator_with_r_program_file(self, app, client):
        headers = _auth_headers(app)

        app.config["RESOURCES_BASE_URL"] = "https://resources.example.com"
        app.config["RESOURCES_SHARED_FOLDER"] = "/tmp/observatorio-test-shared"

        with (
            patch("app.api.simulator_routes.AccessChecker.is_admin", return_value=True),
            patch("app.api.simulator_routes.AccessChecker.grant_admin_access", return_value=(None, None)),
            patch("app.api.simulator_routes.RoleService.get_by_name", return_value=_AdminRole()),
        ):
            response = client.post(
                "/simulator",
                data={
                    "title": "Simulador R",
                    "description": "Con programa R",
                    "updated_at": "2026-04-19T12:00:00",
                    "r_program": (BytesIO(b"print('hola')"), "programa.R"),
                },
                headers=headers,
                content_type="multipart/form-data",
            )

        assert response.status_code == 201
        payload = response.get_json()
        assert payload["title"] == "Simulador R"
        assert payload["simulator_url"].startswith("https://resources.example.com/")

    def test_update_simulator_with_r_program_file(self, app, client):
        headers = _auth_headers(app)

        app.config["RESOURCES_BASE_URL"] = "https://resources.example.com"
        app.config["RESOURCES_SHARED_FOLDER"] = "/tmp/observatorio-test-shared"

        with app.app_context():
            simulator = SimulatorService.create(title="Simulador base")
            simulator_id = simulator.id

        with patch("app.api.simulator_routes.AccessChecker.is_admin", return_value=True):
            response = client.patch(
                f"/simulator/{simulator_id}",
                data={
                    "title": "Simulador actualizado",
                    "r_program": (BytesIO(b"print('update')"), "actualizacion.R"),
                },
                headers=headers,
                content_type="multipart/form-data",
            )

        assert response.status_code == 200
        payload = response.get_json()
        assert payload["title"] == "Simulador actualizado"
        assert payload["simulator_url"].startswith("https://resources.example.com/")
