#!/bin/bash

# Hospital Management System Local Setup
# This script sets up the development environment locally

set -e

echo "🏥 Setting up Hospital Management System locally..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cat > .env << 'EOF'
# PostgreSQL Database Configuration
POSTGRES_PASSWORD=hospital_password_2024

# Backend API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# Frontend API Keys (Optional - at least one recommended)
VITE_CLAUDE_API_KEY=your_claude_api_key_here
VITE_OPENAI_API_KEY=your_openai_api_key_here
VITE_GROQ_API_KEY=your_groq_api_key_here
VITE_GOOGLE_API_KEY=your_google_api_key_here

# Logging
LOG_LEVEL=INFO
EOF
    
    echo "✅ .env file created. Please edit it with your API keys."
    echo "⚠️  At minimum, you need to set GEMINI_API_KEY for the backend to work."
fi

# Create necessary directories
mkdir -p logs
mkdir -p data/postgres

# Build and start services
echo "🐳 Building and starting Docker containers..."
docker-compose down --remove-orphans || true
docker-compose build --no-cache
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service health..."

# Wait for PostgreSQL
echo "   Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker-compose exec postgres pg_isready -U hospital_user -d hospital_management &> /dev/null; then
        echo "   ✅ PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ❌ PostgreSQL failed to start"
        docker-compose logs postgres
        exit 1
    fi
    sleep 2
done

# Wait for Backend
echo "   Waiting for Backend API..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo "   ✅ Backend API is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ❌ Backend API failed to start"
        docker-compose logs backend
        exit 1
    fi
    sleep 2
done

# Wait for Frontend
echo "   Waiting for Frontend..."
for i in {1..30}; do
    if curl -f http://localhost:80 &> /dev/null; then
        echo "   ✅ Frontend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ❌ Frontend failed to start"
        docker-compose logs frontend
        exit 1
    fi
    sleep 2
done

# Show running containers
echo ""
echo "🐳 Running containers:"
docker-compose ps

echo ""
echo "🎉 Hospital Management System is running!"
echo ""
echo "📱 Access the application:"
echo "   • Frontend (React): http://localhost"
echo "   • Backend API: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo ""
echo "🗄️  Database connection:"
echo "   • Host: localhost"
echo "   • Port: 5432"
echo "   • Database: hospital_management"
echo "   • User: hospital_user"
echo "   • Password: (check .env file)"
echo ""
echo "📋 Useful commands:"
echo "   • View logs: docker-compose logs [service]"
echo "   • Stop all: docker-compose down"
echo "   • Restart: docker-compose restart [service]"
echo "   • Shell access: docker-compose exec [service] /bin/bash"
echo ""
echo "🔧 Development tips:"
echo "   • Edit .env file to change API keys"
echo "   • Code changes in backend-python/ will require rebuild"
echo "   • Frontend changes need rebuild and restart"
echo ""

# If GEMINI_API_KEY is not set, show warning
if grep -q "your_gemini_api_key_here" .env; then
    echo "⚠️  WARNING: GEMINI_API_KEY is not set!"
    echo "   Please edit .env file and set your Gemini API key."
    echo "   Get it from: https://aistudio.google.com/app/apikey"
    echo "   Then restart: docker-compose restart backend"
fi
