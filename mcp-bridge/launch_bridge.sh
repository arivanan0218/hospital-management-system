#!/bin/bash

echo "===================================="
echo "Hospital Management System MCP Bridge"
echo "Complete Setup and Launch"
echo "===================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ ERROR: Python 3 is not installed or not in PATH${NC}"
    echo -e "${BLUE}💡 Please install Python 3.8+ and add it to your PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python found${NC}"

# Check if we're in the right directory
if [ ! -f "mcp_bridge.py" ]; then
    echo -e "${RED}❌ ERROR: mcp_bridge.py not found${NC}"
    echo -e "${BLUE}💡 Please run this script from the mcp-bridge directory${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Bridge files found${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ ERROR: Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Install/upgrade requirements
echo -e "${BLUE}📥 Installing requirements...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERROR: Failed to install requirements${NC}"
    echo -e "${BLUE}💡 Try running: pip install --upgrade pip${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Requirements installed${NC}"

# Check if the parent MCP server exists
MCP_SERVER_PATH="../backend-python/comprehensive_server.py"
if [ ! -f "$MCP_SERVER_PATH" ]; then
    echo -e "${YELLOW}⚠️  WARNING: MCP server not found at $MCP_SERVER_PATH${NC}"
    echo -e "${BLUE}💡 Make sure the comprehensive_server.py is in the correct location${NC}"
    echo -e "${BLUE}💡 Continuing anyway - bridge will fail if server is not found${NC}"
    echo
fi

echo -e "${BLUE}🚀 Starting MCP Bridge Server...${NC}"
echo
echo -e "${GREEN}🌐 Bridge will be available at: http://localhost:8080${NC}"
echo -e "${GREEN}📖 API documentation will be at: http://localhost:8080/docs${NC}"
echo
echo -e "${BLUE}🔧 Starting bridge in background and running quick test...${NC}"
echo

# Start the bridge in background
python3 mcp_bridge.py &
BRIDGE_PID=$!

# Wait a moment for the server to start
sleep 3

# Run quick test
echo -e "${BLUE}🧪 Running quick test...${NC}"
python3 quick_test.py --wait

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Quick test failed${NC}"
    echo -e "${BLUE}💡 Check the console output above for errors${NC}"
    kill $BRIDGE_PID 2>/dev/null
    exit 1
fi

echo
echo -e "${GREEN}✅ Bridge is running successfully!${NC}"
echo
echo -e "${BLUE}🎯 What you can do now:${NC}"
echo "   1. Open http://localhost:8080 in your browser"
echo "   2. View API docs at http://localhost:8080/docs"
echo "   3. Run ./test_bridge.sh to test functionality"
echo "   4. Use the HTTP API endpoints (see README.md)"
echo
echo -e "${YELLOW}🛑 To stop the bridge: Press Ctrl+C${NC}"
echo

# Function to cleanup on exit
cleanup() {
    echo
    echo -e "${BLUE}🛑 Stopping bridge server...${NC}"
    kill $BRIDGE_PID 2>/dev/null
    echo -e "${GREEN}✅ Bridge stopped${NC}"
    exit 0
}

# Set trap to catch Ctrl+C
trap cleanup SIGINT SIGTERM

echo "Press Ctrl+C to stop the bridge..."
echo

# Keep the script running and show heartbeat
while true; do
    sleep 30
    if kill -0 $BRIDGE_PID 2>/dev/null; then
        echo -e "${GREEN}💓 Bridge heartbeat - still running at http://localhost:8080${NC}"
    else
        echo -e "${RED}❌ Bridge process died${NC}"
        exit 1
    fi
done
