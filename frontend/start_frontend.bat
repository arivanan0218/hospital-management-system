@echo off
echo ========================================
echo Hospital AI Assistant Frontend
echo Starting Development Server
echo ========================================
echo.

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Node.js is not installed or not in PATH
    echo 💡 Please install Node.js 16+ from https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js found

REM Check if we're in the right directory
if not exist "package.json" (
    echo ❌ ERROR: package.json not found
    echo 💡 Please run this script from the frontend directory
    pause
    exit /b 1
)

echo ✅ Frontend project found

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
    if errorlevel 1 (
        echo ❌ ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
) else (
    echo ✅ Dependencies already installed
)

REM Check for API key configuration
if not exist ".env" (
    echo ⚠️  WARNING: .env file not found
    echo � Copy .env.example to .env and add your Gemini API key
    echo.
) else (
    echo ✅ Environment file found
)

echo.
echo �🚀 Starting development server...
echo.
echo 🌐 Frontend will be available at: http://localhost:5173
echo 📖 Make sure MCP Bridge is running at: http://localhost:8080
echo.
echo 💡 Configure your Gemini API key in .env file or in the app settings!
echo.
echo 🛑 To stop the server: Press Ctrl+C
echo.

npm run dev

pause
