import base64
import hashlib
import secrets
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse

import pytest

from api import create_app
from api.app import db
from api.dao.users_dao import get_token
from api.models.models import User
from api.routes.mcp_oauth import auth_codes, exchange_authorization_code_for_session_token
from config import TestConfig


@pytest.fixture
def client():
    """Create test client with clean database."""
    app = create_app(TestConfig)
    client = app.test_client()
    with app.app_context():
        db.create_all()
        # Clear auth_codes before each test
        auth_codes.clear()
        yield client


@pytest.fixture
def test_user(client):
    """Create a test user and return user_id."""
    with client.application.app_context():
        user = User(email='test@example.com',
                    username='testuser', password='testpass')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        return user_id


@pytest.fixture
def test_user2(client):
    """Create a second test user and return user_id."""
    with client.application.app_context():
        user = User(email='test2@example.com',
                    username='testuser2', password='testpass2')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        return user_id


def generate_pkce_pair(method='S256'):
    """Generate a valid PKCE code_verifier and code_challenge pair."""
    code_verifier = secrets.token_urlsafe(32)
    if method == 'S256':
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).rstrip(b'=').decode()
    else:
        code_challenge = code_verifier
    return code_verifier, code_challenge


def create_auth_code(user_id, redirect_uri='http://localhost:3000/callback',
                     code_challenge=None, code_challenge_method='plain',
                     expires_in_minutes=10):
    """Create an authorization code in the auth_codes dictionary."""
    code = secrets.token_urlsafe(32)
    auth_codes[code] = {
        'user_id': user_id,
        'expires': datetime.utcnow() + timedelta(minutes=expires_in_minutes),
        'code_challenge': code_challenge,
        'code_challenge_method': code_challenge_method,
        'client_id': 'test_client',
        'redirect_uri': redirect_uri
    }
    return code


def create_expired_auth_code(user_id, redirect_uri='http://localhost:3000/callback'):
    """Create an expired authorization code."""
    code = secrets.token_urlsafe(32)
    auth_codes[code] = {
        'user_id': user_id,
        'expires': datetime.utcnow() - timedelta(minutes=1),  # Expired 1 minute ago
        'code_challenge': None,
        'code_challenge_method': 'plain',
        'client_id': 'test_client',
        'redirect_uri': redirect_uri
    }
    return code


# ============================================================================
# METADATA ENDPOINTS
# ============================================================================

def test_oauth_authorization_server_metadata(client):
    """Test OAuth authorization server metadata endpoint."""
    response = client.get('/.well-known/oauth-authorization-server')
    assert response.status_code == 200
    data = response.json

    assert 'issuer' in data
    assert 'authorization_endpoint' in data
    assert 'token_endpoint' in data
    assert 'registration_endpoint' in data
    assert 'grant_types_supported' in data
    assert 'response_types_supported' in data
    assert 'code_challenge_methods_supported' in data
    assert 'token_endpoint_auth_methods_supported' in data

    assert data['grant_types_supported'] == ['authorization_code']
    assert data['response_types_supported'] == ['code']
    assert 'S256' in data['code_challenge_methods_supported']
    assert 'plain' in data['code_challenge_methods_supported']


def test_oauth_protected_resource_metadata(client):
    """Test OAuth protected resource metadata endpoint."""
    response = client.get('/.well-known/oauth-protected-resource')
    assert response.status_code == 200
    data = response.json

    assert 'resource' in data
    assert 'authorization_servers' in data
    assert isinstance(data['authorization_servers'], list)


# ============================================================================
# GET /api/mcp/oauth/authorize
# ============================================================================

def test_authorize_get_success(client):
    """Test successful authorization redirect with all parameters."""
    params = {
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
        'response_type': 'code',
        'state': 'random_state_value',
        'code_challenge': 'test_challenge',
        'code_challenge_method': 'S256'
    }
    response = client.get('/api/mcp/oauth/authorize', query_string=params)

    assert response.status_code == 302  # Redirect
    assert 'Location' in response.headers
    location = response.headers['Location']
    assert '/oauth/authorize' in location

    # Parse query parameters from redirect URL
    parsed = urlparse(location)
    query_params = parse_qs(parsed.query)
    assert query_params['client_id'][0] == 'test_client'
    assert query_params['redirect_uri'][0] == 'http://localhost:3000/callback'
    assert query_params['response_type'][0] == 'code'
    assert query_params['state'][0] == 'random_state_value'
    assert query_params['code_challenge'][0] == 'test_challenge'
    assert query_params['code_challenge_method'][0] == 'S256'


