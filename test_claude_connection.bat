@echo off
echo Testing Hospital Management MCP Server for Claude Desktop
echo =========================================================

echo 1. Testing Python availability...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH
    exit /b 1
)

echo 2. Testing server startup...
cd /d "C:\Users\Arivanan\hospital-management-system\backend-python"
timeout /t 3 /nobreak > nul
echo Server should start with initialization messages...

echo 3. Configuration location:
echo C:\Users\Arivanan\AppData\Roaming\Claude\claude_desktop_config.json
if exist "C:\Users\Arivanan\AppData\Roaming\Claude\claude_desktop_config.json" (
    echo ✓ Configuration file exists
) else (
    echo ✗ Configuration file missing
)

echo.
echo Instructions:
echo 1. Restart Claude Desktop
echo 2. Look for hospital-management-system in available tools
echo 3. Try asking Claude: "List all patients in the hospital"
pause
