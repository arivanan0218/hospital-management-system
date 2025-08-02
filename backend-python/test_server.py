#!/usr/bin/env python3
"""Simple test MCP server for Claude Desktop debugging."""

from mcp.server.fastmcp import FastMCP
from typing import Dict, Any

# Initialize simple MCP server
mcp = FastMCP("test-server")

@mcp.tool()
def test_connection() -> Dict[str, Any]:
    """Test if the MCP server is working."""
    return {"success": True, "message": "MCP Server is working correctly!"}

@mcp.tool()
def get_server_info() -> Dict[str, Any]:
    """Get basic server information."""
    return {
        "server_name": "Hospital Management Test Server", 
        "version": "1.0.0",
        "status": "running"
    }

if __name__ == "__main__":
    try:
        print("Starting Test MCP Server...")
        print("Server ready for Claude Desktop connection")
        mcp.run()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
