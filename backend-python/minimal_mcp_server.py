#!/usr/bin/env python3
"""
Minimal MCP server test - starts without database dependency
"""
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("hospital-test-server")

@mcp.tool()
def server_health_check() -> dict:
    """Basic health check tool that doesn't require database."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": "AWS" if os.getenv('AWS_EXECUTION_ENV') else "Local",
        "message": "MCP server is running without database"
    }

@mcp.tool()
def list_environment_variables() -> dict:
    """List relevant environment variables for debugging."""
    env_vars = {}
    relevant_vars = [
        'DATABASE_URL', 'AWS_EXECUTION_ENV', 'POSTGRES_DB', 
        'POSTGRES_USER', 'POSTGRES_PASSWORD', 'PYTHONPATH'
    ]
    
    for var in relevant_vars:
        env_vars[var] = os.getenv(var, 'Not Set')
    
    return {
        "environment_variables": env_vars,
        "working_directory": os.getcwd()
    }

if __name__ == "__main__":
    print("🧪 Starting minimal MCP server for testing...")
    print("📡 Server has 2 basic tools available")
    print("✅ No database dependency - should start immediately")
    
    # Run the server
    mcp.run()
