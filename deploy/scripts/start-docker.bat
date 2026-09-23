@echo off
title Hospital Management System - Docker Startup

echo 🏥 Hospital Management System - Docker Startup
echo ==============================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ docker-compose not found. Please install Docker Compose.
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    (
        echo # Hospital Management System - Environment Variables for Docker
        echo.
        echo # Backend Python Environment Variables
        echo GEMINI_API_KEY=your_gemini_api_key_here
        echo.
        echo # Frontend Environment Variables
        echo VITE_CLAUDE_API_KEY=your_claude_api_key_here
        echo VITE_OPENAI_API_KEY=your_openai_api_key_here
        echo VITE_GROQ_API_KEY=your_groq_api_key_here
        echo VITE_GOOGLE_API_KEY=your_google_api_key_here
        echo.
        echo # Database Configuration (automatically handled by docker-compose^)
        echo DATABASE_URL=postgresql://postgres:postgres@postgres:5432/hospital_management
        echo.
        echo # MCP Configuration
        echo VITE_MCP_BRIDGE_URL=http://localhost:8000
    ) > .env
    echo ✅ Created .env file. You can edit it to add your API keys.
)

REM Check which compose file to use
set COMPOSE_FILE=docker-compose.simple.yml
if "%1"=="--full" set COMPOSE_FILE=docker-compose.yml
if "%1"=="-f" set COMPOSE_FILE=docker-compose.yml

if "%COMPOSE_FILE%"=="docker-compose.yml" (
    echo 🌐 Using full setup with Nginx reverse proxy
) else (
    echo 🚀 Using simple setup (no reverse proxy^)
    echo    Use --full flag for Nginx reverse proxy setup
)

echo.
echo Starting services with %COMPOSE_FILE%...
echo This may take a few minutes on first run...
echo.

REM Start the services
docker-compose -f %COMPOSE_FILE% up --build

REM Show access information when done
echo.
echo 🎉 Hospital Management System is running!
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 💾 Database: localhost:5432 (postgres/postgres^)
echo.
echo Press Ctrl+C to stop all services
pause
