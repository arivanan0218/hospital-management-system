@echo off
echo Hospital Management MCP Server - Claude Desktop Diagnosis
echo =======================================================

echo 1. Testing Python and server startup...
cd /d "C:\Users\Arivanan\hospital-management-system\backend-python"
echo.
echo Starting server test (will timeout after 5 seconds)...
timeout /t 5 /nobreak | C:\Python313\python.exe comprehensive_server.py

echo.
echo 2. Checking Claude Desktop configuration...
set CONFIG_FILE=C:\Users\Arivanan\AppData\Roaming\Claude\claude_desktop_config.json
if exist "%CONFIG_FILE%" (
    echo ✓ Configuration file exists
    echo Contents:
    type "%CONFIG_FILE%"
) else (
    echo ✗ Configuration file missing at %CONFIG_FILE%
)

echo.
echo 3. Testing dependencies...
echo Checking required Python packages:
C:\Python313\python.exe -c "import mcp.server.fastmcp; print('✓ FastMCP available')" 2>&1
C:\Python313\python.exe -c "import sqlalchemy; print('✓ SQLAlchemy available')" 2>&1
C:\Python313\python.exe -c "from backend-python.database import User; print('✓ Database models available')" 2>&1

echo.
echo 4. Manual test instructions:
echo - Restart Claude Desktop completely
echo - Look for "hospital-management-system" in available servers
echo - Try asking: "test the hospital management connection"
echo.
pause
