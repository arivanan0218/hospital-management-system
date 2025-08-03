#!/bin/bash

echo "Testing Hospital Management System MCP Bridge..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    exit 1
fi

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install httpx if not available
python3 -c "import httpx" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing httpx for testing..."
    pip install httpx
fi

# Run the test client
echo
echo "Running bridge test client..."
echo "Make sure the bridge server is running on http://localhost:8080"
echo

python3 client.py

echo
echo "Test completed."
