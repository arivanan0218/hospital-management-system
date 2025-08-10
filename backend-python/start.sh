#!/bin/bash

# Hospital Management System - Docker Startup Script

# Wait for database to be ready
wait_for_db() {
    echo "Waiting for PostgreSQL to be ready..."
    while ! pg_isready -h postgres -U postgres; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    echo "PostgreSQL is ready!"
}

# Initialize database if needed
init_database() {
    echo "Initializing database..."
    python setup_database.py || echo "Database initialization completed or already exists"
}

# Start the FastMCP server
start_server() {
    echo "Starting Hospital Management MCP Server..."
    python comprehensive_server.py
}

# Main execution
main() {
    wait_for_db
    init_database
    start_server
}

# Run if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
