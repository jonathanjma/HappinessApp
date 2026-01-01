"""
Discord linking endpoints for the Happiness App MCP OAuth flow.

Goal: allow a Discord bot to link a Discord user to a Happiness App user *without*
running a web server on the bot and without any copy/paste codes.

High-level flow:
1) Bot calls POST /api/discord/link/start (authenticated with a shared secret).
2) Backend returns a link URL to /api/mcp/oauth/authorize with redirect_uri pointing to
   /api/discord/link/callback and PKCE parameters.
3) User clicks link, logs in, backend receives OAuth code at /callback and exchanges it
   for a session token.
4) Bot polls GET /api/discord/link/poll (authenticated) to fetch the token once.

Storage:
- In-memory link sessions (dev-friendly). For production, use Redis or DB.
"""

from __future__ import annotations

import base64
import hashlib
import secrets
import time
import urllib.parse
from typing import Any, Dict, Optional

from flask import Blueprint, current_app, jsonify, request
from itsdangerous import BadSignature, BadTimeSignature, URLSafeTimedSerializer

discord_link = Blueprint("discord_link", __name__)


# In-memory link session store.
# Keyed by link_id. Values are LinkSession dicts.
_link_sessions: Dict[str, Dict[str, Any]] = {}


def _now_s() -> int:
    return int(time.time())


def _cleanup_expired_sessions() -> None:
    now = _now_s()
    expired_keys = [k for k, v in _link_sessions.items() if int(
        v.get("expires_at", 0)) <= now]
    for k in expired_keys:
        _link_sessions.pop(k, None)


def _b64url_no_pad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _pkce_verifier() -> str:
    # RFC 7636: code_verifier length 43..128 characters.
    return secrets.token_urlsafe(64)[:128]


def _pkce_challenge_s256(verifier: str) -> str:
    return _b64url_no_pad(hashlib.sha256(verifier.encode("utf-8")).digest())


def _serializer() -> URLSafeTimedSerializer:
    secret = current_app.config.get("SECRET_KEY")
    if not secret:
        # SECRET_KEY is required for signing state.
        raise RuntimeError(
            "SECRET_KEY must be configured to use Discord linking.")
    return URLSafeTimedSerializer(secret_key=secret, salt="discord-link-state-v1")


def _oauth_base_url() -> str:
    return str(current_app.config.get("OAUTH_BASE_URL", "")).rstrip("/")


def _require_bot_secret() -> Optional[Any]:
    """
    Enforce bot-to-backend authentication for link start/poll.

    If DISCORD_BOT_LINK_SECRET is not set, allow requests (dev convenience).
    """
    expected = current_app.config.get("DISCORD_BOT_LINK_SECRET")
    if not expected:
        return None
    provided = request.headers.get("X-Bot-Secret", "")
    if not secrets.compare_digest(str(expected), str(provided)):
        return jsonify({"error": "unauthorized"}), 401
    return None


@discord_link.route("/start", methods=["POST"])
def start_link():
    """
    Bot calls this endpoint to start a link session and get a browser URL.
    """
    _cleanup_expired_sessions()

    auth_resp = _require_bot_secret()
    if auth_resp is not None:
        return auth_resp

    body = request.get_json(silent=True) or {}
    discord_user_id = body.get("discord_user_id")
    if not discord_user_id:
        return jsonify({"error": "discord_user_id_required"}), 400

    base_url = _oauth_base_url()
    if not base_url:
        return jsonify({"error": "OAUTH_BASE_URL_not_configured"}), 500

    # Create link session and PKCE params
    link_id = secrets.token_urlsafe(24)
    code_verifier = _pkce_verifier()
    code_challenge = _pkce_challenge_s256(code_verifier)

    # OAuth client_id: authorize endpoint doesn't validate it (simple implementation),
    # so we can generate an ephemeral one.
    client_id = secrets.token_urlsafe(16)

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
    _link_sessions[link_id] = {
        "discord_user_id": str(discord_user_id),
        "code_verifier": code_verifier,
        "expires_at": _now_s() + 600,
        "status": "pending",
    }

    return jsonify(
        {
            "link_id": link_id,
            "link_url": authorize_url,
            "expires_in": 600,
        }
    )


@discord_link.route("/callback", methods=["GET"])
def link_callback():
    """
    Browser lands here after /api/mcp/oauth/authorize redirects with ?code=...&state=...
    """
    _cleanup_expired_sessions()

    code = request.args.get("code", "")
    state = request.args.get("state", "")
    if not code or not state:
        return "Missing code/state.", 400

    try:
        payload = _serializer().loads(state, max_age=600)
    except (BadSignature, BadTimeSignature):
        return "Invalid or expired state.", 400

    link_id = str(payload.get("link_id") or "")
    if not link_id:
        return "Invalid state payload.", 400

    session = _link_sessions.get(link_id)
    if not session:
        return "Link session expired. Please restart linking from Discord.", 400

    # Optional: ensure the same discord_user_id we created matches
    if str(payload.get("discord_user_id")) != str(session.get("discord_user_id")):
        return "Link session mismatch.", 400

    if session.get("status") != "pending":
        return "Link session already completed. You can return to Discord.", 200

    try:
        from api.routes.mcp_oauth import exchange_authorization_code_for_session_token

        access_token, expires_in = exchange_authorization_code_for_session_token(
            code=code,
            code_verifier=str(session.get("code_verifier") or ""),
        )
    except Exception:
        # Keep message generic to avoid leaking info
        return "Failed to complete linking. Please try again.", 400

    session["status"] = "complete"
    session["access_token"] = access_token
    session["token_expires_at"] = _now_s() + int(expires_in)
    session["expires_at"] = _now_s() + 600  # keep around briefly for bot poll

    return (
        "<html><body><h2>✅ Linked successfully</h2>"
        "<p>You can now return to Discord. This page can be closed.</p>"
        "</body></html>",
        200,
        {"Content-Type": "text/html; charset=utf-8"},
    )


@discord_link.route("/poll", methods=["GET"])
def poll_link():
    """
    Bot polls for completion; returns token once and deletes the session.
    """
    _cleanup_expired_sessions()

    auth_resp = _require_bot_secret()
    if auth_resp is not None:
        return auth_resp

    link_id = request.args.get("link_id", "")
    if not link_id:
        return jsonify({"error": "link_id_required"}), 400

    session = _link_sessions.get(link_id)
    if not session:
        return jsonify({"status": "expired"}), 404

    status = session.get("status")
    if status != "complete":
        return jsonify({"status": "pending"}), 200

    access_token = session.get("access_token") or ""
    token_expires_at = int(session.get("token_expires_at") or 0)
    expires_in = max(0, token_expires_at - _now_s())

    # One-time delivery: remove from memory after returning.
    _link_sessions.pop(link_id, None)

    return jsonify(
        {
            "status": "complete",
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": expires_in,
        }
    )
