from unittest.mock import patch

from flask_jwt_extended import create_access_token


def _auth_headers(app, identity="user@unal.edu.co"):
    with app.app_context():
        token = create_access_token(identity=identity)
    return {"Authorization": f"Bearer {token}"}


class TestRoleRoutes:
    def test_validate_resource_access_accepts_data_source_type(self, app, client):
        headers = _auth_headers(app, identity="reader@unal.edu.co")

        with patch("app.api.role_routes.AccessChecker.check_access", return_value=True) as mock_check_access:
            response = client.get(
                "/role/validate?id=15&resourceType=data-source",
                headers=headers,
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["has_access"] is True
            assert data["resource_id"] == 15
            assert data["resourceType"] == "data_source"
            mock_check_access.assert_called_once_with("reader@unal.edu.co", 15, "data_source")

    def test_validate_resource_access_returns_true_when_access_exists(self, app, client):
        headers = _auth_headers(app, identity="reader@unal.edu.co")

        with patch("app.api.role_routes.AccessChecker.check_access", return_value=True) as mock_check_access:
            response = client.get(
                "/role/validate?id=42&resourceType=report",
                headers=headers,
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["has_access"] is True
            assert data["resource_id"] == 42
            assert data["resourceType"] == "report"
            mock_check_access.assert_called_once_with("reader@unal.edu.co", 42, "report")

    def test_validate_resource_access_returns_false_when_access_missing(self, app, client):
        headers = _auth_headers(app, identity="reader@unal.edu.co")

        with patch("app.api.role_routes.AccessChecker.check_access", return_value=False) as mock_check_access:
            response = client.get(
                "/role/validate?id=7&resourceType=visor",
                headers=headers,
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["has_access"] is False
            assert data["resource_id"] == 7
            assert data["resourceType"] == "visor"
            mock_check_access.assert_called_once_with("reader@unal.edu.co", 7, "visor")

    def test_validate_resource_access_rejects_missing_parameters(self, app, client):
        headers = _auth_headers(app)

        response = client.get("/role/validate?resourceType=report", headers=headers)

        assert response.status_code == 400
        data = response.get_json()
        assert data["message"] == "Los parámetros id y resourceType son obligatorios"

    def test_validate_resource_access_rejects_invalid_resource_type(self, app, client):
        headers = _auth_headers(app)

        response = client.get("/role/validate?id=1&resourceType=unknown", headers=headers)

        assert response.status_code == 400
        data = response.get_json()
        assert data["message"].startswith("El tipo de recurso no es válido")
