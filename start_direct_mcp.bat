@echo off
echo ========================================
echo   Hospital Management System Startup
echo   Direct MCP Process Communication
echo ========================================

echo.
echo 1/3 Starting MCP Process Manager (Backend)...
start "MCP Process Manager" cmd /k "cd /d c:\Users\Arivanan\hospital-management-system\mcp-process-manager && npm install && npm start"

echo.
echo Waiting for MCP Process Manager to start...
timeout /t 5 > nul

echo.
echo 2/3 Starting Frontend (React)...
start "Frontend" cmd /k "cd /d c:\Users\Arivanan\hospital-management-system\frontend && npm install && npm run dev"

echo.
echo 3/3 Setup Complete!
echo.
echo Services starting:
echo - MCP Process Manager: http://localhost:3001
echo - Frontend (React): http://localhost:5173
echo.
echo Please wait a moment for all services to fully start.
echo Then open your browser to: http://localhost:5173
echo.
echo Select "🚀 Direct MCP" mode for direct process communication.
echo.
pause
