"""
OAuth endpoints for MCP server authentication.
Maps MCP OAuth flow to existing session token system.
"""
from flask import Blueprint, jsonify, request, redirect, current_app
from api.app import db
import hashlib
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlencode

mcp_oauth = Blueprint('mcp_oauth', __name__)

# In-memory store for authorization codes (for production, use Redis or database)
# Format: {code: {'user_id': int, 'expires': datetime, 'code_challenge': str, 'code_challenge_method': str, 'redirect_uri': str, 'client_id': str}}
auth_codes = {}


def get_oauth_base_url():
    """Get OAuth base URL from config."""
    return current_app.config.get('OAUTH_BASE_URL', 'http://localhost:5001')


def get_frontend_url():
    """Get frontend URL from config."""
    return current_app.config.get('FRONTEND_URL', 'http://localhost:5173')


def exchange_authorization_code_for_session_token(
    *,
    code: str,
    code_verifier: str | None,
    redirect_uri: str | None = None,
) -> tuple[str, int]:
    """
    Shared helper to exchange an OAuth authorization code for a session token.

    Used by:
    - /api/mcp/oauth/token (standard OAuth token endpoint)
    - /api/discord/link/callback (Discord bot linking flow)
    """
    # Validate authorization code
    if not code or code not in auth_codes:
        raise ValueError("invalid_grant")

    auth_data = auth_codes[code]

    # Check expiration
    if datetime.utcnow() > auth_data['expires']:
        del auth_codes[code]
        raise ValueError("invalid_grant: authorization_code_expired")

    # SECURITY: Verify redirect_uri matches (if provided)
    if redirect_uri and auth_data.get('redirect_uri') != redirect_uri:
        raise ValueError("invalid_grant: redirect_uri_mismatch")

    # Verify PKCE if code_challenge was provided
    if auth_data.get('code_challenge'):
        if not code_verifier:
            raise ValueError("invalid_request: code_verifier_required")

        # Verify code challenge
        if auth_data['code_challenge_method'] == 'S256':
            import base64
            computed_challenge = base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode()).digest()
            ).rstrip(b'=').decode()
        else:
            computed_challenge = code_verifier

        if computed_challenge != auth_data['code_challenge']:
            raise ValueError("invalid_grant: invalid_code_verifier")

    # Get user and create session token (reuse existing token system!)
    from api.dao.users_dao import get_user_by_id
    user = get_user_by_id(auth_data['user_id'])

    if not user:
        raise ValueError("invalid_grant")

    # Create token using existing system
    token_obj, session_token = user.create_token()
    db.session.add(token_obj)
    db.session.commit()

    # Clean up authorization code
    del auth_codes[code]

    return session_token, 86400  # 24 hours


def oauth_authorization_server():
    """
    OAuth 2.1 Authorization Server Metadata.
    Tells MCP clients where to find auth endpoints.

    NOTE: This is intended to be registered at the *root* path:
    `/.well-known/oauth-authorization-server` (see `api/app.py`).
    """
    base_url = get_oauth_base_url()
    return jsonify({
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/api/mcp/oauth/authorize",
        "token_endpoint": f"{base_url}/api/mcp/oauth/token",
        "registration_endpoint": f"{base_url}/api/mcp/oauth/register",
        "grant_types_supported": ["authorization_code"],
        "response_types_supported": ["code"],
        "code_challenge_methods_supported": ["S256", "plain"],
        "token_endpoint_auth_methods_supported": ["none"]
    })


def oauth_protected_resource():
    """
    OAuth 2.1 Protected Resource Metadata.
    Tells MCP clients about the protected resource.

    NOTE: This is intended to be registered at the *root* path:
    `/.well-known/oauth-protected-resource` (see `api/app.py`).
    """
    base_url = get_oauth_base_url()
    return jsonify({
        "resource": base_url,
        "authorization_servers": [base_url]
    })


