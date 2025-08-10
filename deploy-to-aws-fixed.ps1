# AWS Deployment Script for Hospital Management System (PowerShell)

Write-Host "Hospital Management System - AWS Deployment" -ForegroundColor Green
Write-Host "============================================"

# Check if AWS CLI is installed
if (!(Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "AWS CLI is not installed. Please install it first." -ForegroundColor Red
    Write-Host "Visit: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html"
    exit 1
}

# Check if user is logged into AWS
try {
    aws sts get-caller-identity | Out-Null
} catch {
    Write-Host "You are not authenticated with AWS. Please run 'aws configure' first." -ForegroundColor Red
    exit 1
}

# Get AWS Account ID
$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
$AWS_REGION = "us-east-1"

Write-Host "AWS Account ID: $ACCOUNT_ID" -ForegroundColor Green
Write-Host "AWS Region: $AWS_REGION" -ForegroundColor Green

# Step 1: Create CloudFormation Stack
Write-Host ""
Write-Host "Step 1: Creating AWS Infrastructure..." -ForegroundColor Yellow
aws cloudformation deploy `
    --template-file aws-infrastructure.yml `
    --stack-name hospital-infrastructure `
    --parameter-overrides `
        VpcCIDR=10.0.0.0/16 `
        PublicSubnet1CIDR=10.0.1.0/24 `
        PublicSubnet2CIDR=10.0.2.0/24 `
    --capabilities CAPABILITY_IAM `
    --region $AWS_REGION

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to create infrastructure. Please check the error above." -ForegroundColor Red
    exit 1
}

Write-Host "Infrastructure created successfully!" -ForegroundColor Green

# Step 2: Create database password in SSM Parameter Store
Write-Host ""
Write-Host "Step 2: Setting up database password..." -ForegroundColor Yellow
aws ssm put-parameter `
    --name "/hospital/database/password" `
    --value "HospitalSecure123!" `
    --type "SecureString" `
    --overwrite `
    --region $AWS_REGION

Write-Host "Database password stored in SSM Parameter Store" -ForegroundColor Green

# Step 3: Get RDS endpoint
Write-Host ""
Write-Host "Step 3: Getting database endpoint..." -ForegroundColor Yellow
$DB_ENDPOINT = aws cloudformation describe-stacks `
    --stack-name hospital-infrastructure `
    --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' `
    --output text `
    --region $AWS_REGION

Write-Host "Database endpoint: $DB_ENDPOINT" -ForegroundColor Green

# Step 4: Get ALB DNS name
$ALB_DNS = aws cloudformation describe-stacks `
    --stack-name hospital-infrastructure `
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' `
    --output text `
    --region $AWS_REGION

Write-Host "Load balancer DNS: $ALB_DNS" -ForegroundColor Green

# Step 5: Update task definitions with actual values
Write-Host ""
Write-Host "Step 5: Updating task definitions..." -ForegroundColor Yellow

# Update backend task definition
(Get-Content backend-task-definition.json) -replace 'ACCOUNT_ID', $ACCOUNT_ID | Set-Content backend-task-definition.json
(Get-Content backend-task-definition.json) -replace 'RDS_ENDPOINT', $DB_ENDPOINT | Set-Content backend-task-definition.json
(Get-Content backend-task-definition.json) -replace 'PASSWORD', 'HospitalSecure123!' | Set-Content backend-task-definition.json

# Update frontend task definition
(Get-Content frontend-task-definition.json) -replace 'ACCOUNT_ID', $ACCOUNT_ID | Set-Content frontend-task-definition.json
(Get-Content frontend-task-definition.json) -replace 'ALB_DNS_NAME', $ALB_DNS | Set-Content frontend-task-definition.json

Write-Host "Task definitions updated" -ForegroundColor Green

# Step 6: Create CloudWatch Log Groups
Write-Host ""
Write-Host "Step 6: Creating CloudWatch log groups..." -ForegroundColor Yellow
try { aws logs create-log-group --log-group-name "/ecs/hospital-backend" --region $AWS_REGION } catch { Write-Host "Backend log group already exists" }
try { aws logs create-log-group --log-group-name "/ecs/hospital-frontend" --region $AWS_REGION } catch { Write-Host "Frontend log group already exists" }

Write-Host "CloudWatch log groups created" -ForegroundColor Green

Write-Host ""
Write-Host "Initial setup completed!" -ForegroundColor Green
Write-Host "Your application will be available at: http://$ALB_DNS" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Push your code to GitHub"
Write-Host "2. Set up GitHub secrets for CI/CD"
Write-Host "3. GitHub Actions will build and deploy automatically"
Write-Host ""
Write-Host "GitHub Secrets to add:" -ForegroundColor Yellow
Write-Host "- AWS_ACCESS_KEY_ID"
Write-Host "- AWS_SECRET_ACCESS_KEY"
