from datetime import datetime
import json

import pytest
from starlette.testclient import TestClient

from api import create_app
from api.app import db
from api.models.models import Happiness, User
from api.routes.mcp_server import AuthMiddleware, create_mcp_server
from api.util.db_session import init_session_factory
from config import TestConfig
from mcp.server.streamable_http import (
    MCP_PROTOCOL_VERSION_HEADER,
    MCP_SESSION_ID_HEADER,
)
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import LATEST_PROTOCOL_VERSION


def _initialize_payload():
    # Minimal MCP initialize request for a JSON-RPC session.
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": LATEST_PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {
                "name": "pytest",
                "version": "0.1",
            },
        },
    }


def _jsonrpc_request(method, params, request_id):
    # Helper to build JSON-RPC requests for MCP endpoints.
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params,
    }


@pytest.fixture
def mcp_env():
    app = create_app(TestConfig)
    init_session_factory(app)

    with app.app_context():
        db.create_all()
        # Seed a user, token, and a few happiness entries for MCP tool queries.
        user = User(
            email="mcp@example.com",
            username="mcp_user",
            password="password",
        )
        db.session.add(user)
        db.session.commit()

        token_obj, token = user.create_token()
        db.session.add(token_obj)

        entries = [
            Happiness(
                user_id=user.id,
                value=5.0,
                comment="ok",
                timestamp=datetime(2024, 1, 10),
            ),
            Happiness(
                user_id=user.id,
                value=7.0,
                comment="good",
                timestamp=datetime(2024, 1, 12),
            ),
            Happiness(
                user_id=user.id,
                value=3.0,
                comment="rough",
                timestamp=datetime(2024, 1, 15),
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

    mcp = create_mcp_server()
    # Disable DNS rebinding checks for the TestClient host header.
    mcp.settings.transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=False
    )
    # Use JSON responses so tool calls return a JSON-RPC response body.
    mcp.settings.json_response = True
    asgi_app = mcp.streamable_http_app()
    # Attach auth middleware so /mcp enforces Bearer tokens.
    asgi_app.add_middleware(
        AuthMiddleware,
        oauth_base_url=app.config["OAUTH_BASE_URL"],
    )

    return asgi_app, token


def test_mcp_auth_and_tools(mcp_env):
    asgi_app, token = mcp_env

    with TestClient(asgi_app) as client:
        # Verify auth middleware blocks unauthenticated /mcp access.
        no_token_response = client.post(
            "/mcp",
            json=_initialize_payload(),
            headers={"Accept": "application/json"},
        )
        assert no_token_response.status_code == 401
        assert "WWW-Authenticate" in no_token_response.headers

        auth_headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        init_response = client.post(
            "/mcp",
            json=_initialize_payload(),
            headers=auth_headers,
        )
        assert init_response.status_code == 200

        # Session ID is required for subsequent MCP requests.
        session_id = init_response.headers.get(MCP_SESSION_ID_HEADER)
        assert session_id

        mcp_headers = {
            **auth_headers,
            MCP_SESSION_ID_HEADER: session_id,
            MCP_PROTOCOL_VERSION_HEADER: LATEST_PROTOCOL_VERSION,
        }

        # List available tools and ensure expected MCP tools are registered.
        list_tools_response = client.post(
            "/mcp",
            json=_jsonrpc_request("tools/list", {}, 2),
            headers=mcp_headers,
        )
        assert list_tools_response.status_code == 200
        tools = list_tools_response.json().get("result", {}).get("tools", [])
        tool_names = {tool.get("name") for tool in tools}
        assert "happiness_list_by_date_range" in tool_names
        assert "happiness_search" in tool_names

        # Call the date-range tool and validate returned entries.
        call_tool_response = client.post(
            "/mcp",
            json=_jsonrpc_request(
                "tools/call",
                {
                    "name": "happiness_list_by_date_range",
                    "arguments": {"start": "2024-01-10", "end": "2024-01-12"},
                },
                3,
            ),
            headers=mcp_headers,
        )
        assert call_tool_response.status_code == 200
        result = call_tool_response.json().get("result", {})
        structured = result.get("structuredContent")
        if structured is None:
            content_blocks = result.get("content", [])
            assert content_blocks
            structured = json.loads(content_blocks[0].get("text", "{}"))
        assert structured.get("count") == 2
        assert len(structured.get("entries", [])) == 2
