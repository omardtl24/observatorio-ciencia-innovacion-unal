
import pytest # type: ignore
from unittest.mock import Mock, patch, MagicMock
from app.services.auth_service import AuthService
from app.domain.exceptions import NotFoundError, IllegalOperationError

@pytest.fixture
def mock_app(app):
    """Fixture for app with Auth0 configuration."""
    with app.app_context():
        app.config['AUTH0_CLIENT_ID'] = 'test_client_id'
        app.config['AUTH0_CLIENT_SECRET'] = 'test_client_secret'
        app.config['AUTH0_DOMAIN'] = 'test-domain.auth0.com'
        app.config['RESTRICTED_EMAIL_DOMAIN'] = 'unal.edu.co'
        yield app


@pytest.fixture
def auth_service(mock_app):
    """Fixture for AuthService instance with mocked OAuth."""
    with patch('app.services.auth_service.OAuth') as mock_oauth_class:
        mock_oauth = Mock()
        mock_auth0 = Mock()
        mock_oauth.register.return_value = mock_auth0
        mock_oauth_class.return_value = mock_oauth
        
        service = AuthService(mock_app)
        service.auth0 = mock_auth0
        yield service


@pytest.fixture
def valid_user_info():
    """Fixture for valid Auth0 user info."""
    return {
        'email': 'test.user@unal.edu.co',
        'given_name': 'Test',
        'family_name': 'User',
        'picture': 'https://example.com/picture.jpg'
    }


@pytest.fixture
def valid_token(valid_user_info):
    """Fixture for valid Auth0 token."""
    return {
        'userinfo': valid_user_info,
        'access_token': 'auth0_access_token',
        'id_token': 'auth0_id_token'
    }

class TestAuthServiceInit:
    """Tests for AuthService initialization."""
    
    def test_init_creates_oauth_client(self, mock_app):
        """Test that AuthService initializes OAuth client correctly."""
        with patch('app.services.auth_service.OAuth') as mock_oauth_class:
            mock_oauth = Mock()
            mock_oauth_class.return_value = mock_oauth
            
            service = AuthService(mock_app)
            
            mock_oauth_class.assert_called_once_with(mock_app)
            mock_oauth.register.assert_called_once()
            assert service.oauth == mock_oauth
    
    def test_init_registers_auth0_with_correct_config(self, mock_app):
        """Test that Auth0 is registered with correct configuration."""
        with patch('app.services.auth_service.OAuth') as mock_oauth_class:
            mock_oauth = Mock()
            mock_oauth_class.return_value = mock_oauth
            
            AuthService(mock_app)
            
            call_args = mock_oauth.register.call_args
            assert call_args[0][0] == 'auth0'
            assert call_args[1]['client_id'] == 'test_client_id'
            assert call_args[1]['client_secret'] == 'test_client_secret'
            assert 'openid profile email' in call_args[1]['client_kwargs']['scope']


class TestAuthServiceProcessCallbackNew:
    """Tests for process_callback_for_redirect with new user."""
    
    @patch('app.services.auth_service.create_access_token')
    @patch('app.services.auth_service.UserService')
    def test_successful_callback_creates_new_user(
        self, mock_user_service, mock_create_token, auth_service, mock_app, 
        valid_token, valid_user_info
    ):
        """Test successful authentication creating a new user."""
        with mock_app.app_context():
            # Setup mocks
            auth_service.auth0.authorize_access_token.return_value = valid_token
            
            mock_user = Mock()
            mock_user.email = valid_user_info['email']
            mock_user.names = valid_user_info['given_name']
            mock_user.last_names = valid_user_info['family_name']
            
            mock_user_service.create.return_value = mock_user
            mock_user_service.update.return_value = mock_user
            mock_create_token.return_value = 'jwt_token_123'
            
            # Execute
            result = auth_service.process_callback_for_redirect()
            
            # Verify
            mock_user_service.create.assert_called_once_with(
                email='test.user@unal.edu.co',
                names='Test',
                last_names='User'
            )
            mock_user_service.update.assert_called_once()
            mock_create_token.assert_called_once_with(identity='test.user@unal.edu.co')
            
            assert result['access_token'] == 'jwt_token_123'
            assert result['email'] == 'test.user@unal.edu.co'
            assert result['names'] == 'Test'
            assert result['last_names'] == 'User'
            assert result['picture'] == 'https://example.com/picture.jpg'


