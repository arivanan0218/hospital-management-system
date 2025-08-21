#!/usr/bin/env pwsh
# PowerShell script to fix PDF deployment issues
# Run this on your local machine to rebuild and redeploy

Write-Host "Hospital Management System - PDF Deployment Fix" -ForegroundColor Green
Write-Host "=================================================="

Write-Host "Current Docker images:" -ForegroundColor Cyan
docker images | findstr hospital

Write-Host ""
Write-Host "Rebuilding backend with PDF dependencies..." -ForegroundColor Yellow
Set-Location "backend-python"

# Rebuild Docker image with --no-cache to ensure fresh dependencies
Write-Host "Building fresh Docker image with reportlab..." -ForegroundColor Yellow
docker build --no-cache -t hospital-backend:latest .

# Tag for ECR
Write-Host "Tagging for ECR..." -ForegroundColor Yellow
$ECR_REPO = "135878023409.dkr.ecr.us-east-1.amazonaws.com/hospital-backend"
docker tag hospital-backend:latest "${ECR_REPO}:latest"

Write-Host ""
Write-Host "Ready to push to ECR. Run these commands to deploy:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Login to ECR:" -ForegroundColor White
Write-Host "   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 135878023409.dkr.ecr.us-east-1.amazonaws.com" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Push new image:" -ForegroundColor White
Write-Host "   docker push ${ECR_REPO}:latest" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Restart EC2 containers:" -ForegroundColor White
Write-Host "   SSH to your EC2 instance and run:" -ForegroundColor Gray
Write-Host "   docker stop hospital-backend" -ForegroundColor Gray
Write-Host "   docker pull ${ECR_REPO}:latest" -ForegroundColor Gray
Write-Host "   docker-compose up -d" -ForegroundColor Gray

Write-Host ""
Write-Host "Testing local Docker image..." -ForegroundColor Cyan

# Test the newly built image locally
Write-Host "Starting test container..." -ForegroundColor Yellow
$containerID = docker run -d --name test-backend-pdf -p 8001:8000 hospital-backend:latest

Start-Sleep -Seconds 10

Write-Host "Testing PDF dependencies in container..." -ForegroundColor Yellow
docker exec $containerID python -c "
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    import markdown2
    print('All PDF dependencies available!')
    print('reportlab imported successfully')
    print('markdown2 imported successfully')
except ImportError as e:
    print('Missing dependency:', e)
    exit(1)
"

Write-Host "Cleaning up test container..." -ForegroundColor Yellow
docker stop $containerID
docker rm $containerID

Write-Host ""
Write-Host "Local Docker image built successfully with PDF support!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "   1. Push the image to ECR using commands above"
Write-Host "   2. SSH to EC2 and restart containers with new image"
Write-Host "   3. Test PDF download in deployed web interface"
