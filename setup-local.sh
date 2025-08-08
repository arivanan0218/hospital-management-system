#!/bin/bash

# Hospital Management System - Local Development Setup

echo "🏥 Setting up Hospital Management System for Local Development"

# Check if required tools are installed
check_dependency() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    else
        echo "✅ $1 is installed"
    fi
}

echo "🔍 Checking dependencies..."
check_dependency "docker"
check_dependency "docker-compose"
check_dependency "git"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your API keys before running the application"
else
    echo "✅ .env file already exists"
fi

# Build and start the application
echo "🐳 Building and starting Docker containers..."
docker-compose build
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

# Show application URLs
echo ""
echo "🎉 Hospital Management System is ready!"
echo ""
echo "📱 Application URLs:"
echo "   Frontend:     http://localhost"
echo "   Backend API:  http://localhost:8000"
echo "   MCP Manager:  http://localhost:3001"
echo "   Database:     localhost:5432"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env file with your API keys"
echo "   2. Restart with: docker-compose restart"
echo "   3. View logs with: docker-compose logs -f"
echo "   4. Stop with: docker-compose down"
echo ""
echo "🔧 For AWS deployment, see DEPLOYMENT.md"