def test_authorize_get_without_optional_params(client):
    """Test authorization redirect without optional parameters."""
    params = {
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
        'response_type': 'code'
    }
    response = client.get('/api/mcp/oauth/authorize', query_string=params)
    assert response.status_code == 302


def test_authorize_get_defaults_code_challenge_method(client):
    """Test that code_challenge_method defaults to 'plain' when not provided."""
    params = {
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
        'response_type': 'code',
        'code_challenge': 'test_challenge'
    }
    response = client.get('/api/mcp/oauth/authorize', query_string=params)
    assert response.status_code == 302
    location = response.headers['Location']
    parsed = urlparse(location)
    query_params = parse_qs(parsed.query)
    assert query_params.get('code_challenge_method', ['plain'])[0] == 'plain'


def test_authorize_get_missing_parameters(client):
    """Test authorization endpoint with missing required parameters."""
    # Missing client_id
    response = client.get('/api/mcp/oauth/authorize', query_string={
        'redirect_uri': 'http://localhost:3000/callback',
        'response_type': 'code'
    })
    assert response.status_code == 400

    # Missing redirect_uri
    response = client.get('/api/mcp/oauth/authorize', query_string={
        'client_id': 'test_client',
        'response_type': 'code'
    })
    assert response.status_code == 400

    # Missing response_type
    response = client.get('/api/mcp/oauth/authorize', query_string={
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback'
    })
    assert response.status_code == 400


def test_authorize_get_invalid_response_type(client):
    """Test authorization endpoint with invalid response_type."""
    params = {
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
        'response_type': 'token'  # Invalid, should be 'code'
    }
    response = client.get('/api/mcp/oauth/authorize', query_string=params)
    assert response.status_code == 400


# ============================================================================
# POST /api/mcp/oauth/authorize - Credential Validation
# ============================================================================

def test_authorize_post_success_with_email(client, test_user):
    """Test successful authorization with email login."""
    data = {
        'username': 'test@example.com',
        'password': 'testpass',
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
    }
    response = client.post('/api/mcp/oauth/authorize', json=data)

    assert response.status_code == 200
    result = response.json
    assert 'redirect_url' in result
    assert 'code=' in result['redirect_url']
    assert 'http://localhost:3000/callback' in result['redirect_url']

    # Verify auth code was created
    assert len(auth_codes) == 1
    code = result['redirect_url'].split('code=')[1].split('&')[0]
    assert code in auth_codes
    assert auth_codes[code]['user_id'] == test_user


def test_authorize_post_success_with_username(client, test_user):
    """Test successful authorization with username login."""
    data = {
        'username': 'testuser',
        'password': 'testpass',
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
    }
    response = client.post('/api/mcp/oauth/authorize', json=data)
    assert response.status_code == 200
    assert 'redirect_url' in response.json


