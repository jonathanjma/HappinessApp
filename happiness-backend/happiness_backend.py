from starlette.middleware.wsgi import WSGIMiddleware

from api import create_app
from api.util.db_session import init_session_factory
from api.routes.mcp_server import create_mcp_asgi_app

# Create Flask app (which is WSGI)
flask_app = create_app()

# Initialize global SQLAlchemy session factory for MCP tools
init_session_factory(flask_app)

# Create MCP server (which is ASGI)
app = create_mcp_asgi_app(flask_app)

# Mount Flask in the ASGI server 
# MCP: served at "/mcp"
# Flask app: mounted at "/" (everything else)
app.mount("/", WSGIMiddleware(flask_app))
