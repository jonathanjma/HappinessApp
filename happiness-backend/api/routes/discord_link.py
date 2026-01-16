"""
Discord linking endpoints for the Happiness App MCP OAuth flow.

High-level flow:
1) Bot calls POST /api/discord/link/start (authenticated with a shared secret).
2) Backend returns a link URL to /api/mcp/oauth/authorize with redirect_uri pointing to
   /api/discord/link/callback and PKCE parameters.
3) User clicks link, logs in, backend receives OAuth code at /callback and exchanges it
   for a session token.
4) Bot polls GET /api/discord/link/poll (authenticated) to fetch the token once.
"""

import base64
import hashlib
import secrets
import time
import urllib.parse
from typing import Any, Dict

from flask import Blueprint, current_app, redirect
from apifairy import arguments, body, response, other_responses
from api.models.schema import (
    StartLinkSchema,
    StartLinkResponseSchema,
    LinkCallbackSchema,
    PollLinkSchema,
    PollLinkResponseSchema,
    BotSecretSchema,
)
from api.routes.mcp_oauth import exchange_authorization_code_for_session_token
from api.util.errors import failure_response
from itsdangerous import BadSignature, BadTimeSignature, URLSafeTimedSerializer

discord_link = Blueprint("DiscordLink", __name__)


# In-memory link session store.
# Keyed by link_id. Values are LinkSession dicts.
link_sessions: Dict[str, Dict[str, Any]] = {}


def _cleanup_expired_sessions() -> None:
    expired_keys = [k for k, v in link_sessions.items() if int(
        v.get("expires_at", 0)) <= int(time.time())]
    for k in expired_keys:
        link_sessions.pop(k, None)


def _serializer() -> URLSafeTimedSerializer:
    secret = current_app.config.get("SECRET_KEY")
    if not secret:
        # SECRET_KEY is required for signing state.
        raise RuntimeError(
            "SECRET_KEY must be configured to use Discord linking.")
    return URLSafeTimedSerializer(secret_key=secret, salt="discord-link-state-v1")


@discord_link.post("/start")
@body(StartLinkSchema)
@arguments(BotSecretSchema, location='headers')
@response(StartLinkResponseSchema)
def start_link(link_data, headers):
    """
    Start Discord Link Session
    Creates a new Discord linking session and returns a URL for the user to authorize.

    This endpoint is called by the Discord bot to initiate the OAuth linking flow.
    It returns a temporary URL that the Discord user can visit to complete the authorization. 
    The link session expires after 10 minutes.
    """
    _cleanup_expired_sessions()

    discord_user_id = link_data["discord_user_id"]

    # Create link session and PKCE params
    link_id = secrets.token_urlsafe(24)
    # RFC 7636: code_verifier length 43..128 characters.
    code_verifier = secrets.token_urlsafe(64)[:128]
    verifier_hash = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(
        verifier_hash).rstrip(b"=").decode("ascii")

    # OAuth client_id: authorize endpoint doesn't validate it (simple implementation),
    # so we can generate an ephemeral one.
    client_id = secrets.token_urlsafe(16)

    base_url = current_app.config['OAUTH_BASE_URL']
    callback_url = f"{base_url}/api/discord/link/callback"

    state = _serializer().dumps(
        {"link_id": link_id, "discord_user_id": str(discord_user_id)})

    authorize_params = {
        "client_id": client_id,
        "redirect_uri": callback_url,
        "response_type": "code",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    authorize_url = f"{base_url}/api/mcp/oauth/authorize?{urllib.parse.urlencode(authorize_params)}"

    # Store pending session for 10 minutes
    link_sessions[link_id] = {
        "discord_user_id": str(discord_user_id),
        "code_verifier": code_verifier,
        "expires_at": int(time.time()) + 600,
        "status": "pending",
    }

    return {
        "link_id": link_id,
        "link_url": authorize_url,
        "expires_in": 600,
    }


@discord_link.get("/callback")
@arguments(LinkCallbackSchema)
@other_responses({400: "Invalid state, expired session, or linking failed"})
def link_callback(callback_params):
    """
    Discord Link OAuth Callback
    Handles the OAuth callback after user authorization and completes the linking process.

    This endpoint is called by the browser after the user completes OAuth authorization.
    It validates the authorization code, exchanges it for a session token, 
    stores it in the link session, and redirects the user to the frontend.
    The bot can then poll /poll to retrieve the access token.

    Prerequisites: User must have completed OAuth authorization via the link_url from POST /start
    """
    _cleanup_expired_sessions()

    code = callback_params["code"]
    state = callback_params["state"]

    try:
        payload = _serializer().loads(state, max_age=600)
    except (BadSignature, BadTimeSignature):
        return failure_response("Invalid or expired state.", 400)

    link_id = payload.get("link_id")
    if not link_id:
        return failure_response("Invalid state payload.", 400)

    session = link_sessions.get(link_id)
    if not session:
        return failure_response("Link session expired.", 400)

    # Ensure the same discord_user_id we created matches
    if str(payload.get("discord_user_id")) != str(session.get("discord_user_id")):
        return failure_response("Link session mismatch.", 400)

    if session.get("status") != "pending":
        return failure_response("Link session already completed.", 200)

    try:
        # Get the callback URL that was used in the authorization request
        callback_url = f"{current_app.config['OAUTH_BASE_URL']}/api/discord/link/callback"

        access_token, expires_in = exchange_authorization_code_for_session_token(
            code=code,
            code_verifier=str(session.get("code_verifier") or ""),
            redirect_uri=callback_url,  # Pass redirect_uri for validation
        )
    except Exception:
        # Keep message generic to avoid leaking info
        return failure_response("Failed to complete linking. Please try again.", 400)

    session["status"] = "complete"
    session["access_token"] = access_token
    session["token_expires_at"] = int(time.time()) + int(expires_in)
    # keep around briefly for bot poll
    session["expires_at"] = int(time.time()) + 600

    # Redirect to frontend
    return redirect(current_app.config['FRONTEND_URL'])


@discord_link.get("/poll")
@arguments(PollLinkSchema)
@arguments(BotSecretSchema, location='headers')
@response(PollLinkResponseSchema)
@other_responses({400: "Link session expired"})
def poll_link(poll_params, headers):
    """
    Poll Discord Link Status
    Checks the status of a Discord linking session and returns the access token when complete.

    This endpoint is polled by the Discord bot to check if the user has completed the
    OAuth authorization. It returns "pending" if authorization is not yet complete,
    "expired" if the session has expired, or "complete" with the access token if
    authorization succeeded.
    """
    _cleanup_expired_sessions()

    link_id = poll_params["link_id"]
    session = link_sessions.get(link_id)
    if not session:
        return failure_response("Link session expired.", 400)

    if session.get("status") != "complete":
        return {"status": "pending"}

    access_token = session.get("access_token")
    token_expires_at = session.get("token_expires_at")
    expires_in = max(0, token_expires_at - int(time.time()))

    # One-time delivery: remove from memory after returning.
    link_sessions.pop(link_id, None)

    return {
        "status": "complete",
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": expires_in,
    }