def test_authorize_post_success_with_pkce_s256(client, test_user):
    """Test successful authorization with PKCE S256."""
    code_verifier, code_challenge = generate_pkce_pair('S256')
    data = {
        'username': 'testuser',
        'password': 'testpass',
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    response = client.post('/api/mcp/oauth/authorize', json=data)
    assert response.status_code == 200

    # Verify PKCE data was stored
    code = response.json['redirect_url'].split('code=')[1].split('&')[0]
    assert auth_codes[code]['code_challenge'] == code_challenge
    assert auth_codes[code]['code_challenge_method'] == 'S256'


def test_authorize_post_success_with_pkce_plain(client, test_user):
    """Test successful authorization with PKCE plain."""
    code_verifier, code_challenge = generate_pkce_pair('plain')
    data = {
        'username': 'testuser',
        'password': 'testpass',
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
        'code_challenge': code_challenge,
        'code_challenge_method': 'plain'
    }
    response = client.post('/api/mcp/oauth/authorize', json=data)
    assert response.status_code == 200


def test_authorize_post_success_with_state(client, test_user):
    """Test successful authorization with state parameter."""
    data = {
        'username': 'testuser',
        'password': 'testpass',
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
        'state': 'test_state_value'
    }
    response = client.post('/api/mcp/oauth/authorize', json=data)
    assert response.status_code == 200
    assert 'state=test_state_value' in response.json['redirect_url']


def test_authorize_post_invalid_credentials(client, test_user):
    """Test authorization with invalid credentials."""
    test_cases = [
        # Wrong password with email
        {
            'username': 'test@example.com',
            'password': 'wrongpass',
            'client_id': 'test_client',
            'redirect_uri': 'http://localhost:3000/callback',
        },
        # Wrong password with username
        {
            'username': 'testuser',
            'password': 'wrongpass',
            'client_id': 'test_client',
            'redirect_uri': 'http://localhost:3000/callback',
        },
        # Non-existent email
        {
            'username': 'nonexistent@example.com',
            'password': 'testpass',
            'client_id': 'test_client',
            'redirect_uri': 'http://localhost:3000/callback',
        },
        # Non-existent username
        {
            'username': 'nonexistent',
            'password': 'testpass',
            'client_id': 'test_client',
            'redirect_uri': 'http://localhost:3000/callback',
        }
    ]

    for data in test_cases:
        response = client.post('/api/mcp/oauth/authorize', json=data)
        assert response.status_code == 401


def test_authorize_post_missing_credentials(client):
    """Test authorization with missing credential fields."""
    # Missing username - should return 401
    response = client.post('/api/mcp/oauth/authorize', json={
        'password': 'testpass',
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
    })
    assert response.status_code == 400

    # Missing password - should return 401
    response = client.post('/api/mcp/oauth/authorize', json={
        'username': 'testuser',
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
    })
    assert response.status_code == 400

    # Empty username - should return 401
    response = client.post('/api/mcp/oauth/authorize', json={
        'username': '',
        'password': 'testpass',
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
    })
    assert response.status_code == 401

    # Empty password - should return 401
    response = client.post('/api/mcp/oauth/authorize', json={
        'username': 'testuser',
        'password': '',
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
    })
    assert response.status_code == 401


def test_authorize_post_missing_oauth_parameters(client, test_user):
    """Test authorization POST with missing OAuth parameters."""
    test_cases = [
        # Missing client_id
        {
            'username': 'testuser',
            'password': 'testpass',
            'redirect_uri': 'http://localhost:3000/callback',
        },
        # Missing redirect_uri
        {
            'username': 'testuser',
            'password': 'testpass',
            'client_id': 'test_client',
        }
    ]

    for data in test_cases:
        response = client.post('/api/mcp/oauth/authorize', json=data)
        assert response.status_code == 400


def test_authorize_post_empty_json(client):
    """Test authorization POST with empty JSON body."""
    response = client.post('/api/mcp/oauth/authorize', json={})
    # Empty JSON means missing required fields
    assert response.status_code == 400


def test_authorize_post_auth_code_storage(client, test_user):
    """Test that authorization code is properly stored with correct data."""
    data = {
        'username': 'testuser',
        'password': 'testpass',
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
        'state': 'test_state',
        'code_challenge': 'test_challenge',
        'code_challenge_method': 'S256'
    }
    response = client.post('/api/mcp/oauth/authorize', json=data)
    assert response.status_code == 200

    code = response.json['redirect_url'].split('code=')[1].split('&')[0]
    assert code in auth_codes

    stored = auth_codes[code]
    assert stored['user_id'] == test_user
    assert stored['client_id'] == 'test_client'
    assert stored['redirect_uri'] == 'http://localhost:3000/callback'
    assert stored['code_challenge'] == 'test_challenge'
    assert stored['code_challenge_method'] == 'S256'
    assert 'expires' in stored
    assert isinstance(stored['expires'], datetime)


# ============================================================================
# POST /api/mcp/oauth/token - Token Exchange
# ============================================================================

def test_token_post_success(client, test_user):
    """Test successful token exchange."""
    code = create_auth_code(test_user)

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:3000/callback'
    }
    response = client.post(
        '/api/mcp/oauth/token',
        data=data,
        content_type='application/x-www-form-urlencoded'
    )

    assert response.status_code == 200
    result = response.json
    assert 'access_token' in result
    assert result['token_type'] == 'Bearer'
    assert result['expires_in'] == 86400

    # Verify code was deleted
    assert code not in auth_codes

    # Verify token is valid
    token = result['access_token']
    with client.application.app_context():
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        token_obj = get_token(token_hash)
        assert token_obj is not None
        assert token_obj.user_id == test_user


