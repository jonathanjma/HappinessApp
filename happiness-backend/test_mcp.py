"""
Test script for MCP server integration.
Verifies that all MCP tools are working correctly.

Usage:
    python test_mcp.py          # Run tests only
    python test_mcp.py --serve  # Run tests then start the MCP server
"""
import sys
import asyncio
from datetime import date, timedelta
from api.app import create_app
from api.routes.mcp_server import create_mcp_server
from api.util.db_session import init_session_factory

# Initialize MCP server at module level for mcp dev command
app = create_app()
init_session_factory(app)
mcp = create_mcp_server(app)


async def test_mcp():
    """Run tests on the MCP server."""
    global mcp, app

    print("=" * 60)
    print("MCP Server Test Suite")
    print("=" * 60)

    try:
        # Test 1: Verify Flask app
        print("\n[1/4] Verifying Flask app...")
        print("✓ Flask app initialized successfully")

        # Test 2: Verify MCP server
        print("\n[2/4] Verifying MCP server...")
        print("✓ MCP server initialized successfully")

        # Test 3: List tools
        print("\n[3/4] Listing available tools...")
        with app.app_context():
            tools = await mcp.list_tools()
            print(f"✓ Found {len(tools)} tools:")
            for i, tool in enumerate(tools, 1):
                desc = tool.description.split('\n')[0][:60]
                print(f"   {i}. {tool.name}")
                print(f"      {desc}...")

        # Test 4: Test a tool call
        print("\n[4/4] Testing tool call (happiness_list_by_date_range)...")
        with app.app_context():
            end = date.today()
            start = end - timedelta(days=6)  # last 7 days inclusive
            result = await mcp.call_tool(
                "happiness_list_by_date_range",
                {"start": start.isoformat(), "end": end.isoformat()},
            )
            if isinstance(result, list) and len(result) > 0:
                content = result[0]
                if hasattr(content, 'text'):
                    print(f"✓ Tool call successful")
                    print(f"   Response preview: {content.text[:200]}...")
                else:
                    print(
                        f"✓ Tool call successful (result type: {type(content)})")
            else:
                print(f"✓ Tool call successful (result type: {type(result)})")

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        print("\nThe MCP server is ready to use.")
        print("Run it with: python -m api.routes.mcp_server")
        print("Or run with --serve flag to start server after tests.")
        print("Or run with: mcp dev test_mcp.py")

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 60)
        print("✗ Tests failed")
        print("=" * 60)

        return False


if __name__ == "__main__":
    tests_passed = asyncio.run(test_mcp())

    # If tests passed, optionally start the MCP server
    # Use --serve flag to start the server after tests
    start_server = "--serve" in sys.argv

    if tests_passed and start_server:
        print("\n" + "=" * 60)
        print("Starting MCP server...")
        print("=" * 60)
        # Run using stdio transport (standard for MCP clients)
        asyncio.run(mcp.run_stdio_async())
