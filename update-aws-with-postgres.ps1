# Update AWS ECS Task Definition to Include PostgreSQL
Write-Host "Updating AWS ECS Task Definition to include PostgreSQL..." -ForegroundColor Cyan

try {
    # Check if AWS CLI is configured
    $awsIdentity = aws sts get-caller-identity 2>$null | ConvertFrom-Json
    if (-not $awsIdentity) {
        Write-Host "❌ AWS CLI not configured. Please run 'aws configure' first." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ AWS Identity: $($awsIdentity.Arn)" -ForegroundColor Green
    
    # Register the new task definition with PostgreSQL
    Write-Host "`nRegistering updated task definition with PostgreSQL..." -ForegroundColor Yellow
    $taskDefResult = aws ecs register-task-definition --cli-input-json file://aws-task-definition-with-postgres.json 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Task definition registered successfully" -ForegroundColor Green
        
        # Update the ECS service to use the new task definition
        Write-Host "`nUpdating ECS service..." -ForegroundColor Yellow
        $serviceResult = aws ecs update-service --cluster hospital-cluster --service hospital-service --task-definition hospital-task-definition 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ ECS service updated successfully" -ForegroundColor Green
            Write-Host "`n🎉 PostgreSQL has been added to the AWS deployment!" -ForegroundColor Green
            Write-Host "⏳ The service will take a few minutes to redeploy with the database..." -ForegroundColor Yellow
            Write-Host "`n📊 You can monitor the deployment status at:" -ForegroundColor Cyan
            Write-Host "https://console.aws.amazon.com/ecs/home?region=us-east-1#/clusters/hospital-cluster/services" -ForegroundColor Blue
        } else {
            Write-Host "❌ Failed to update ECS service:" -ForegroundColor Red
            Write-Host $serviceResult -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Failed to register task definition:" -ForegroundColor Red
        Write-Host $taskDefResult -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