def test_token_post_success_with_pkce_s256(client, test_user):
    """Test successful token exchange with PKCE S256."""
    code_verifier, code_challenge = generate_pkce_pair('S256')
    code = create_auth_code(test_user, code_challenge=code_challenge,
                            code_challenge_method='S256')

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:3000/callback',
        'code_verifier': code_verifier
    }
    response = client.post(
        '/api/mcp/oauth/token',
        data=data,
        content_type='application/x-www-form-urlencoded'
    )
    assert response.status_code == 200
    assert 'access_token' in response.json


def test_token_post_success_with_pkce_plain(client, test_user):
    """Test successful token exchange with PKCE plain."""
    code_verifier, code_challenge = generate_pkce_pair('plain')
    code = create_auth_code(test_user, code_challenge=code_challenge,
                            code_challenge_method='plain')

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:3000/callback',
        'code_verifier': code_verifier
    }
    response = client.post(
        '/api/mcp/oauth/token',
        data=data,
        content_type='application/x-www-form-urlencoded'
    )
    assert response.status_code == 200
    assert 'access_token' in response.json


def test_token_post_success_form_urlencoded(client, test_user):
    """Test token exchange with form-urlencoded content type."""
    code = create_auth_code(test_user)

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:3000/callback'
    }
    response = client.post('/api/mcp/oauth/token',
                           data=data,
                           content_type='application/x-www-form-urlencoded')
    assert response.status_code == 200
    assert 'access_token' in response.json


def test_token_post_invalid_grant_type(client):
    """Test token endpoint with invalid grant type."""
    test_cases = [
        {'grant_type': 'client_credentials', 'code': 'test',
            'redirect_uri': 'http://localhost:3000/callback'},
        {'grant_type': 'password', 'code': 'test',
            'redirect_uri': 'http://localhost:3000/callback'},
        {'grant_type': '', 'code': 'test',
            'redirect_uri': 'http://localhost:3000/callback'},
    ]

    for data in test_cases:
        response = client.post(
            '/api/mcp/oauth/token',
            data=data,
            content_type='application/x-www-form-urlencoded'
        )
        assert response.status_code == 400


def test_token_post_invalid_code(client):
    """Test token endpoint with invalid authorization code."""
    test_cases = [
        {'grant_type': 'authorization_code', 'code': 'invalid_code',
            'redirect_uri': 'http://localhost:3000/callback'},
        {'grant_type': 'authorization_code', 'code': '',
            'redirect_uri': 'http://localhost:3000/callback'},
    ]

    for data in test_cases:
        response = client.post(
            '/api/mcp/oauth/token',
            data=data,
            content_type='application/x-www-form-urlencoded'
        )
        assert response.status_code == 400

    # Missing code should fail schema validation
    response = client.post(
        '/api/mcp/oauth/token',
        data={'grant_type': 'authorization_code',
              'redirect_uri': 'http://localhost:3000/callback'},
        content_type='application/x-www-form-urlencoded'
    )
    assert response.status_code == 400


def test_token_post_expired_code(client, test_user):
    """Test token endpoint with expired authorization code."""
    code = create_expired_auth_code(test_user)

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:3000/callback'
    }
    response = client.post(
        '/api/mcp/oauth/token',
        data=data,
        content_type='application/x-www-form-urlencoded'
    )

    assert response.status_code == 400

    # Verify expired code was deleted
    assert code not in auth_codes


def test_token_post_code_replay_attack(client, test_user):
    """Test that authorization code can only be used once (replay attack prevention)."""
    code = create_auth_code(test_user)

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:3000/callback'
    }

    # First use - should succeed
    response1 = client.post(
        '/api/mcp/oauth/token',
        data=data,
        content_type='application/x-www-form-urlencoded'
    )
    assert response1.status_code == 200

    # Second use - should fail (replay attack)
    response2 = client.post(
        '/api/mcp/oauth/token',
        data=data,
        content_type='application/x-www-form-urlencoded'
    )
    assert response2.status_code == 400


