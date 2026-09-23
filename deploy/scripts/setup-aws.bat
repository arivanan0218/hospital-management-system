@echo off
echo.
echo ================================================
echo    Hospital Management System - Quick Setup
echo ================================================
echo.

REM Check if AWS CLI is installed
aws --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] AWS CLI is not installed!
    echo Please install AWS CLI from: https://awscli.amazonaws.com/AWSCLIV2.msi
    echo Then run this script again.
    pause
    exit /b 1
)

REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    echo Then run this script again.
    pause
    exit /b 1
)

echo [INFO] All prerequisites are installed!
echo.

REM Check if AWS is configured
aws sts get-caller-identity >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] AWS CLI is not configured!
    echo Please run: aws configure
    echo You'll need your AWS Access Key ID and Secret Access Key
    echo.
    echo Do you want to configure AWS now? (y/n)
    set /p choice=
    if /i "%choice%"=="y" (
        aws configure
    ) else (
        echo Please configure AWS and run this script again.
        pause
        exit /b 1
    )
)

echo [INFO] AWS is configured!
echo.

REM Get current directory
set CURRENT_DIR=%cd%

REM Check if we're in the right directory
if not exist "docker-compose.simple.yml" (
    echo [ERROR] Please run this script from the hospital-management-system directory
    echo Current directory: %CURRENT_DIR%
    pause
    exit /b 1
)

echo [INFO] Starting deployment process...
echo.

REM Run the PowerShell deployment script
powershell -ExecutionPolicy Bypass -File "deploy-to-aws.ps1"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Deployment failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ================================================
echo           Deployment Completed!
echo ================================================
echo.
echo Next steps:
echo 1. Push your code to GitHub
echo 2. Set up GitHub secrets (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
echo 3. GitHub Actions will handle automatic deployments
echo.
echo Check the AWS-DEPLOYMENT-GUIDE.md for detailed instructions.
echo.
pause
