#!/usr/bin/env pwsh
# ================================
# Fix Permissions Deployment Script
# ================================

Write-Host "🔧 Hospital Management System - Permission Fix Deployment" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Function to test deployment locally
function Test-LocalDeployment {
    Write-Host "🧪 Testing Local Deployment..." -ForegroundColor Yellow
    
    # Stop any existing containers
    Write-Host "Stopping existing containers..." -ForegroundColor Gray
    docker-compose -f docker-compose.simple.yml down -v
    
    # Remove old images to force rebuild
    Write-Host "Cleaning old images..." -ForegroundColor Gray
    docker image prune -f
    docker rmi hospital-management-system-backend 2>$null
    
    # Build and start with fixed configuration
    Write-Host "Building with permission fixes..." -ForegroundColor Yellow
    docker-compose -f docker-compose.simple.yml up --build -d
    
    # Wait for services to start
    Write-Host "Waiting for services to initialize..." -ForegroundColor Gray
    Start-Sleep -Seconds 30
    
    # Test the API health
    Write-Host "Testing backend health..." -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
        Write-Host "✅ Backend is healthy: $($response.status)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Check container logs for permission errors
    Write-Host "Checking for permission errors..." -ForegroundColor Yellow
    $logs = docker logs hospital_backend 2>&1
    if ($logs -match "Permission denied") {
        Write-Host "❌ Permission errors still found in logs" -ForegroundColor Red
        Write-Host $logs -ForegroundColor Gray
    } else {
        Write-Host "✅ No permission errors found" -ForegroundColor Green
    }
    
    # Show ChromaDB status
    if ($logs -match "ChromaDB directory writable") {
        Write-Host "✅ ChromaDB initialization successful" -ForegroundColor Green
    } else {
        Write-Host "⚠️ ChromaDB initialization may have issues" -ForegroundColor Yellow
    }
}

# Function to deploy to AWS with fixes
function Deploy-ToAWS {
    Write-Host "☁️ Deploying to AWS with permission fixes..." -ForegroundColor Yellow
    
    # Update task definition with new image
    Write-Host "Updating ECS task definition..." -ForegroundColor Gray
    
    # Build and push new image
    $ECR_REPO = "hospital-backend"
    $AWS_REGION = "us-east-1"
    $AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
    
    if (-not $AWS_ACCOUNT_ID) {
        Write-Host "❌ AWS credentials not configured" -ForegroundColor Red
        return
    }
    
    # Login to ECR
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
    
    # Build and tag image
    docker build -t $ECR_REPO ./backend-python/
    docker tag "$ECR_REPO:latest" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest"
    
    # Push image
    docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest"
    
    # Update task definition
    $taskDefJson = Get-Content "backend-task-definition.json" | ConvertFrom-Json
    $taskDefJson.containerDefinitions[0].image = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest"
    $taskDefJson | ConvertTo-Json -Depth 10 | Set-Content "backend-task-definition-updated.json"
    
    # Register new task definition
    aws ecs register-task-definition --cli-input-json file://backend-task-definition-updated.json
    
    # Update service
    aws ecs update-service --cluster hospital-cluster --service hospital-backend-service --force-new-deployment
    
    Write-Host "✅ AWS deployment initiated with permission fixes" -ForegroundColor Green
}

# Function to show diagnostic information
function Show-DiagnosticInfo {
    Write-Host "📊 Diagnostic Information" -ForegroundColor Cyan
    Write-Host "=========================" -ForegroundColor Cyan
    
    Write-Host "Fixed Issues:" -ForegroundColor Yellow
    Write-Host "✅ Added appuser home directory permissions" -ForegroundColor Green
    Write-Host "✅ Added medical_knowledge_db volume mounts" -ForegroundColor Green
    Write-Host "✅ Enhanced Docker detection in AI agent" -ForegroundColor Green
    Write-Host "✅ Added /tmp fallback paths for ChromaDB" -ForegroundColor Green
    Write-Host "✅ Updated ECS task definition with mount points" -ForegroundColor Green
    
    Write-Host "`nDeployment Options:" -ForegroundColor Yellow
    Write-Host "1. Test locally with: docker-compose -f docker-compose.simple.yml up --build" -ForegroundColor Gray
    Write-Host "2. Deploy to AWS with updated configurations" -ForegroundColor Gray
    Write-Host "3. Use this script for automated testing and deployment" -ForegroundColor Gray
}

# Main menu
$choice = Read-Host @"

Choose deployment option:
1. Test local deployment with fixes
2. Deploy to AWS with fixes
3. Show diagnostic information only
Enter choice (1-3)
"@

switch ($choice) {
    "1" { Test-LocalDeployment }
    "2" { Deploy-ToAWS }
    "3" { Show-DiagnosticInfo }
    default { 
        Show-DiagnosticInfo
        Write-Host "Invalid choice. Showing diagnostic info." -ForegroundColor Yellow
    }
}

Write-Host "`n🎯 Deployment script completed!" -ForegroundColor Cyan
