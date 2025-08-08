@echo off
REM Hospital Management System - Local Development Setup for Windows

echo 🏥 Setting up Hospital Management System for Local Development

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)
echo ✅ Docker is installed

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not available. Please make sure Docker Desktop is running.
    pause
    exit /b 1
)
echo ✅ Docker Compose is available

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📄 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file and add your API keys before running the application
) else (
    echo ✅ .env file already exists
)

REM Build and start the application
echo 🐳 Building and starting Docker containers...
docker-compose build
docker-compose up -d

echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Check if services are running
echo 🔍 Checking service status...
docker-compose ps

REM Show application URLs
echo.
echo 🎉 Hospital Management System is ready!
echo.
echo 📱 Application URLs:
echo    Frontend:     http://localhost
echo    Backend API:  http://localhost:8000
echo    MCP Manager:  http://localhost:3001
echo    Database:     localhost:5432
echo.
echo 📋 Next steps:
echo    1. Edit .env file with your API keys
echo    2. Restart with: docker-compose restart
echo    3. View logs with: docker-compose logs -f
echo    4. Stop with: docker-compose down
echo.
echo 🔧 For AWS deployment, see DEPLOYMENT.md

pause
