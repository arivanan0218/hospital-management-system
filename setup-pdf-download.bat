@echo off
echo ================================
echo Hospital PDF Download Setup
echo ================================

echo.
echo 1. Installing frontend dependencies...
cd frontend
call npm install express cors concurrently

echo.
echo 2. Starting PDF server and frontend...
echo   - PDF Server: http://localhost:3000/reports/
echo   - Frontend: http://localhost:5173
echo.

start /B npm run pdf-server
timeout /t 2
start /B npm run dev

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo Services running:
echo   📁 PDF Server: http://localhost:3000
echo   🌐 Frontend: http://localhost:5173
echo.
echo The Discharge Reports tab now supports:
echo   ✅ PDF generation and download
echo   ✅ Local storage management
echo   ✅ File size tracking
echo   ✅ Automatic cleanup
echo.
echo To test the PDF download:
echo   1. Open http://localhost:5173
echo   2. Connect to hospital system
echo   3. Go to "Discharge Reports" tab
echo   4. Use bed ID: 64b05767-1b82-46e4-87e1-00f3615f1c00
echo   5. Generate and download PDF
echo.
pause
