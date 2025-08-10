# Hospital Management System - Quick Start Script for Windows
# Run this in PowerShell

Write-Host "🏥 Hospital Management System - Quick Start" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} else {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop:" -ForegroundColor Red
    Write-Host "   https://www.docker.com/products/docker-desktop/"
    exit 1
}

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop" -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (Test-Path ".env") {
    Write-Host "✅ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "📝 Please edit .env file with your API keys before running docker-compose up" -ForegroundColor Yellow
    Write-Host "   Required: GEMINI_API_KEY" -ForegroundColor Yellow
    Write-Host "   Optional: Other AI API keys" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter after you've updated the .env file"
}

Write-Host ""
Write-Host "🚀 Starting Hospital Management System..." -ForegroundColor Cyan

# Start the application
docker-compose up -d

# Wait a moment for services to start
Start-Sleep -Seconds 10

# Check if services are running
Write-Host ""
Write-Host "📊 Service Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "🌐 Application URLs:" -ForegroundColor Green
Write-Host "   Frontend: http://localhost" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   Health Check: http://localhost:8000/health" -ForegroundColor White

Write-Host ""
Write-Host "📋 Useful Commands:" -ForegroundColor Cyan
Write-Host "   View logs: docker-compose logs -f" -ForegroundColor White
Write-Host "   Stop services: docker-compose down" -ForegroundColor White
Write-Host "   Restart services: docker-compose restart" -ForegroundColor White

Write-Host ""
Write-Host "✅ Quick start complete! Your hospital management system is running." -ForegroundColor Green