def test_token_post_redirect_uri_mismatch(client, test_user):
    """Test token endpoint with redirect URI mismatch."""
    code = create_auth_code(
        test_user, redirect_uri='http://localhost:3000/callback')

    # Wrong redirect_uri
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://evil.com/callback'
    }
    response = client.post(
        '/api/mcp/oauth/token',
        data=data,
        content_type='application/x-www-form-urlencoded'
    )
    assert response.status_code == 400


def test_token_post_missing_code_verifier_with_challenge(client, test_user):
    """Test token endpoint missing code_verifier when code_challenge was provided."""
    code_verifier, code_challenge = generate_pkce_pair('S256')
    code = create_auth_code(test_user, code_challenge=code_challenge,
                            code_challenge_method='S256')

    # Missing code_verifier
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:3000/callback'
    }
    response = client.post(
        '/api/mcp/oauth/token',
        data=data,
        content_type='application/x-www-form-urlencoded'
    )
    assert response.status_code == 400


def test_token_post_invalid_code_verifier(client, test_user):
    """Test token endpoint with invalid code_verifier."""
    code_verifier, code_challenge = generate_pkce_pair('S256')
    code = create_auth_code(test_user, code_challenge=code_challenge,
                            code_challenge_method='S256')

    # Wrong code_verifier
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:3000/callback',
        'code_verifier': 'wrong_verifier'
    }
    response = client.post(
        '/api/mcp/oauth/token',
        data=data,
        content_type='application/x-www-form-urlencoded'
    )
    assert response.status_code == 400


def test_token_post_code_verifier_without_challenge(client, test_user):
    """Test that providing code_verifier without challenge should succeed."""
    code = create_auth_code(test_user, code_challenge=None)

    # Providing code_verifier when no challenge exists should be fine
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:3000/callback',
        'code_verifier': 'some_verifier'
    }
    response = client.post(
        '/api/mcp/oauth/token',
        data=data,
        content_type='application/x-www-form-urlencoded'
    )
    assert response.status_code == 200


def test_token_post_cross_user_attack(client, test_user, test_user2):
    """Test that User A's code cannot be used to get User B's token."""
    # Create code for user1
    code = create_auth_code(test_user)

    # Try to use it (should work for user1)
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:3000/callback'
    }
    response = client.post(
        '/api/mcp/oauth/token',
        data=data,
        content_type='application/x-www-form-urlencoded'
    )
    assert response.status_code == 200

    # Verify token belongs to user1, not user2
    token = response.json['access_token']
    with client.application.app_context():
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        token_obj = get_token(token_hash)
        assert token_obj.user_id == test_user
        assert token_obj.user_id != test_user2


def test_token_post_nonexistent_user(client):
    """Test token exchange when user doesn't exist."""
    # Create auth code with non-existent user_id
    code = secrets.token_urlsafe(32)
    auth_codes[code] = {
        'user_id': 99999,  # Non-existent user
        'expires': datetime.utcnow() + timedelta(minutes=10),
        'code_challenge': None,
        'code_challenge_method': 'plain',
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback'
    }

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:3000/callback'
    }
    response = client.post(
        '/api/mcp/oauth/token',
        data=data,
        content_type='application/x-www-form-urlencoded'
    )
    assert response.status_code == 400


# ============================================================================
# POST /api/mcp/oauth/register - Client Registration
# ============================================================================

def test_register_post_success(client):
    """Test successful client registration."""
    data = {
        'client_name': 'Test Client',
        'redirect_uris': ['http://localhost:3000/callback']
    }
    response = client.post('/api/mcp/oauth/register', json=data)

    assert response.status_code == 201
    result = response.json
    assert 'client_id' in result
    assert result['client_name'] == 'Test Client'
    assert result['redirect_uris'] == ['http://localhost:3000/callback']
    assert result['token_endpoint_auth_method'] == 'none'
    assert len(result['client_id']) > 0


def test_register_post_minimal_data(client):
    """Test client registration with minimal data."""
    data = {}
    response = client.post('/api/mcp/oauth/register', json=data)

    assert response.status_code == 201
    result = response.json
    assert 'client_id' in result
    assert result['client_name'] == 'MCP Client'  # Default value
    assert result['redirect_uris'] == []


def test_register_post_without_client_name(client):
    """Test client registration without client_name."""
    data = {
        'redirect_uris': ['http://localhost:3000/callback']
    }
    response = client.post('/api/mcp/oauth/register', json=data)
    assert response.status_code == 201
    assert response.json['client_name'] == 'MCP Client'


