"""
MCP (Model Context Protocol) server for Happiness App.
Exposes read-only tools for LLMs to query user happiness data.

High-level flow:
1. Claude (MCP client) tries to access /mcp
   ↓
2. MCP server returns 401 with WWW-Authenticate header
   ↓
3. Claude discovers OAuth endpoints via /.well-known/
   ↓
4. Claude redirects user to /api/mcp/oauth/authorize
   ↓
5. User enters username/password in login form
   ↓
6. Server validates credentials (using your existing system!)
   ↓
7. Server generates authorization code
   ↓
8. Claude exchanges code for access token at /api/mcp/oauth/token
   ↓
9. Server creates session token (using your existing Token.create_token()!)
   ↓
10. Claude uses this session token as Bearer token for all MCP requests
    ↓
11. MCP validates token (using your existing verify_token logic!)
    ↓
12. MCP extracts user_id and queries their data
"""
from datetime import datetime
from typing import Optional
from statistics import mean
import hashlib
from contextvars import ContextVar

from mcp.server.fastmcp import FastMCP
from flask import Flask
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import select

from api.dao import happiness_dao
from api.models.models import Token
from api.util.db_session import session_scope

# Context variable to store user_id for the current request
_current_user_id: ContextVar[Optional[int]] = ContextVar(
    'current_user_id', default=None)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to validate Bearer tokens for MCP requests only.

    Only applies to /mcp endpoint. All other paths (Flask routes, OAuth endpoints)
    pass through without authentication.
    """

    def __init__(self, app, oauth_base_url: str):
        super().__init__(app)
        self.oauth_base_url = oauth_base_url

    async def dispatch(self, request: Request, call_next):
        """Validate token and extract user_id for /mcp requests only."""
        # Only apply authentication to /mcp endpoint
        # Let all other requests (Flask routes, OAuth endpoints) pass through
        if not request.url.path.startswith('/mcp'):
            return await call_next(request)

        # Get authorization header
        auth_header = request.headers.get('authorization')

        # Validate token and get user_id
        user_id = get_user_from_token(auth_header)

        if not user_id:
            # Return 401 with WWW-Authenticate header to trigger OAuth flow
            return JSONResponse(
                status_code=401,
                content={"error": "unauthorized",
                         "message": "Valid Bearer token required"},
                headers={
                    "WWW-Authenticate": f'Bearer realm="HappinessApp MCP", resource_metadata_uri="{self.oauth_base_url}/.well-known/oauth-protected-resource"'
                }
            )

        # Store user_id in request state for tools to access
        request.state.user_id = user_id

        # Also store in context variable for easy access in tools
        _current_user_id.set(user_id)

        # Continue processing
        response = await call_next(request)

        # Clean up context variable after request
        _current_user_id.set(None)

        return response


def get_user_from_token(authorization_header: Optional[str]) -> Optional[int]:
    """
    Extract and validate user from Bearer token. Returns user_id if valid, None otherwise.
    """
    if not authorization_header:
        return None

    # Parse Bearer token
    parts = authorization_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None

    # Validate token using session_scope (works in ASGI context)
    session_token = parts[1]
    token_hash = hashlib.sha256(session_token.encode()).hexdigest()
    with session_scope() as session:
        token = session.execute(
            select(Token).where(Token.session_token == token_hash)
        ).scalar()

        if token and token.verify():
            return token.user_id

    return None


def create_mcp_server() -> FastMCP:
    """
    Create and configure the MCP server with tools for happiness data queries.
    """
    mcp = FastMCP(
        name="HappinessApp",
        streamable_http_path="/mcp",
        instructions=(
            "This server provides tools to query a user's happiness data. "
            "Happiness entries include a value (0-10), optional comment text, and a timestamp. "
            "Use these tools to answer questions about the user's happiness trends, "
            "specific events, and comparisons over time."
        )
    )

    @mcp.tool()
    def happiness_list_by_date_range(start: str, end: str) -> dict:
        """
        Get happiness entries between two dates (inclusive).

        Args:
            start: Start date in YYYY-MM-DD format
            end: End date in YYYY-MM-DD format

        Returns:
            Dictionary with list of happiness entries and summary statistics
        """
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.strptime(end, "%Y-%m-%d").date()
        except ValueError as e:
            return {"error": f"Invalid date format. Use YYYY-MM-DD. {str(e)}"}

        if start_date > end_date:
            return {"error": "Start date must be before or equal to end date"}

        # Get user_id from context variable (set by middleware)
        user_id = _current_user_id.get()
        with session_scope() as session:
            entries = happiness_dao.get_happiness_by_date_range(
                [user_id], start_date, end_date, session=session
            )

        result = {
            "entries": [
                {
                    "date": entry.timestamp.strftime("%Y-%m-%d"),
                    "value": entry.value,
                    "comment": entry.comment or ""
                }
                for entry in entries
            ],
            "count": len(entries)
        }

        if entries:
            values = [e.value for e in entries]
            result["average"] = round(mean(values), 2)
            result["min"] = min(values)
            result["max"] = max(values)

        return result

    @mcp.tool()
    def happiness_search(
        text: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        low: Optional[float] = None,
        high: Optional[float] = None,
        limit: int = 20
    ) -> dict:
        """
        Search happiness entries with filters. At least one filter must be provided.

        Args:
            text: Search for entries containing this text in comments
            start: Start date in YYYY-MM-DD format
            end: End date in YYYY-MM-DD format
            low: Minimum happiness value (0-10)
            high: Maximum happiness value (0-10)
            limit: Maximum number of results (default: 20)

        Returns:
            Dictionary with matching happiness entries
        """
        # Parse dates if provided
        start_date = None
        end_date = None
        if start:
            try:
                start_date = datetime.strptime(start, "%Y-%m-%d").date()
            except ValueError as e:
                return {"error": f"Invalid start date format. Use YYYY-MM-DD. {str(e)}"}
        if end:
            try:
                end_date = datetime.strptime(end, "%Y-%m-%d").date()
            except ValueError as e:
                return {"error": f"Invalid end date format. Use YYYY-MM-DD. {str(e)}"}

        # Validate at least one filter is provided
        if not any([text, start_date, end_date, low is not None, high is not None]):
            return {"error": "At least one filter parameter must be provided"}

        # Get user_id from context variable (set by middleware)
        user_id = _current_user_id.get()
        with session_scope() as session:
            entries = happiness_dao.get_happiness_by_filter(
                user_id=user_id,
                page=1,
                per_page=limit,
                start=start_date,
                end=end_date,
                low=low,
                high=high,
                text=text,
                session=session,
            )

        return {
            "entries": [
                {
                    "date": entry.timestamp.strftime("%Y-%m-%d"),
                    "value": entry.value,
                    "comment": entry.comment or ""
                }
                for entry in entries
            ],
            "count": len(entries),
            "limit": limit
        }

    return mcp


def create_mcp_asgi_app(flask_app: Flask):
    """
    Create an ASGI application for the MCP server with authentication middleware.
    """
    mcp = create_mcp_server()
    asgi_app = mcp.streamable_http_app()

    # Add authentication middleware
    oauth_base_url = flask_app.config['OAUTH_BASE_URL']
    asgi_app.add_middleware(AuthMiddleware, oauth_base_url=oauth_base_url)

    return asgi_app
