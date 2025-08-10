# Check Deployment Status

Write-Host "Checking AWS Infrastructure Status..." -ForegroundColor Green
Write-Host "====================================="

$AWS_REGION = "us-east-1"

# Check RDS Database Status
Write-Host ""
Write-Host "RDS Database Status:" -ForegroundColor Yellow
try {
    $db_status = aws rds describe-db-instances --db-instance-identifier hospital-postgres --query 'DBInstances[0].DBInstanceStatus' --output text --region $AWS_REGION
    $db_endpoint = aws rds describe-db-instances --db-instance-identifier hospital-postgres --query 'DBInstances[0].Endpoint.Address' --output text --region $AWS_REGION
    
    if ($db_status -eq "available") {
        Write-Host "✅ Database Status: $db_status" -ForegroundColor Green
        Write-Host "✅ Database Endpoint: $db_endpoint" -ForegroundColor Green
    } else {
        Write-Host "⏳ Database Status: $db_status (still creating...)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Database not found or error occurred" -ForegroundColor Red
}

# Check ECR Repositories
Write-Host ""
Write-Host "ECR Repositories:" -ForegroundColor Yellow
try {
    $repos = aws ecr describe-repositories --query 'repositories[?contains(repositoryName, `hospital`)].repositoryName' --output text --region $AWS_REGION
    if ($repos) {
        Write-Host "✅ ECR Repositories: $repos" -ForegroundColor Green
    } else {
        Write-Host "❌ No hospital ECR repositories found" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error checking ECR repositories" -ForegroundColor Red
}

# Check ECS Cluster
Write-Host ""
Write-Host "ECS Cluster:" -ForegroundColor Yellow
try {
    $cluster_status = aws ecs describe-clusters --clusters hospital-cluster --query 'clusters[0].status' --output text --region $AWS_REGION
    if ($cluster_status -eq "ACTIVE") {
        Write-Host "✅ ECS Cluster: $cluster_status" -ForegroundColor Green
    } else {
        Write-Host "❌ ECS Cluster status: $cluster_status" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ ECS Cluster not found" -ForegroundColor Red
}

# Check Load Balancer
Write-Host ""
Write-Host "Application Load Balancer:" -ForegroundColor Yellow
try {
    $alb_dns = aws elbv2 describe-load-balancers --names hospital-alb --query 'LoadBalancers[0].DNSName' --output text --region $AWS_REGION
    $alb_state = aws elbv2 describe-load-balancers --names hospital-alb --query 'LoadBalancers[0].State.Code' --output text --region $AWS_REGION
    
    if ($alb_state -eq "active") {
        Write-Host "✅ Load Balancer: $alb_state" -ForegroundColor Green
        Write-Host "✅ Application URL: http://$alb_dns" -ForegroundColor Green
    } else {
        Write-Host "⏳ Load Balancer State: $alb_state" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Load Balancer not found" -ForegroundColor Red
}

# Check if ready for deployment
Write-Host ""
Write-Host "Deployment Readiness:" -ForegroundColor Cyan
if ($db_status -eq "available" -and $cluster_status -eq "ACTIVE" -and $alb_state -eq "active") {
    Write-Host "🎉 Infrastructure is ready for application deployment!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Build and push Docker images: run build-and-deploy.ps1"
    Write-Host "2. Create ECS services"
    Write-Host "3. Test your application"
} else {
    Write-Host "⏳ Infrastructure is still being created. Please wait and run this script again." -ForegroundColor Yellow
    if ($db_status -ne "available") {
        Write-Host "   - Database is still creating (this typically takes 5-10 minutes)"
    }
}
