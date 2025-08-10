#!/bin/bash

# Hospital Management System - Start Script

echo "🏥 Hospital Management System - Docker Startup"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker is running"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cat > .env << 'EOF'
# Hospital Management System - Environment Variables for Docker

# Backend Python Environment Variables
GEMINI_API_KEY=your_gemini_api_key_here

# Frontend Environment Variables
VITE_CLAUDE_API_KEY=your_claude_api_key_here
VITE_OPENAI_API_KEY=your_openai_api_key_here
VITE_GROQ_API_KEY=your_groq_api_key_here
VITE_GOOGLE_API_KEY=your_google_api_key_here

# Database Configuration (automatically handled by docker-compose)
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/hospital_management

# MCP Configuration
VITE_MCP_BRIDGE_URL=http://localhost:8000
EOF
    echo "✅ Created .env file. You can edit it to add your API keys."
fi

# Check which compose file to use
COMPOSE_FILE="docker-compose.simple.yml"
if [ "$1" = "--full" ] || [ "$1" = "-f" ]; then
    COMPOSE_FILE="docker-compose.yml"
    echo "🌐 Using full setup with Nginx reverse proxy"
else
    echo "🚀 Using simple setup (no reverse proxy)"
    echo "   Use --full flag for Nginx reverse proxy setup"
fi

echo ""
echo "Starting services with $COMPOSE_FILE..."
echo "This may take a few minutes on first run..."
echo ""

# Start the services
docker-compose -f "$COMPOSE_FILE" up --build

# Show access information when done
echo ""
echo "🎉 Hospital Management System is running!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "💾 Database: localhost:5432 (postgres/postgres)"
echo ""
echo "Press Ctrl+C to stop all services"
