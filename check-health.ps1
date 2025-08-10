# Hospital Management System - Health Check Script

Write-Host "🏥 Hospital Management System - Health Check" -ForegroundColor Green
Write-Host "============================================"

# Check AWS CLI
Write-Host ""
Write-Host "🔍 Checking AWS CLI..." -ForegroundColor Yellow
if (Get-Command aws -ErrorAction SilentlyContinue) {
    $awsVersion = aws --version
    Write-Host "✅ AWS CLI installed: $awsVersion" -ForegroundColor Green
} else {
    Write-Host "❌ AWS CLI not found" -ForegroundColor Red
    exit 1
}

# Check AWS Authentication
Write-Host ""
Write-Host "🔍 Checking AWS Authentication..." -ForegroundColor Yellow
try {
    $identity = aws sts get-caller-identity --output json | ConvertFrom-Json
    Write-Host "✅ AWS Account: $($identity.Account)" -ForegroundColor Green
    Write-Host "✅ User/Role: $($identity.Arn)" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS not configured. Run 'aws configure'" -ForegroundColor Red
    exit 1
}

# Check CloudFormation Stack
Write-Host ""
Write-Host "🔍 Checking Infrastructure..." -ForegroundColor Yellow
try {
    $stack = aws cloudformation describe-stacks --stack-name hospital-infrastructure --output json | ConvertFrom-Json
    $status = $stack.Stacks[0].StackStatus
    if ($status -eq "CREATE_COMPLETE" -or $status -eq "UPDATE_COMPLETE") {
        Write-Host "✅ Infrastructure Status: $status" -ForegroundColor Green
        
        # Get outputs
        foreach ($output in $stack.Stacks[0].Outputs) {
            if ($output.OutputKey -eq "LoadBalancerDNS") {
                $albDns = $output.OutputValue
                Write-Host "✅ Application URL: http://$albDns" -ForegroundColor Green
            }
            if ($output.OutputKey -eq "DatabaseEndpoint") {
                Write-Host "✅ Database: $($output.OutputValue)" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "⚠️ Infrastructure Status: $status" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Infrastructure not found. Run deployment script first." -ForegroundColor Red
}

# Check ECS Services
Write-Host ""
Write-Host "🔍 Checking ECS Services..." -ForegroundColor Yellow
try {
    $services = aws ecs describe-services --cluster hospital-cluster --services hospital-backend-service hospital-frontend-service --output json | ConvertFrom-Json
    
    foreach ($service in $services.services) {
        $name = $service.serviceName
        $status = $service.status
        $running = $service.runningCount
        $desired = $service.desiredCount
        
        if ($status -eq "ACTIVE" -and $running -eq $desired) {
            Write-Host "✅ $name : $status ($running/$desired tasks)" -ForegroundColor Green
        } else {
            Write-Host "⚠️ $name : $status ($running/$desired tasks)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "❌ ECS services not found" -ForegroundColor Red
}

# Check ECR Repositories
Write-Host ""
Write-Host "🔍 Checking ECR Repositories..." -ForegroundColor Yellow
try {
    $repos = aws ecr describe-repositories --output json | ConvertFrom-Json
    $hospitalRepos = $repos.repositories | Where-Object { $_.repositoryName -like "*hospital*" }
    
    foreach ($repo in $hospitalRepos) {
        Write-Host "✅ ECR Repository: $($repo.repositoryName)" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ ECR repositories not found" -ForegroundColor Red
}

# Test Application Health (if ALB DNS is available)
if ($albDns) {
    Write-Host ""
    Write-Host "🔍 Testing Application Health..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://$albDns/health" -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Application health check passed" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Application health check returned: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ Application not responding yet (may still be starting)" -ForegroundColor Yellow
    }
}

# Summary
Write-Host ""
Write-Host "📊 Health Check Summary" -ForegroundColor Cyan
Write-Host "======================"
Write-Host "If all items show ✅, your system is ready!"
Write-Host "If you see ⚠️ or ❌, check the AWS console for details."
Write-Host ""
if ($albDns) {
    Write-Host "🌐 Your application: http://$albDns" -ForegroundColor Cyan
}
Write-Host "📱 AWS Console: https://console.aws.amazon.com/" -ForegroundColor Cyan
Write-Host "📋 ECS Console: https://console.aws.amazon.com/ecs/" -ForegroundColor Cyan
Write-Host "📊 CloudWatch: https://console.aws.amazon.com/cloudwatch/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
