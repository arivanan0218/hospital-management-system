#!/bin/bash
# Simple MCP server startup for testing - no database dependency

echo "🧪 Starting minimal MCP server (no database)..."

# Start minimal MCP server that doesn't require database
echo "📡 Starting minimal MCP server..."
exec uv run mcp run minimal_mcp_server.py
