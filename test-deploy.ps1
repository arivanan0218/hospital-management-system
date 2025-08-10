# Test Deployment - Create simple ECS services

Write-Host "Creating ECS Services for Testing..." -ForegroundColor Green
Write-Host "===================================="

$ACCOUNT_ID = "324037286635"
$AWS_REGION = "us-east-1"
$VPC_ID = "vpc-02b9cb42b900c1742"
$SUBNET1 = "subnet-07c708f6f5f6e4b8b"
$SUBNET2 = "subnet-0a03f0b465b06b5ff"

# Create a security group for ECS tasks
Write-Host "Creating security group..." -ForegroundColor Yellow
try {
    $SG_ID = aws ec2 create-security-group --group-name hospital-ecs-sg --description "Hospital ECS Security Group" --vpc-id $VPC_ID --query 'GroupId' --output text --region $AWS_REGION
    
    # Allow HTTP traffic
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8000 --cidr 0.0.0.0/0 --region $AWS_REGION
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 3000 --cidr 0.0.0.0/0 --region $AWS_REGION
    
    Write-Host "Security group created: $SG_ID" -ForegroundColor Green
} catch {
    # Get existing security group
    $SG_ID = aws ec2 describe-security-groups --filters "Name=group-name,Values=hospital-ecs-sg" --query 'SecurityGroups[0].GroupId' --output text --region $AWS_REGION
    Write-Host "Using existing security group: $SG_ID" -ForegroundColor Yellow
}

# Create simple task definition for backend
$BACKEND_TASK_DEF = @"
{
  "family": "hospital-backend-simple",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::$ACCOUNT_ID:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "hospital-backend",
      "image": "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "sqlite:///./hospital.db"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/hospital-backend",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
"@

$BACKEND_TASK_DEF | Out-File -FilePath "backend-simple-task.json" -Encoding utf8

# Create simple task definition for frontend  
$FRONTEND_TASK_DEF = @"
{
  "family": "hospital-frontend-simple",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::$ACCOUNT_ID:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "hospital-frontend",
      "image": "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-frontend:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/hospital-frontend",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
"@

$FRONTEND_TASK_DEF | Out-File -FilePath "frontend-simple-task.json" -Encoding utf8

# Register task definitions
Write-Host "Registering task definitions..." -ForegroundColor Yellow
aws ecs register-task-definition --cli-input-json file://backend-simple-task.json --region $AWS_REGION
aws ecs register-task-definition --cli-input-json file://frontend-simple-task.json --region $AWS_REGION

Write-Host "Task definitions registered" -ForegroundColor Green

# Create ECS services
Write-Host "Creating ECS services..." -ForegroundColor Yellow

# Backend service
aws ecs create-service `
    --cluster hospital-cluster `
    --service-name hospital-backend-simple `
    --task-definition hospital-backend-simple `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET1,$SUBNET2],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" `
    --region $AWS_REGION

# Frontend service  
aws ecs create-service `
    --cluster hospital-cluster `
    --service-name hospital-frontend-simple `
    --task-definition hospital-frontend-simple `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET1,$SUBNET2],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" `
    --region $AWS_REGION

Write-Host "ECS services created" -ForegroundColor Green

# Wait a moment and check service status
Write-Host ""
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Get service information
$BACKEND_SERVICE = aws ecs describe-services --cluster hospital-cluster --services hospital-backend-simple --query 'services[0]' --output json --region $AWS_REGION | ConvertFrom-Json
$FRONTEND_SERVICE = aws ecs describe-services --cluster hospital-cluster --services hospital-frontend-simple --query 'services[0]' --output json --region $AWS_REGION | ConvertFrom-Json

Write-Host ""
Write-Host "Service Status:" -ForegroundColor Cyan
Write-Host "Backend: $($BACKEND_SERVICE.status) - Running: $($BACKEND_SERVICE.runningCount)/$($BACKEND_SERVICE.desiredCount)"
Write-Host "Frontend: $($FRONTEND_SERVICE.status) - Running: $($FRONTEND_SERVICE.runningCount)/$($FRONTEND_SERVICE.desiredCount)"

# Get task public IPs
if ($BACKEND_SERVICE.runningCount -gt 0) {
    $BACKEND_TASKS = aws ecs list-tasks --cluster hospital-cluster --service-name hospital-backend-simple --query 'taskArns' --output text --region $AWS_REGION
    if ($BACKEND_TASKS) {
        $BACKEND_TASK_DETAILS = aws ecs describe-tasks --cluster hospital-cluster --tasks $BACKEND_TASKS --query 'tasks[0]' --output json --region $AWS_REGION | ConvertFrom-Json
        $BACKEND_ENI = $BACKEND_TASK_DETAILS.attachments[0].details | Where-Object { $_.name -eq "networkInterfaceId" } | Select-Object -ExpandProperty value
        $BACKEND_IP = aws ec2 describe-network-interfaces --network-interface-ids $BACKEND_ENI --query 'NetworkInterfaces[0].Association.PublicIp' --output text --region $AWS_REGION
        
        Write-Host ""
        Write-Host "Backend available at: http://${BACKEND_IP}:8000" -ForegroundColor Green
        Write-Host "Backend health check: http://${BACKEND_IP}:8000/health" -ForegroundColor Green
    }
}

if ($FRONTEND_SERVICE.runningCount -gt 0) {
    $FRONTEND_TASKS = aws ecs list-tasks --cluster hospital-cluster --service-name hospital-frontend-simple --query 'taskArns' --output text --region $AWS_REGION
    if ($FRONTEND_TASKS) {
        $FRONTEND_TASK_DETAILS = aws ecs describe-tasks --cluster hospital-cluster --tasks $FRONTEND_TASKS --query 'tasks[0]' --output json --region $AWS_REGION | ConvertFrom-Json
        $FRONTEND_ENI = $FRONTEND_TASK_DETAILS.attachments[0].details | Where-Object { $_.name -eq "networkInterfaceId" } | Select-Object -ExpandProperty value
        $FRONTEND_IP = aws ec2 describe-network-interfaces --network-interface-ids $FRONTEND_ENI --query 'NetworkInterfaces[0].Association.PublicIp' --output text --region $AWS_REGION
        
        Write-Host "Frontend available at: http://${FRONTEND_IP}:3000" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your Hospital Management System is now running on AWS!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test the URLs above"
Write-Host "2. Check CloudWatch logs if needed"
Write-Host "3. Set up GitHub for CI/CD (push code and add secrets)"
Write-Host "4. Set up a proper database (RDS) for production"

# Clean up temporary files
Remove-Item "backend-simple-task.json" -ErrorAction SilentlyContinue
Remove-Item "frontend-simple-task.json" -ErrorAction SilentlyContinue