class TestAuthServiceProcessCallbackExisting:
    """Tests for process_callback_for_redirect with existing user."""
    
    @patch('app.services.auth_service.create_access_token')
    @patch('app.services.auth_service.UserService')
    def test_successful_callback_with_existing_user(
        self, mock_user_service, mock_create_token, auth_service, mock_app,
        valid_token, valid_user_info
    ):
        """Test successful authentication with existing user."""
        with mock_app.app_context():
            # Setup mocks
            auth_service.auth0.authorize_access_token.return_value = valid_token
            
            mock_user = Mock()
            mock_user.email = valid_user_info['email']
            mock_user.names = valid_user_info['given_name']
            mock_user.last_names = valid_user_info['family_name']
            
            # Simulate existing user (create raises IllegalOperationError)
            mock_user_service.create.side_effect = IllegalOperationError("User exists")
            mock_user_service.get_by_id.return_value = mock_user
            mock_user_service.update.return_value = mock_user
            mock_create_token.return_value = 'jwt_token_456'
            
            # Execute
            result = auth_service.process_callback_for_redirect()
            
            # Verify
            mock_user_service.create.assert_called_once()
            mock_user_service.get_by_id.assert_called_once_with('test.user@unal.edu.co')
            mock_user_service.update.assert_called_once()
            
            assert result['access_token'] == 'jwt_token_456'
            assert result['email'] == 'test.user@unal.edu.co'
    
    @patch('app.services.auth_service.create_access_token')
    @patch('app.services.auth_service.UserService')
    def test_callback_uses_id_token_when_no_userinfo(
        self, mock_user_service, mock_create_token, auth_service, mock_app,
        valid_user_info
    ):
        """Test callback uses parse_id_token when userinfo is not present."""
        with mock_app.app_context():
            # Setup token without userinfo
            token_without_userinfo = {
                'access_token': 'auth0_token',
                'id_token': 'id_token_123'
            }
            auth_service.auth0.authorize_access_token.return_value = token_without_userinfo
            auth_service.auth0.parse_id_token.return_value = valid_user_info
            
            mock_user = Mock()
            mock_user.email = valid_user_info['email']
            mock_user.names = valid_user_info['given_name']
            mock_user.last_names = valid_user_info['family_name']
            
            mock_user_service.create.return_value = mock_user
            mock_user_service.update.return_value = mock_user
            mock_create_token.return_value = 'jwt_token'
            
            # Execute
            result = auth_service.process_callback_for_redirect()
            
            # Verify parse_id_token was called
            auth_service.auth0.parse_id_token.assert_called_once_with(token_without_userinfo)
            assert result['email'] == 'test.user@unal.edu.co'


class TestAuthServiceProcessCallbackErrors:
    """Tests for process_callback_for_redirect error cases."""
    
    def test_callback_raises_error_when_no_user_info(self, auth_service, mock_app):
        """Test that NotFoundError is raised when user_info is not available."""
        with mock_app.app_context():
            # Setup mocks
            auth_service.auth0.authorize_access_token.return_value = {'access_token': 'token'}
            auth_service.auth0.parse_id_token.return_value = None
            
            # Execute and verify
            with pytest.raises(NotFoundError) as exc_info:
                auth_service.process_callback_for_redirect()
            
            assert "No se pudo obtener el perfil del usuario" in str(exc_info.value)
    
    def test_callback_raises_error_when_no_email(self, auth_service, mock_app):
        """Test that NotFoundError is raised when email is missing."""
        with mock_app.app_context():
            # Setup token with user info but no email
            token = {
                'userinfo': {
                    'given_name': 'Test',
                    'family_name': 'User'
                    # Missing email
                }
            }
            auth_service.auth0.authorize_access_token.return_value = token
            
            # Execute and verify
            with pytest.raises(NotFoundError) as exc_info:
                auth_service.process_callback_for_redirect()
            
            assert "no proporcionó un correo electrónico" in str(exc_info.value)
    
    @patch('app.services.auth_service.create_access_token')
    @patch('app.services.auth_service.UserService')
    def test_callback_allows_invalid_email_domain(
        self, mock_user_service, mock_create_token, auth_service, mock_app
    ):
        """Test that non-community domains are allowed and authenticated."""
        with mock_app.app_context():
            # Setup token with wrong email domain
            token = {
                'userinfo': {
                    'email': 'test@invalid-domain.com',
                    'given_name': 'Test',
                    'family_name': 'User'
                }
            }
            auth_service.auth0.authorize_access_token.return_value = token

            mock_user = Mock()
            mock_user.email = 'test@invalid-domain.com'
            mock_user.names = 'Test'
            mock_user.last_names = 'User'
            mock_user.roles = []

            mock_user_service.create.return_value = mock_user
            mock_user_service.update.return_value = mock_user
            mock_create_token.return_value = 'jwt_token'
            
            # Execute and verify
            result = auth_service.process_callback_for_redirect()
            assert result['email'] == 'test@invalid-domain.com'
    
    @patch('app.services.auth_service.create_access_token')
    @patch('app.services.auth_service.UserService')
    def test_callback_allows_email_with_partial_domain_match(
        self, mock_user_service, mock_create_token, auth_service, mock_app
    ):
        """Test that partial domain matches are also allowed by current auth logic."""
        with mock_app.app_context():
            # Setup token with email that contains but doesn't end with domain
            token = {
                'userinfo': {
                    'email': 'test@notunal.edu.co.fake.com',
                    'given_name': 'Test',
                    'family_name': 'User'
                }
            }
            auth_service.auth0.authorize_access_token.return_value = token

            mock_user = Mock()
            mock_user.email = 'test@notunal.edu.co.fake.com'
            mock_user.names = 'Test'
            mock_user.last_names = 'User'
            mock_user.roles = []

            mock_user_service.create.return_value = mock_user
            mock_user_service.update.return_value = mock_user
            mock_create_token.return_value = 'jwt_token'
            
            # Execute and verify
            result = auth_service.process_callback_for_redirect()
            assert result['email'] == 'test@notunal.edu.co.fake.com'


