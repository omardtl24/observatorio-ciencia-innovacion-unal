from unittest.mock import patch

from flask_jwt_extended import create_access_token


def _auth_headers(app, identity="admin@unal.edu.co"):
    with app.app_context():
        token = create_access_token(identity=identity)
    return {"Authorization": f"Bearer {token}"}


class TestResourceRoutes:
    def test_validate_resource_access_returns_200_when_user_has_access(self, app, client):
        headers = _auth_headers(app, identity="user@unal.edu.co")

        with patch("app.api.resource_routes.AccessChecker.check_access", return_value=True):
            response = client.get("/resource/1?resourceType=simulator", headers=headers)

        assert response.status_code == 200

    def test_validate_resource_access_returns_403_when_user_lacks_access(self, app, client):
        headers = _auth_headers(app, identity="user@unal.edu.co")

        with patch("app.api.resource_routes.AccessChecker.check_access", return_value=False):
            response = client.get("/resource/1?resourceType=visor", headers=headers)

        assert response.status_code == 403

    def test_validate_resource_access_returns_403_when_resource_type_is_invalid(self, app, client):
        headers = _auth_headers(app, identity="user@unal.edu.co")

        with patch("app.api.resource_routes.AccessChecker.check_access") as mock_check_access:
            response = client.get("/resource/1?resourceType=report", headers=headers)

        assert response.status_code == 403
        mock_check_access.assert_not_called()
