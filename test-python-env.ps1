# Test Python and Database in AWS Environment
Write-Host "Testing Python Environment in AWS..." -ForegroundColor Cyan

try {
    Write-Host "Checking if we can access the backend environment..." -ForegroundColor Yellow
    
    # Try to test Python execution through the MCP manager
    $testData = @{
        "testType" = "python"
        "command" = "python -c `"import sys; print('Python Version:', sys.version); print('Working Directory:', __import__('os').getcwd())`""
    }
    
    $testResponse = Invoke-RestMethod -Uri "http://hospital-alb-1667599615.us-east-1.elb.amazonaws.com:3001/test" -Method POST -Body ($testData | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 15
    Write-Host "Python Test Response:" -ForegroundColor Green
    Write-Host $testResponse
} catch {
    Write-Host "Python test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nTesting database environment variables..." -ForegroundColor Yellow
try {
    $envData = @{
        "testType" = "env"
        "command" = "python -c `"import os; print('DATABASE_URL:', os.getenv('DATABASE_URL', 'Not Set')); print('AWS_EXECUTION_ENV:', os.getenv('AWS_EXECUTION_ENV', 'Not Set')); print('POSTGRES_DB:', os.getenv('POSTGRES_DB', 'Not Set'))`""
    }
    
    $envResponse = Invoke-RestMethod -Uri "http://hospital-alb-1667599615.us-east-1.elb.amazonaws.com:3001/test" -Method POST -Body ($envData | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 15
    Write-Host "Environment Test Response:" -ForegroundColor Green
    Write-Host $envResponse
} catch {
    Write-Host "Environment test failed: $($_.Exception.Message)" -ForegroundColor Red
}
