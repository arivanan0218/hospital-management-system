@echo off
echo Testing Hospital Management System MCP Bridge...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install httpx if not available
python -c "import httpx" 2>nul
if errorlevel 1 (
    echo Installing httpx for testing...
    pip install httpx
)

REM Run the test client
echo.
echo Running bridge test client...
echo Make sure the bridge server is running on http://localhost:8080
echo.

python client.py

echo.
echo Test completed.
pause
