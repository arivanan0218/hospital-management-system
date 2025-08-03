@echo off
setlocal enabledelayedexpansion

echo ====================================
echo Hospital Management System MCP Bridge
echo Complete Setup and Launch
echo ====================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo 💡 Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if we're in the right directory
if not exist "mcp_bridge.py" (
    echo ❌ ERROR: mcp_bridge.py not found
    echo 💡 Please run this script from the mcp-bridge directory
    pause
    exit /b 1
)

echo ✅ Bridge files found

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment exists
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade requirements
echo 📥 Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ ERROR: Failed to install requirements
    echo 💡 Try running: pip install --upgrade pip
    pause
    exit /b 1
)

echo ✅ Requirements installed

REM Check if the parent MCP server exists
set "MCP_SERVER_PATH=..\backend-python\comprehensive_server.py"
if not exist "%MCP_SERVER_PATH%" (
    echo ⚠️  WARNING: MCP server not found at %MCP_SERVER_PATH%
    echo 💡 Make sure the comprehensive_server.py is in the correct location
    echo 💡 Continuing anyway - bridge will fail if server is not found
    echo.
)

echo 🚀 Starting MCP Bridge Server...
echo.
echo 🌐 Bridge will be available at: http://localhost:8080
echo 📖 API documentation will be at: http://localhost:8080/docs
echo.
echo 🔧 Starting bridge in background and running quick test...
echo.

REM Start the bridge in background
start /B python mcp_bridge.py

REM Wait a moment for the server to start
timeout /t 3 /nobreak >nul

REM Run quick test
echo 🧪 Running quick test...
python quick_test.py --wait

if errorlevel 1 (
    echo ❌ Quick test failed
    echo 💡 Check the console output above for errors
    pause
    exit /b 1
)

echo.
echo ✅ Bridge is running successfully!
echo.
echo 🎯 What you can do now:
echo   1. Open http://localhost:8080 in your browser
echo   2. View API docs at http://localhost:8080/docs
echo   3. Run test_bridge.bat to test functionality
echo   4. Use the HTTP API endpoints (see README.md)
echo.
echo 🛑 To stop the bridge: Press Ctrl+C in this window
echo.
echo Press any key to keep the bridge running...
pause >nul

echo.
echo 🔄 Bridge is still running in the background
echo 💡 Close this window to stop the bridge
echo.

REM Keep the window open
:loop
timeout /t 30 /nobreak >nul
echo 💓 Bridge heartbeat - still running at http://localhost:8080
goto loop
