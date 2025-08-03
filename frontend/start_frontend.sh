#!/bin/bash
echo "========================================"
echo "Hospital AI Assistant Frontend"
echo "Starting Development Server"
echo "========================================"
echo

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ ERROR: Node.js is not installed or not in PATH"
    echo "💡 Please install Node.js 16+ from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ ERROR: package.json not found"
    echo "💡 Please run this script from the frontend directory"
    exit 1
fi

echo "✅ Frontend project found"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

echo
echo "🚀 Starting development server..."
echo
echo "🌐 Frontend will be available at: http://localhost:5173"
echo "📖 Make sure MCP Bridge is running at: http://localhost:8080"
echo
echo "💡 Don't forget to configure your Gemini API key in the settings!"
echo
echo "🛑 To stop the server: Press Ctrl+C"
echo

npm run dev
