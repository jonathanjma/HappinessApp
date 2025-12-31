"""
MCP (Model Context Protocol) server for Happiness App.
Exposes read-only tools for LLMs to query user happiness data.
"""
from datetime import datetime, timedelta
from typing import Optional
from statistics import mean, median
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
    Extract and validate user from Bearer token.
    Returns user_id if valid, None otherwise.

    Uses session_scope instead of Flask db.session since this runs in ASGI context.
    """
    if not authorization_header:
        return None

    # Parse Bearer token
    parts = authorization_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None

    session_token = parts[1]

    # Validate token using session_scope (works in ASGI context)
    token_hash = hashlib.sha256(session_token.encode()).hexdigest()

    with session_scope() as session:
        token = session.execute(
            select(Token).where(Token.session_token == token_hash)
        ).scalar()

        if token and token.verify():
            return token.user_id

    return None


def create_mcp_server(flask_app: Flask) -> FastMCP:
    """
    Create and configure the MCP server with tools for happiness data queries.

    Args:
        flask_app: The Flask application instance (needed for app context in DAOs)

    Returns:
        FastMCP: Configured MCP server instance
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
        if not user_id:
            return {"error": "Authentication required"}

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
        if not user_id:
            return {"error": "Authentication required"}

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

    # @mcp.tool()
    # def happiness_weekly_summary(reference_date: Optional[str] = None) -> dict:
    #     """
    #     Get a summary of happiness data for the past 7 days.

    #     Args:
    #         reference_date: Reference date in YYYY-MM-DD format (defaults to today)

    #     Returns:
    #         Dictionary with weekly happiness summary including top entries and statistics
    #     """
    #     with flask_app.app_context():
    #         # Parse reference date or use today
    #         if reference_date:
    #             try:
    #                 end_date = datetime.strptime(
    #                     reference_date, "%Y-%m-%d").date()
    #             except ValueError as e:
    #                 return {"error": f"Invalid date format. Use YYYY-MM-DD. {str(e)}"}
    #         else:
    #             end_date = datetime.today().date()

    #         start_date = end_date - timedelta(days=6)  # Last 7 days inclusive

    #         entries = happiness_dao.get_happiness_by_date_range(
    #             [MCP_USER_ID], start_date, end_date
    #         )

    #         if not entries:
    #             return {
    #                 "message": "No happiness entries found for the past week",
    #                 "start": start_date.strftime("%Y-%m-%d"),
    #                 "end": end_date.strftime("%Y-%m-%d"),
    #                 "count": 0
    #             }

    #         values = [e.value for e in entries]

    #         # Find high-value entries (>= 7.0)
    #         high_entries = [e for e in entries if e.value >= 7.0]

    #         # Extract notable events (entries with comments)
    #         notable_entries = [
    #             {
    #                 "date": e.timestamp.strftime("%Y-%m-%d"),
    #                 "value": e.value,
    #                 "comment": e.comment
    #             }
    #             for e in entries if e.comment
    #         ]

    #         return {
    #             "period": {
    #                 "start": start_date.strftime("%Y-%m-%d"),
    #                 "end": end_date.strftime("%Y-%m-%d")
    #             },
    #             "statistics": {
    #                 "count": len(entries),
    #                 "average": round(mean(values), 2),
    #                 "min": min(values),
    #                 "max": max(values),
    #                 "high_count": len(high_entries)
    #             },
    #             # Top 10 entries with comments
    #             "notable_entries": notable_entries[:10]
    #         }

    # @mcp.tool()
    # def happiness_compare_months(year: int, month: int) -> dict:
    #     """
    #     Compare happiness between a specified month and the previous month.

    #     Args:
    #         year: Year (e.g., 2024)
    #         month: Month number (1-12)

    #     Returns:
    #         Dictionary with comparison data between the two months
    #     """
    #     with flask_app.app_context():
    #         try:
    #             # Calculate month ranges
    #             this_month_start = datetime(year, month, 1).date()

    #             # Calculate next month for end date
    #             if month == 12:
    #                 next_month_start = datetime(year + 1, 1, 1).date()
    #             else:
    #                 next_month_start = datetime(year, month + 1, 1).date()
    #             this_month_end = next_month_start - timedelta(days=1)

    #             # Calculate previous month
    #             if month == 1:
    #                 prev_month_start = datetime(year - 1, 12, 1).date()
    #                 prev_month_end = datetime(
    #                     year, 1, 1).date() - timedelta(days=1)
    #             else:
    #                 prev_month_start = datetime(year, month - 1, 1).date()
    #                 prev_month_end = this_month_start - timedelta(days=1)

    #         except ValueError as e:
    #             return {"error": f"Invalid date: {str(e)}"}

    #         # Fetch data for both months
    #         this_month_entries = happiness_dao.get_happiness_by_date_range(
    #             [MCP_USER_ID], this_month_start, this_month_end
    #         )
    #         prev_month_entries = happiness_dao.get_happiness_by_date_range(
    #             [MCP_USER_ID], prev_month_start, prev_month_end
    #         )

    #         # Calculate statistics
    #         result = {
    #             "this_month": {
    #                 "period": f"{this_month_start.strftime('%Y-%m-%d')} to {this_month_end.strftime('%Y-%m-%d')}",
    #                 "count": len(this_month_entries)
    #             },
    #             "previous_month": {
    #                 "period": f"{prev_month_start.strftime('%Y-%m-%d')} to {prev_month_end.strftime('%Y-%m-%d')}",
    #                 "count": len(prev_month_entries)
    #             }
    #         }

    #         if this_month_entries:
    #             this_values = [e.value for e in this_month_entries]
    #             result["this_month"]["average"] = round(mean(this_values), 2)
    #             result["this_month"]["median"] = round(median(this_values), 2)
    #             result["this_month"]["min"] = min(this_values)
    #             result["this_month"]["max"] = max(this_values)

    #         if prev_month_entries:
    #             prev_values = [e.value for e in prev_month_entries]
    #             result["previous_month"]["average"] = round(
    #                 mean(prev_values), 2)
    #             result["previous_month"]["median"] = round(
    #                 median(prev_values), 2)
    #             result["previous_month"]["min"] = min(prev_values)
    #             result["previous_month"]["max"] = max(prev_values)

    #         # Calculate change if both months have data
    #         if this_month_entries and prev_month_entries:
    #             avg_change = result["this_month"]["average"] - \
    #                 result["previous_month"]["average"]
    #             result["comparison"] = {
    #                 "average_change": round(avg_change, 2),
    #                 "percentage_change": round((avg_change / result["previous_month"]["average"]) * 100, 1) if result["previous_month"]["average"] > 0 else None,
    #                 "entry_count_change": len(this_month_entries) - len(prev_month_entries)
    #             }

    #         return result

    # @mcp.tool()
    # def happiness_last_mention(text: str) -> dict:
    #     """
    #     Find the most recent happiness entry that mentions specific text.

    #     Args:
    #         text: Text to search for in happiness entry comments

    #     Returns:
    #         Dictionary with the most recent matching entry, or None if not found
    #     """
    #     with flask_app.app_context():
    #         if not text:
    #             return {"error": "Text parameter is required"}

    #         # Search with text filter, sorted by most recent, limit 1
    #         entries = happiness_dao.get_happiness_by_filter(
    #             user_id=MCP_USER_ID,
    #             page=1,
    #             per_page=1,
    #             start=None,
    #             end=None,
    #             low=None,
    #             high=None,
    #             text=text
    #         )

    #         if not entries:
    #             return {
    #                 "found": False,
    #                 "message": f"No happiness entries found containing '{text}'"
    #             }

    #         entry = entries[0]
    #         return {
    #             "found": True,
    #             "entry": {
    #                 "date": entry.timestamp.strftime("%Y-%m-%d"),
    #                 "value": entry.value,
    #                 "comment": entry.comment or ""
    #             }
    #         }

    return mcp


def create_mcp_asgi_app(flask_app: Flask):
    """
    Create an ASGI application for the MCP server with authentication middleware.

    NOTE: The returned app requires ASGI lifespan handling (FastMCP uses Starlette lifespan
    to initialize its internal task group). This works correctly when served by uvicorn
    or when mounted into another ASGI app.

    Args:
        flask_app: The Flask application instance

    Returns:
        ASGI application (Starlette app) with authentication middleware
    """
    mcp = create_mcp_server(flask_app)
    asgi_app = mcp.streamable_http_app()

    # Add authentication middleware
    oauth_base_url = flask_app.config['OAUTH_BASE_URL']
    asgi_app.add_middleware(AuthMiddleware, oauth_base_url=oauth_base_url)

    return asgi_app
