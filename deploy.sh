#!/bin/bash

# Hospital Management System - Docker Deployment Script
# This script builds and runs the entire system using Docker Compose

set -e

echo "🏥 Hospital Management System - Docker Deployment"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        echo "⚠️  No .env file found. Copying from .env.docker template..."
        cp .env.docker .env
        echo "📝 Please edit .env file with your actual API keys:"
        echo "   - GEMINI_API_KEY"
        echo "   - VITE_CLAUDE_API_KEY (optional)"
        echo "   - VITE_OPENAI_API_KEY (optional)"
        echo "   - VITE_GROQ_API_KEY (optional)"
        echo "   - VITE_GOOGLE_API_KEY (optional)"
        echo ""
        read -p "Press Enter to continue after updating .env file..."
    fi
}

# Function to build and start services
start_services() {
    echo "🔨 Building Docker images..."
    docker-compose build

    echo "🚀 Starting services..."
    docker-compose up -d

    echo "⏳ Waiting for services to be ready..."
    sleep 10

    echo "🔍 Checking service status..."
    docker-compose ps
}

# Function to show service URLs
show_urls() {
    echo ""
    echo "🌐 Service URLs:"
    echo "================================"
    echo "Frontend:              http://localhost"
    echo "MCP Process Manager:   http://localhost:3001"
    echo "Backend Python (MCP):  http://localhost:8000"
    echo "PostgreSQL Database:   localhost:5432"
    echo ""
    echo "📊 Health Check URLs:"
    echo "MCP Manager Status:    http://localhost:3001/mcp/status"
    echo "Backend Tools:         http://localhost:3001/mcp/tools"
}

# Function to show logs
show_logs() {
    echo "📋 Showing logs (Ctrl+C to stop)..."
    docker-compose logs -f
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping services..."
    docker-compose down
}

# Function to clean up
cleanup() {
    echo "🧹 Cleaning up (removing containers, networks, volumes)..."
    docker-compose down -v
    docker system prune -f
}

# Main menu
case "${1:-start}" in
    "start")
        check_env_file
        start_services
        show_urls
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        sleep 2
        check_env_file
        start_services
        show_urls
        ;;
    "logs")
        show_logs
        ;;
    "cleanup")
        cleanup
        ;;
    "status")
        docker-compose ps
        show_urls
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|cleanup|status}"
        echo ""
        echo "Commands:"
        echo "  start     - Build and start all services (default)"
        echo "  stop      - Stop all services"
        echo "  restart   - Restart all services"
        echo "  logs      - Show logs from all services"
        echo "  cleanup   - Stop services and remove volumes/networks"
        echo "  status    - Show service status and URLs"
        exit 1
        ;;
esac
