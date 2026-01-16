"""
OAuth endpoints for MCP server authentication.
Maps MCP OAuth flow to existing session token system.
"""
from flask import Blueprint, redirect, current_app
from apifairy import arguments, body, response, other_responses
from api.app import db
from api.models.schema import (
    AuthorizationRequestSchema,
    AuthorizationPostSchema,
    AuthorizationResponseSchema,
    TokenRequestSchema,
    TokenResponseSchema,
    ClientRegistrationSchema,
    ClientRegistrationResponseSchema,
    OAuthAuthorizationServerSchema,
    OAuthProtectedResourceSchema,
)
from api.util.errors import failure_response
import hashlib
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlencode
from marshmallow import INCLUDE

mcp_oauth = Blueprint('OAuth', __name__)

# In-memory store for authorization codes (for production, use Redis or database)
# Format: {code: {'user_id': int, 'expires': datetime, 'code_challenge': str, 'code_challenge_method': str, 'redirect_uri': str, 'client_id': str}}
auth_codes = {}


def exchange_authorization_code_for_session_token(
    *,
    code: str,
    code_verifier: str | None,
    redirect_uri: str | None = None,
) -> tuple[str, int]:
    """
    Exchange Authorization Code for Session Token
    Internal helper function that validates an OAuth authorization code and exchanges it for a session token.

    Prerequisites: Authorization code must exist in auth_codes store and not be expired.

    Required Arguments:
    - code: The authorization code to exchange
    - code_verifier: PKCE code verifier (required if code_challenge was used during authorization)
    - redirect_uri: Redirect URI to validate against stored value (optional)

    Returns: Tuple of (session_token, expires_in_seconds)
    Raises: ValueError with OAuth error codes if validation fails.
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


@response(OAuthAuthorizationServerSchema)
def oauth_authorization_server():
    """
    OAuth Auth Server Metadata
    Returns OAuth 2.1 authorization server discovery metadata for MCP clients.

    This endpoint provides clients with the locations of all OAuth endpoints including
    authorization, token, and registration endpoints, as well as supported grant types
    and code challenge methods.
    """
    base_url = current_app.config['OAUTH_BASE_URL']
    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/api/mcp/oauth/authorize",
        "token_endpoint": f"{base_url}/api/mcp/oauth/token",
        "registration_endpoint": f"{base_url}/api/mcp/oauth/register",
        "grant_types_supported": ["authorization_code"],
        "response_types_supported": ["code"],
        "code_challenge_methods_supported": ["S256", "plain"],
        "token_endpoint_auth_methods_supported": ["none"]
    }


@response(OAuthProtectedResourceSchema)
def oauth_protected_resource():
    """
    OAuth Protected Resource Metadata
    Returns OAuth 2.1 protected resource metadata for MCP clients.

    This endpoint identifies the protected resource and lists the authorization servers
    that can issue access tokens for accessing this resource.
    """
    base_url = current_app.config['OAUTH_BASE_URL']
    return {
        "resource": base_url,
        "authorization_servers": [base_url]
    }


@mcp_oauth.get('/authorize')
@arguments(AuthorizationRequestSchema)
@other_responses({400: "Invalid request or unsupported response type"})
def authorize(auth_params):
    """
    OAuth Authorization Request
    Initiates the OAuth 2.1 authorization flow by redirecting users to the frontend login page.

    This is the first step in the OAuth flow. Users are redirected to the frontend where they
    can log in and authorize MCP client access to their data. After successful authorization,
    the frontend will POST to /authorize to complete the flow.

    Required Arguments:
    - client_id: The OAuth client identifier
    - redirect_uri: The URI to redirect to after authorization (must match registration)
    - response_type: Must be "code" for authorization code flow
    - state: Optional state parameter for CSRF protection
    - code_challenge: Optional PKCE code challenge
    - code_challenge_method: PKCE method ("S256" or "plain"), defaults to "plain"
    """
    # Get OAuth parameters from validated schema
    client_id = auth_params['client_id']
    redirect_uri = auth_params['redirect_uri']
    response_type = auth_params['response_type']
    state = auth_params.get('state')
    code_challenge = auth_params.get('code_challenge')
    code_challenge_method = auth_params['code_challenge_method']

    # Validate parameters
    if response_type != 'code':
        return failure_response("Unsupported response type", 400)

    # Build frontend URL with OAuth parameters
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

    frontend_oauth_url = f"{current_app.config['FRONTEND_URL']}/oauth/authorize?{urlencode(params)}"

    return redirect(frontend_oauth_url)


@mcp_oauth.post('/authorize')
@body(AuthorizationPostSchema)
@response(AuthorizationResponseSchema)
@other_responses({401: "Invalid credentials"})
def authorize_post(auth_data):
    """
    Complete OAuth Authorization
    Processes user login credentials and generates an authorization code for the OAuth flow.

    After the user logs in via the frontend, this endpoint validates their credentials,
    creates a temporary authorization code, and returns a redirect URL containing the code.
    The authorization code expires after 10 minutes and can only be used once.

    Prerequisites: User must have initiated authorization via GET /authorize
    Required Arguments:
    - username: User's email or username
    - password: User's password
    - client_id: The OAuth client identifier (must match GET /authorize request)
    - redirect_uri: The redirect URI (must match GET /authorize request)
    - state: Optional state parameter to pass through to redirect
    - code_challenge: Optional PKCE code challenge
    - code_challenge_method: PKCE method ("S256" or "plain"), defaults to "plain"
    """
    from api.dao.users_dao import get_user_by_username, get_user_by_email

    username = auth_data['username']
    password = auth_data['password']
    client_id = auth_data['client_id']
    redirect_uri = auth_data['redirect_uri']
    state = auth_data.get('state')
    code_challenge = auth_data.get('code_challenge')
    code_challenge_method = auth_data['code_challenge_method']

    # Verify user credentials (reuse existing verification logic)
    user = get_user_by_email(username)
    if not user or not user.verify_password(password):
        user = get_user_by_username(username)
        if not user or not user.verify_password(password):
            return failure_response("Invalid credentials", 401)

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
    return {"redirect_url": redirect_url}


@mcp_oauth.post('/token')
@body(TokenRequestSchema(unknown=INCLUDE), location='form')
@response(TokenResponseSchema)
@other_responses({400: "Invalid request, unsupported grant type, or invalid grant"})
def token(token_data):
    """
    Exchange Auth Code for Token
    Exchanges a valid OAuth authorization code for an access token (session token).

    This endpoint completes the OAuth 2.1 authorization code flow. The authorization code
    obtained from the /authorize endpoint is exchanged for a session token that can be
    used to authenticate API requests. The token expires after 24 hours.

    Prerequisites: Must have a valid authorization code from POST /authorize
    Required Arguments:
    - grant_type: Must be "authorization_code"
    - code: The authorization code from POST /authorize
    - redirect_uri: Must match the redirect_uri used in authorization request
    - code_verifier: Required if PKCE code_challenge was used during authorization
    - client_id: Optional client identifier
    """
    grant_type = token_data['grant_type']
    code = token_data['code']
    redirect_uri = token_data['redirect_uri']
    code_verifier = token_data.get('code_verifier')
    client_id = token_data.get('client_id')

    # Validate grant type
    if grant_type != 'authorization_code':
        return failure_response("Unsupported grant type", 400)

    # SECURITY: Validate redirect_uri matches the one used in authorization request
    if code and code in auth_codes:
        stored_redirect_uri = auth_codes[code].get('redirect_uri')
        if redirect_uri and redirect_uri != stored_redirect_uri:
            return failure_response("Redirect URI mismatch", 400)

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
            return failure_response("Invalid request", 400)
        return failure_response("Invalid grant", 400)

    # Return access token (this is your session token!)
    return {
        "access_token": session_token,
        "token_type": "Bearer",
        "expires_in": expires_in
    }


@mcp_oauth.post('/register')
@body(ClientRegistrationSchema(unknown=INCLUDE))
@response(ClientRegistrationResponseSchema, status_code=201)
def register_client(registration_data):
    """
    OAuth Client Registration
    Dynamically registers a new OAuth client and returns client credentials.

    This endpoint allows MCP clients to register themselves without pre-configuration.
    A new client_id is generated and returned.

    Required Arguments:
    - client_name: Optional client name, defaults to "MCP Client"
    - redirect_uris: Optional list of allowed redirect URIs, defaults to empty list
    """
    client_name = registration_data.get('client_name', 'MCP Client')
    redirect_uris = registration_data.get('redirect_uris', [])

    # Generate a client_id (for this simple implementation, we don't validate it)
    client_id = secrets.token_urlsafe(16)

    return {
        "client_id": client_id,
        "client_name": client_name,
        "redirect_uris": redirect_uris,
        "token_endpoint_auth_method": "none"
    }
