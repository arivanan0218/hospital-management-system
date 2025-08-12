@echo off
REM Install script for Hospital Management System (Windows)

echo 🏥 Hospital Management System - Installing Dependencies
echo =======================================================

REM Navigate to backend-python directory
cd backend-python

echo 📦 Installing Python dependencies...
REM Install using pip
pip install -e .

echo 📝 Installing additional PDF dependencies...
REM Ensure reportlab and markdown2 are installed
pip install reportlab>=4.0.0 markdown2>=2.4.0

echo ✅ Backend dependencies installed!

REM Navigate to frontend directory
cd ../frontend

echo 📦 Installing Frontend dependencies...
npm install

echo ✅ Frontend dependencies installed!

echo.
echo 🚀 To start the system:
echo 1. Backend: cd backend-python && python comprehensive_server.py
echo 2. Process Manager: cd mcp-process-manager && node server.js
echo 3. Frontend: cd frontend && npm run dev
echo.
echo 🎯 All dependencies are now installed!

pause