def test_register_post_without_redirect_uris(client):
    """Test client registration without redirect_uris."""
    data = {
        'client_name': 'Test Client'
    }
    response = client.post('/api/mcp/oauth/register', json=data)
    assert response.status_code == 201
    assert response.json['redirect_uris'] == []


def test_register_post_multiple_redirect_uris(client):
    """Test client registration with multiple redirect URIs."""
    data = {
        'client_name': 'Test Client',
        'redirect_uris': [
            'http://localhost:3000/callback',
            'http://localhost:3000/callback2',
            'https://example.com/callback'
        ]
    }
    response = client.post('/api/mcp/oauth/register', json=data)
    assert response.status_code == 201
    assert len(response.json['redirect_uris']) == 3


def test_register_post_empty_json(client):
    """Test client registration with empty JSON."""
    response = client.post('/api/mcp/oauth/register', json={})
    assert response.status_code == 201


# ============================================================================
# INTEGRATION TESTS - Full OAuth Flow
# ============================================================================

def test_full_oauth_flow(client, test_user):
    """Test complete OAuth flow: authorize GET -> authorize POST -> token POST."""
    # Step 1: GET /authorize
    params = {
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
        'response_type': 'code',
        'state': 'test_state'
    }
    response1 = client.get('/api/mcp/oauth/authorize', query_string=params)
    assert response1.status_code == 302

    # Step 2: POST /authorize (login)
    data = {
        'username': 'testuser',
        'password': 'testpass',
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
        'state': 'test_state'
    }
    response2 = client.post('/api/mcp/oauth/authorize', json=data)
    assert response2.status_code == 200

    # Extract code from redirect URL
    redirect_url = response2.json['redirect_url']
    code = redirect_url.split('code=')[1].split('&')[0]

    # Step 3: POST /token
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:3000/callback'
    }
    response3 = client.post(
        '/api/mcp/oauth/token',
        data=token_data,
        content_type='application/x-www-form-urlencoded'
    )
    assert response3.status_code == 200
    assert 'access_token' in response3.json

    # Verify token works
    token = response3.json['access_token']
    with client.application.app_context():
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        token_obj = get_token(token_hash)
        assert token_obj is not None
        assert token_obj.user_id == test_user


