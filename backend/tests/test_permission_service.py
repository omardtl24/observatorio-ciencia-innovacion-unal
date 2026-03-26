from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from app.domain.exceptions import IllegalOperationError, UnauthorizedError
from app.services.permission_service import PermissionService


@pytest.fixture
def permission_service(app):
    with app.app_context():
        app.config["CLIENT_ID"] = "test-client-id"
        app.config["CLIENT_SECRET"] = "test-client-secret"
        app.config["REFRESH_TOKEN"] = "test-refresh-token"
        yield PermissionService(app)


class TestPermissionServiceTokenRefresh:
    def test_refresh_access_token_success(self, permission_service):
        with patch("app.services.permission_service.requests.post") as mock_post:
            response = Mock(status_code=200)
            response.json.return_value = {
                "access_token": "token-1",
                "expires_in": 3600,
            }
            mock_post.return_value = response

            token = permission_service._refresh_access_token(force=True)

            assert token == "token-1"
            assert permission_service._access_token == "token-1"
            assert permission_service._access_token_expires_at is not None
            assert permission_service._access_token_expires_at > datetime.utcnow()

    def test_refresh_access_token_uses_cached_token(self, permission_service):
        permission_service._access_token = "cached-token"
        permission_service._access_token_expires_at = datetime.utcnow() + timedelta(minutes=5)

        with patch("app.services.permission_service.requests.post") as mock_post:
            token = permission_service._refresh_access_token(force=False)

            assert token == "cached-token"
            mock_post.assert_not_called()

    def test_refresh_access_token_updates_rotated_refresh_token(self, permission_service):
        with patch("app.services.permission_service.requests.post") as mock_post:
            response = Mock(status_code=200)
            response.json.return_value = {
                "access_token": "token-1",
                "expires_in": 3600,
                "refresh_token": "new-refresh-token",
            }
            mock_post.return_value = response

            permission_service._refresh_access_token(force=True)

            assert permission_service.app.config["REFRESH_TOKEN"] == "new-refresh-token"

    def test_refresh_access_token_requires_refresh_token(self, permission_service):
        permission_service.app.config["REFRESH_TOKEN"] = None

        with pytest.raises(UnauthorizedError):
            permission_service._refresh_access_token(force=True)

    def test_refresh_access_token_raises_on_http_error(self, permission_service):
        with patch("app.services.permission_service.requests.post") as mock_post:
            response = Mock(status_code=400)
            response.json.return_value = {"error": "invalid_grant"}
            mock_post.return_value = response

            with pytest.raises(UnauthorizedError):
                permission_service._refresh_access_token(force=True)


class TestPermissionServiceRequests:
    def test_request_with_auto_refresh_retries_on_401(self, permission_service):
        response_unauthorized = Mock(status_code=401)
        response_ok = Mock(status_code=200)

        with (
            patch.object(
                permission_service,
                "_refresh_access_token",
                side_effect=["token-1", "token-2"],
            ) as mock_refresh,
            patch(
                "app.services.permission_service.requests.request",
                side_effect=[response_unauthorized, response_ok],
            ) as mock_request,
        ):
            response = permission_service._request_with_auto_refresh("GET", "https://example.com")

            assert response is response_ok
            assert mock_refresh.call_count == 2
            assert mock_request.call_count == 2
            assert mock_request.call_args_list[0].kwargs["headers"]["Authorization"] == "Bearer token-1"
            assert mock_request.call_args_list[1].kwargs["headers"]["Authorization"] == "Bearer token-2"

    def test_add_viewers_builds_expected_params(self, permission_service):
        response = Mock(status_code=200)
        response.json.return_value = {"ok": True}

        with patch.object(permission_service, "_request_with_auto_refresh", return_value=response) as mock_request:
            result = permission_service.addViewers("asset-123", ["a@unal.edu.co", "b@unal.edu.co"])

            assert result == {"ok": True}
            mock_request.assert_called_once_with(
                "POST",
                "https://datastudio.googleapis.com/v1/assets/asset-123/permissions:addMembers",
                params={
                    "role": "VIEWER",
                    "members": ["user:a@unal.edu.co", "user:b@unal.edu.co"],
                },
            )


class TestPermissionServiceRolesAndTokenState:
    def test_apply_role_permissions_dispatches_supported_roles(self, permission_service):
        with (
            patch.object(permission_service, "addViewers", return_value={"role": "viewer"}) as mock_add_viewers,
            patch.object(permission_service, "addEditors", return_value={"role": "editor"}) as mock_add_editors,
            patch.object(permission_service, "removeViewers", return_value={"role": "remove"}) as mock_remove_viewers,
        ):
            viewers_result = permission_service.applyRolePermissions("asset-1", "VIEWER", ["user@test.com"])
            editors_result = permission_service.applyRolePermissions("asset-1", "EDITOR", ["svc@test.com"])
            remove_result = permission_service.applyRolePermissions("asset-1", "REMOVE_VIEWER", ["user@test.com"])

            assert viewers_result["role"] == "viewer"
            assert editors_result["role"] == "editor"
            assert remove_result["role"] == "remove"
            mock_add_viewers.assert_called_once()
            mock_add_editors.assert_called_once()
            mock_remove_viewers.assert_called_once()

    def test_apply_role_permissions_rejects_unsupported_role(self, permission_service):
        with pytest.raises(IllegalOperationError):
            permission_service.applyRolePermissions("asset-1", "OWNER", ["user@test.com"])

    def test_update_refresh_token_updates_config_and_clears_cache(self, permission_service):
        permission_service._access_token = "old-token"
        permission_service._access_token_expires_at = datetime.utcnow() + timedelta(minutes=10)

        result = permission_service.updateRefreshToken(" new-token ")

        assert result is True
        assert permission_service.app.config["REFRESH_TOKEN"] == "new-token"
        assert permission_service._access_token is None
        assert permission_service._access_token_expires_at is None

    def test_update_refresh_token_rejects_empty_values(self, permission_service):
        with pytest.raises(IllegalOperationError):
            permission_service.updateRefreshToken(" ")

    def test_is_refresh_token_valid_returns_true_when_refresh_succeeds(self, permission_service):
        with patch.object(permission_service, "_refresh_access_token", return_value="token"):
            assert permission_service.isRefreshTokenValid() is True

    def test_is_refresh_token_valid_returns_false_when_refresh_fails(self, permission_service):
        with patch.object(permission_service, "_refresh_access_token", side_effect=UnauthorizedError("invalid")):
            assert permission_service.isRefreshTokenValid() is False