#!/bin/bash
# Startup script for MCP server with database initialization

echo "🚀 Starting Hospital Management MCP Server..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if pg_isready -h localhost -p 5432 -U postgres; then
        echo "✅ PostgreSQL is ready!"
        break
    fi
    echo "🔄 Waiting for PostgreSQL... ($i/30)"
    sleep 2
done

# Test database connection
echo "🔍 Testing database connection..."
uv run python test_db_connection.py
if [ $? -eq 0 ]; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
fi

# Initialize database schema
echo "🔧 Initializing database..."
uv run python init_database.py
if [ $? -eq 0 ]; then
    echo "✅ Database initialized"
else
    echo "⚠️ Database initialization had issues, continuing anyway..."
fi

# Start MCP server
echo "📡 Starting MCP server..."
exec uv run mcp run comprehensive_server.py