def test_full_oauth_flow_with_pkce(client, test_user):
    """Test complete OAuth flow with PKCE."""
    code_verifier, code_challenge = generate_pkce_pair('S256')

    # Step 1: GET /authorize with PKCE
    params = {
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
        'response_type': 'code',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    response1 = client.get('/api/mcp/oauth/authorize', query_string=params)
    assert response1.status_code == 302

    # Step 2: POST /authorize with PKCE
    data = {
        'username': 'testuser',
        'password': 'testpass',
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    response2 = client.post('/api/mcp/oauth/authorize', json=data)
    assert response2.status_code == 200

    code = response2.json['redirect_url'].split('code=')[1].split('&')[0]

    # Step 3: POST /token with code_verifier
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:3000/callback',
        'code_verifier': code_verifier
    }
    response3 = client.post(
        '/api/mcp/oauth/token',
        data=token_data,
        content_type='application/x-www-form-urlencoded'
    )
    assert response3.status_code == 200
    assert 'access_token' in response3.json


def test_multiple_concurrent_flows(client, test_user, test_user2):
    """Test multiple users authenticating simultaneously."""
    # User 1 flow
    data1 = {
        'username': 'testuser',
        'password': 'testpass',
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
    }
    response1 = client.post('/api/mcp/oauth/authorize', json=data1)
    code1 = response1.json['redirect_url'].split('code=')[1].split('&')[0]

    # User 2 flow
    data2 = {
        'username': 'testuser2',
        'password': 'testpass2',
        'client_id': 'test_client',
        'redirect_uri': 'http://localhost:3000/callback',
    }
    response2 = client.post('/api/mcp/oauth/authorize', json=data2)
    code2 = response2.json['redirect_url'].split('code=')[1].split('&')[0]

    # Verify codes are different
    assert code1 != code2

    # Exchange both codes
    token_data1 = {
        'grant_type': 'authorization_code',
        'code': code1,
        'redirect_uri': 'http://localhost:3000/callback'
    }
    token_data2 = {
        'grant_type': 'authorization_code',
        'code': code2,
        'redirect_uri': 'http://localhost:3000/callback'
    }

    response3 = client.post(
        '/api/mcp/oauth/token',
        data=token_data1,
        content_type='application/x-www-form-urlencoded'
    )
    response4 = client.post(
        '/api/mcp/oauth/token',
        data=token_data2,
        content_type='application/x-www-form-urlencoded'
    )

    assert response3.status_code == 200
    assert response4.status_code == 200

    # Verify tokens belong to correct users
    token1 = response3.json['access_token']
    token2 = response4.json['access_token']

    with client.application.app_context():
        token_hash1 = hashlib.sha256(token1.encode()).hexdigest()
        token_hash2 = hashlib.sha256(token2.encode()).hexdigest()
        token_obj1 = get_token(token_hash1)
        token_obj2 = get_token(token_hash2)
        assert token_obj1.user_id == test_user
        assert token_obj2.user_id == test_user2


# ============================================================================
# HELPER FUNCTION TESTS
# ============================================================================

def test_exchange_authorization_code_helper_success(client, test_user):
    """Test exchange_authorization_code_for_session_token helper function."""
    code = create_auth_code(test_user)

    with client.application.app_context():
        token, expires_in = exchange_authorization_code_for_session_token(
            code=code,
            code_verifier=None,
            redirect_uri='http://localhost:3000/callback'
        )

        assert isinstance(token, str)
        assert expires_in == 86400
        assert code not in auth_codes  # Should be deleted


def test_exchange_authorization_code_helper_with_pkce(client, test_user):
    """Test helper function with PKCE."""
    code_verifier, code_challenge = generate_pkce_pair('S256')
    code = create_auth_code(test_user, code_challenge=code_challenge,
                            code_challenge_method='S256')

    with client.application.app_context():
        token, expires_in = exchange_authorization_code_for_session_token(
            code=code,
            code_verifier=code_verifier,
            redirect_uri='http://localhost:3000/callback'
        )

        assert isinstance(token, str)
        assert expires_in == 86400


def test_exchange_authorization_code_helper_invalid_code(client):
    """Test helper function with invalid code."""
    with client.application.app_context():
        with pytest.raises(ValueError, match='invalid_grant'):
            exchange_authorization_code_for_session_token(
                code='invalid_code',
                code_verifier=None,
                redirect_uri='http://localhost:3000/callback'
            )


def test_exchange_authorization_code_helper_expired_code(client, test_user):
    """Test helper function with expired code."""
    code = create_expired_auth_code(test_user)

    with client.application.app_context():
        with pytest.raises(ValueError, match='invalid_grant'):
            exchange_authorization_code_for_session_token(
                code=code,
                code_verifier=None,
                redirect_uri='http://localhost:3000/callback'
            )


def test_exchange_authorization_code_helper_redirect_uri_mismatch(client, test_user):
    """Test helper function with redirect URI mismatch."""
    code = create_auth_code(
        test_user, redirect_uri='http://localhost:3000/callback')

    with client.application.app_context():
        with pytest.raises(ValueError, match='invalid_grant'):
            exchange_authorization_code_for_session_token(
                code=code,
                code_verifier=None,
                redirect_uri='http://evil.com/callback'
            )


def test_exchange_authorization_code_helper_missing_verifier(client, test_user):
    """Test helper function missing code_verifier when required."""
    code_verifier, code_challenge = generate_pkce_pair('S256')
    code = create_auth_code(test_user, code_challenge=code_challenge,
                            code_challenge_method='S256')

    with client.application.app_context():
        with pytest.raises(ValueError, match='invalid_request'):
            exchange_authorization_code_for_session_token(
                code=code,
                code_verifier=None,  # Missing when required
                redirect_uri='http://localhost:3000/callback'
            )


def test_exchange_authorization_code_helper_invalid_verifier(client, test_user):
    """Test helper function with invalid code_verifier."""
    code_verifier, code_challenge = generate_pkce_pair('S256')
    code = create_auth_code(test_user, code_challenge=code_challenge,
                            code_challenge_method='S256')

    with client.application.app_context():
        with pytest.raises(ValueError, match='invalid_grant'):
            exchange_authorization_code_for_session_token(
                code=code,
                code_verifier='wrong_verifier',
                redirect_uri='http://localhost:3000/callback'
            )
