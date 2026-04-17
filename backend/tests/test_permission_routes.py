from unittest.mock import Mock, patch

from flask_jwt_extended import create_access_token  # type: ignore
from app.domain.exceptions import UnauthorizedError


def _auth_headers(app, identity="admin@unal.edu.co"):
    with app.app_context():
        token = create_access_token(identity=identity)
    return {"Authorization": f"Bearer {token}"}


class TestPermissionRoutes:
    def test_update_refresh_token_success(self, app, client):
        headers = _auth_headers(app)

        with (
            patch("app.api.permission_routes.assert_admin"),
            patch("app.api.permission_routes.PermissionService") as mock_permission_service_class,
        ):
            mock_permission_service = Mock()
            mock_permission_service.isRefreshTokenValid.return_value = True
            mock_permission_service_class.return_value = mock_permission_service

            response = client.post(
                "/permissions/update-refresh-token",
                json={"refresh_token": "new-refresh-token"},
                headers=headers,
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["updated"] is True
            assert data["is_valid"] is True
            mock_permission_service.updateRefreshToken.assert_called_once_with("new-refresh-token")

    def test_update_refresh_token_forbidden_for_non_admin(self, app, client):
        headers = _auth_headers(app, identity="user@unal.edu.co")

        with (
            patch("app.api.permission_routes.assert_admin", side_effect=UnauthorizedError("forbidden")),
            patch("app.api.permission_routes.PermissionService") as mock_permission_service_class,
        ):
            response = client.post(
                "/permissions/update-refresh-token",
                json={"refresh_token": "new-refresh-token"},
                headers=headers,
            )

            assert response.status_code == 401
            mock_permission_service_class.assert_not_called()

    def test_update_refresh_token_validates_schema(self, app, client):
        headers = _auth_headers(app)

        with patch("app.api.permission_routes.assert_admin"):
            response = client.post(
                "/permissions/update-refresh-token",
                json={"invalid": "payload"},
                headers=headers,
            )

            assert response.status_code == 400