@echo off
REM Hospital Management System - Docker Deployment Script (Windows)
REM This script builds and runs the entire system using Docker Compose

echo 🏥 Hospital Management System - Docker Deployment
echo ==================================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    docker compose version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Docker Compose is not installed. Please install Docker Compose first.
        exit /b 1
    )
)

REM Function to check if .env file exists
if not exist .env (
    echo ⚠️  No .env file found. Copying from .env.docker template...
    copy .env.docker .env >nul
    echo 📝 Please edit .env file with your actual API keys:
    echo    - GEMINI_API_KEY
    echo    - VITE_CLAUDE_API_KEY ^(optional^)
    echo    - VITE_OPENAI_API_KEY ^(optional^)
    echo    - VITE_GROQ_API_KEY ^(optional^)
    echo    - VITE_GOOGLE_API_KEY ^(optional^)
    echo.
    pause
)

REM Get command line argument
set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=start

if "%COMMAND%"=="start" goto start
if "%COMMAND%"=="stop" goto stop
if "%COMMAND%"=="restart" goto restart
if "%COMMAND%"=="logs" goto logs
if "%COMMAND%"=="cleanup" goto cleanup
if "%COMMAND%"=="status" goto status
goto usage

:start
echo 🔨 Building Docker images...
docker-compose build
if %errorlevel% neq 0 (
    echo ❌ Failed to build images
    exit /b 1
)

echo 🚀 Starting services...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Failed to start services
    exit /b 1
)

echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo 🔍 Checking service status...
docker-compose ps

goto show_urls

:stop
echo 🛑 Stopping services...
docker-compose down
goto end

:restart
echo 🛑 Stopping services...
docker-compose down
timeout /t 2 /nobreak >nul
goto start

:logs
echo 📋 Showing logs ^(Ctrl+C to stop^)...
docker-compose logs -f
goto end

:cleanup
echo 🧹 Cleaning up ^(removing containers, networks, volumes^)...
docker-compose down -v
docker system prune -f
goto end

:status
docker-compose ps
goto show_urls

:show_urls
echo.
echo 🌐 Service URLs:
echo ================================
echo Frontend:              http://localhost
echo MCP Process Manager:   http://localhost:3001
echo Backend Python ^(MCP^):  http://localhost:8000
echo PostgreSQL Database:   localhost:5432
echo.
echo 📊 Health Check URLs:
echo MCP Manager Status:    http://localhost:3001/mcp/status
echo Backend Tools:         http://localhost:3001/mcp/tools
goto end

:usage
echo Usage: %0 {start^|stop^|restart^|logs^|cleanup^|status}
echo.
echo Commands:
echo   start     - Build and start all services ^(default^)
echo   stop      - Stop all services
echo   restart   - Restart all services
echo   logs      - Show logs from all services
echo   cleanup   - Stop services and remove volumes/networks
echo   status    - Show service status and URLs
exit /b 1

:end