@mcp_oauth.route('/authorize', methods=['GET'])
def authorize():
    """
    OAuth authorization endpoint.
    Redirects to frontend React component for login.

    This is where users authorize MCP access to their data.
    """
    # Get OAuth parameters
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    response_type = request.args.get('response_type')
    state = request.args.get('state')
    code_challenge = request.args.get('code_challenge')
    code_challenge_method = request.args.get('code_challenge_method', 'plain')

    # Validate parameters
    if response_type != 'code':
        return jsonify({"error": "unsupported_response_type"}), 400

    if not client_id or not redirect_uri:
        return jsonify({"error": "invalid_request"}), 400

    # Build frontend URL with OAuth parameters
    frontend_url = get_frontend_url()
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': response_type,
    }
    if state:
        params['state'] = state
    if code_challenge:
        params['code_challenge'] = code_challenge
    if code_challenge_method:
        params['code_challenge_method'] = code_challenge_method

    frontend_oauth_url = f"{frontend_url}/oauth/authorize?{urlencode(params)}"

    return redirect(frontend_oauth_url)


@mcp_oauth.route('/authorize', methods=['POST'])
def authorize_post():
    """
    Handle login form submission and generate authorization code.
    """
    from api.dao.users_dao import get_user_by_username, get_user_by_email

    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    client_id = data.get('client_id')
    redirect_uri = data.get('redirect_uri')
    state = data.get('state')
    code_challenge = data.get('code_challenge')
    code_challenge_method = data.get('code_challenge_method', 'plain')

    # Validate required fields
    if not username or not password:
        return jsonify({"error": "invalid_credentials"}), 401

    # Verify user credentials (reuse existing verification logic)
    user = get_user_by_email(username)
    if not user or not user.verify_password(password):
        user = get_user_by_username(username)
        if not user or not user.verify_password(password):
            return jsonify({"error": "invalid_credentials"}), 401

    # Generate authorization code
    auth_code = secrets.token_urlsafe(32)

    # Store authorization code with user info (including redirect_uri for validation)
    auth_codes[auth_code] = {
        'user_id': user.id,
        'expires': datetime.utcnow() + timedelta(minutes=10),
        'code_challenge': code_challenge,
        'code_challenge_method': code_challenge_method,
        'client_id': client_id,
        # SECURITY: Store redirect_uri to validate in token endpoint
        'redirect_uri': redirect_uri
    }

    # Build redirect URL with authorization code
    redirect_url = f"{redirect_uri}?code={auth_code}"
    if state:
        redirect_url += f"&state={state}"

    # Return JSON for React frontend
    return jsonify({"redirect_url": redirect_url})


@mcp_oauth.route('/token', methods=['POST'])
def token():
    """
    OAuth token endpoint.
    Exchanges authorization code for access token (session token).

    Maps to your existing session token system!
    """
    # Parse request
    content_type = request.headers.get('Content-Type', '')

    if 'application/json' in content_type:
        data = request.json or {}
    else:
        data = request.form.to_dict()

    grant_type = data.get('grant_type')
    code = data.get('code')
    redirect_uri = data.get('redirect_uri')
    code_verifier = data.get('code_verifier')
    client_id = data.get('client_id')

    # Validate grant type
    if grant_type != 'authorization_code':
        return jsonify({"error": "unsupported_grant_type"}), 400

    # SECURITY: Validate redirect_uri matches the one used in authorization request
    if code and code in auth_codes:
        stored_redirect_uri = auth_codes[code].get('redirect_uri')
        if redirect_uri and redirect_uri != stored_redirect_uri:
            return jsonify({"error": "invalid_grant", "error_description": "redirect_uri mismatch"}), 400

    try:
        session_token, expires_in = exchange_authorization_code_for_session_token(
            code=code,
            code_verifier=code_verifier,
            redirect_uri=redirect_uri,  # Pass for validation
        )
    except ValueError as e:
        # Normalize to OAuth-ish errors; keep descriptions minimal.
        msg = str(e)
        if msg.startswith("invalid_request"):
            return jsonify({"error": "invalid_request"}), 400
        return jsonify({"error": "invalid_grant"}), 400

    # Return access token (this is your session token!)
    return jsonify({
        "access_token": session_token,
        "token_type": "Bearer",
        "expires_in": expires_in
    })


@mcp_oauth.route('/register', methods=['POST'])
def register_client():
    """
    Dynamic client registration endpoint.
    For simplicity, we accept all clients without storing registration.
    """
    data = request.json or {}
    client_name = data.get('client_name', 'MCP Client')
    redirect_uris = data.get('redirect_uris', [])

    # Generate a client_id (for this simple implementation, we don't validate it)
    client_id = secrets.token_urlsafe(16)

    return jsonify({
        "client_id": client_id,
        "client_name": client_name,
        "redirect_uris": redirect_uris,
        "token_endpoint_auth_method": "none"
    }), 201
