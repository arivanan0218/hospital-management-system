@echo off
echo ========================================
echo Hospital Management System
echo Full Stack Startup
echo ========================================
echo.

echo 💡 This script will start both the MCP Bridge and Frontend
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo ✅ Node.js found

echo.
echo 🔧 Starting MCP Bridge Server...
echo.

REM Start MCP Bridge in background
start "MCP Bridge" cmd /k "cd mcp-bridge && python mcp_bridge.py"

REM Wait a moment for the bridge to start
timeout /t 3 /nobreak >nul

echo ✅ MCP Bridge started at http://localhost:8080
echo.
echo 🎨 Starting Frontend...
echo.

REM Start Frontend
cd frontend
if not exist "node_modules" (
    echo 📦 Installing frontend dependencies...
    npm install
)

echo ✅ Frontend starting at http://localhost:5173
echo.
echo 🎉 Both services are now running!
echo.
echo 📖 Services:
echo    - MCP Bridge: http://localhost:8080
echo    - Frontend:   http://localhost:5173
echo.
echo 🛑 To stop: Close both terminal windows
echo.

npm run dev

pause