class TestAuthServiceProcessCallbackEdgeCases:
    """Tests for edge cases in process_callback_for_redirect."""
    
    @patch('app.services.auth_service.create_access_token')
    @patch('app.services.auth_service.UserService')
    def test_callback_handles_missing_optional_fields(
        self, mock_user_service, mock_create_token, auth_service, mock_app
    ):
        """Test callback handles missing optional fields (names)."""
        with mock_app.app_context():
            # Setup token with minimal user info
            token = {
                'userinfo': {
                    'email': 'minimal@unal.edu.co'
                    # Missing given_name, family_name, picture
                }
            }
            auth_service.auth0.authorize_access_token.return_value = token
            
            mock_user = Mock()
            mock_user.email = 'minimal@unal.edu.co'
            mock_user.names = ''
            mock_user.last_names = ''
            
            mock_user_service.create.return_value = mock_user
            mock_user_service.update.return_value = mock_user
            mock_create_token.return_value = 'jwt_token'
            
            # Execute
            result = auth_service.process_callback_for_redirect()
            
            # Verify
            mock_user_service.create.assert_called_once_with(
                email='minimal@unal.edu.co',
                names='',
                last_names=''
            )
            assert result['email'] == 'minimal@unal.edu.co'
            assert result['names'] == ''
            assert result['last_names'] == ''
            assert result['picture'] is None
    
    @patch('app.services.auth_service.create_access_token')
    @patch('app.services.auth_service.UserService')
    @patch('app.services.auth_service.db')
    def test_callback_updates_last_login_at(
        self, mock_db, mock_user_service, mock_create_token, auth_service, 
        mock_app, valid_token
    ):
        """Test that callback updates user's last_login_at."""
        with mock_app.app_context():
            # Setup mocks
            auth_service.auth0.authorize_access_token.return_value = valid_token
            
            mock_user = Mock()
            mock_user.email = 'test.user@unal.edu.co'
            mock_user.names = 'Test'
            mock_user.last_names = 'User'
            
            mock_user_service.create.return_value = mock_user
            mock_user_service.update.return_value = mock_user
            mock_create_token.return_value = 'jwt_token'
            
            # Execute
            auth_service.process_callback_for_redirect()
            
            # Verify update was called with last_login_at
            update_call = mock_user_service.update.call_args
            assert update_call[0][0] == 'test.user@unal.edu.co'
            assert 'last_login_at' in update_call[1]


class TestAuthServiceIntegration:
    """Integration tests for AuthService."""
    
    @patch('app.services.auth_service.create_access_token')
    @patch('app.services.auth_service.UserService')
    def test_complete_authentication_flow(
        self, mock_user_service, mock_create_token, auth_service, mock_app,
        valid_token, valid_user_info
    ):
        """Test complete authentication flow from callback to token generation."""
        with mock_app.app_context():
            # Setup mocks
            auth_service.auth0.authorize_access_token.return_value = valid_token
            
            mock_user = Mock()
            mock_user.email = valid_user_info['email']
            mock_user.names = valid_user_info['given_name']
            mock_user.last_names = valid_user_info['family_name']
            
            mock_user_service.create.return_value = mock_user
            mock_user_service.update.return_value = mock_user
            mock_create_token.return_value = 'complete_jwt_token'
            
            # Execute
            result = auth_service.process_callback_for_redirect()
            
            # Verify complete flow
            assert auth_service.auth0.authorize_access_token.called
            assert mock_user_service.create.called or mock_user_service.get_by_id.called
            assert mock_user_service.update.called
            assert mock_create_token.called
            
            # Verify result structure
            assert 'access_token' in result
            assert 'email' in result
            assert 'names' in result
            assert 'last_names' in result
            assert 'picture' in result
            assert len(result) == 5
