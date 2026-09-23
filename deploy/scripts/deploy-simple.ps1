# Simple AWS Deployment Script - Step by Step

Write-Host "Hospital Management System - Simple AWS Setup" -ForegroundColor Green
Write-Host "================================================"

$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
$AWS_REGION = "us-east-1"

Write-Host "AWS Account ID: $ACCOUNT_ID" -ForegroundColor Green
Write-Host "AWS Region: $AWS_REGION" -ForegroundColor Green

# Step 1: Create ECR repositories
Write-Host ""
Write-Host "Step 1: Creating ECR repositories..." -ForegroundColor Yellow

try {
    aws ecr create-repository --repository-name hospital-backend --region $AWS_REGION
    Write-Host "Backend ECR repository created" -ForegroundColor Green
} catch {
    Write-Host "Backend ECR repository already exists" -ForegroundColor Yellow
}

try {
    aws ecr create-repository --repository-name hospital-frontend --region $AWS_REGION
    Write-Host "Frontend ECR repository created" -ForegroundColor Green
} catch {
    Write-Host "Frontend ECR repository already exists" -ForegroundColor Yellow
}

# Step 2: Create VPC and basic networking
Write-Host ""
Write-Host "Step 2: Creating VPC..." -ForegroundColor Yellow

$VPC_ID = aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query 'Vpc.VpcId' --output text --region $AWS_REGION
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames --region $AWS_REGION
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support --region $AWS_REGION
aws ec2 create-tags --resources $VPC_ID --tags Key=Name,Value=hospital-vpc --region $AWS_REGION

Write-Host "VPC created: $VPC_ID" -ForegroundColor Green

# Create Internet Gateway
$IGW_ID = aws ec2 create-internet-gateway --query 'InternetGateway.InternetGatewayId' --output text --region $AWS_REGION
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID --region $AWS_REGION
aws ec2 create-tags --resources $IGW_ID --tags Key=Name,Value=hospital-igw --region $AWS_REGION

Write-Host "Internet Gateway created: $IGW_ID" -ForegroundColor Green

# Create public subnets
$SUBNET1_ID = aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --availability-zone us-east-1a --query 'Subnet.SubnetId' --output text --region $AWS_REGION
$SUBNET2_ID = aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 --availability-zone us-east-1b --query 'Subnet.SubnetId' --output text --region $AWS_REGION

aws ec2 modify-subnet-attribute --subnet-id $SUBNET1_ID --map-public-ip-on-launch --region $AWS_REGION
aws ec2 modify-subnet-attribute --subnet-id $SUBNET2_ID --map-public-ip-on-launch --region $AWS_REGION

aws ec2 create-tags --resources $SUBNET1_ID --tags Key=Name,Value=hospital-public-1 --region $AWS_REGION
aws ec2 create-tags --resources $SUBNET2_ID --tags Key=Name,Value=hospital-public-2 --region $AWS_REGION

Write-Host "Subnets created: $SUBNET1_ID, $SUBNET2_ID" -ForegroundColor Green

# Create route table
$RT_ID = aws ec2 create-route-table --vpc-id $VPC_ID --query 'RouteTable.RouteTableId' --output text --region $AWS_REGION
aws ec2 create-route --route-table-id $RT_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID --region $AWS_REGION
aws ec2 associate-route-table --subnet-id $SUBNET1_ID --route-table-id $RT_ID --region $AWS_REGION
aws ec2 associate-route-table --subnet-id $SUBNET2_ID --route-table-id $RT_ID --region $AWS_REGION
aws ec2 create-tags --resources $RT_ID --tags Key=Name,Value=hospital-public-rt --region $AWS_REGION

Write-Host "Route table created and associated" -ForegroundColor Green

# Step 3: Create security groups
Write-Host ""
Write-Host "Step 3: Creating security groups..." -ForegroundColor Yellow

$ALB_SG = aws ec2 create-security-group --group-name hospital-alb-sg --description "Hospital ALB Security Group" --vpc-id $VPC_ID --query 'GroupId' --output text --region $AWS_REGION
aws ec2 authorize-security-group-ingress --group-id $ALB_SG --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $AWS_REGION
aws ec2 authorize-security-group-ingress --group-id $ALB_SG --protocol tcp --port 443 --cidr 0.0.0.0/0 --region $AWS_REGION

$BACKEND_SG = aws ec2 create-security-group --group-name hospital-backend-sg --description "Hospital Backend Security Group" --vpc-id $VPC_ID --query 'GroupId' --output text --region $AWS_REGION
aws ec2 authorize-security-group-ingress --group-id $BACKEND_SG --protocol tcp --port 8000 --source-group $ALB_SG --region $AWS_REGION

$FRONTEND_SG = aws ec2 create-security-group --group-name hospital-frontend-sg --description "Hospital Frontend Security Group" --vpc-id $VPC_ID --query 'GroupId' --output text --region $AWS_REGION
aws ec2 authorize-security-group-ingress --group-id $FRONTEND_SG --protocol tcp --port 3000 --source-group $ALB_SG --region $AWS_REGION

$DB_SG = aws ec2 create-security-group --group-name hospital-db-sg --description "Hospital Database Security Group" --vpc-id $VPC_ID --query 'GroupId' --output text --region $AWS_REGION
aws ec2 authorize-security-group-ingress --group-id $DB_SG --protocol tcp --port 5432 --source-group $BACKEND_SG --region $AWS_REGION

Write-Host "Security groups created" -ForegroundColor Green

# Step 4: Create RDS subnet group and database
Write-Host ""
Write-Host "Step 4: Creating RDS database..." -ForegroundColor Yellow

aws rds create-db-subnet-group --db-subnet-group-name hospital-db-subnet-group --db-subnet-group-description "Hospital DB Subnet Group" --subnet-ids $SUBNET1_ID $SUBNET2_ID --region $AWS_REGION

aws rds create-db-instance `
    --db-instance-identifier hospital-postgres `
    --db-instance-class db.t3.micro `
    --engine postgres `
    --master-username postgres `
    --master-user-password HospitalSecure123! `
    --allocated-storage 20 `
    --db-name hospital_management `
    --vpc-security-group-ids $DB_SG `
    --db-subnet-group-name hospital-db-subnet-group `
    --backup-retention-period 7 `
    --no-deletion-protection `
    --region $AWS_REGION

Write-Host "RDS database creation started (this will take 5-10 minutes)" -ForegroundColor Green

# Step 5: Create ECS cluster
Write-Host ""
Write-Host "Step 5: Creating ECS cluster..." -ForegroundColor Yellow

aws ecs create-cluster --cluster-name hospital-cluster --region $AWS_REGION
Write-Host "ECS cluster created" -ForegroundColor Green

# Step 6: Create CloudWatch log groups
Write-Host ""
Write-Host "Step 6: Creating CloudWatch log groups..." -ForegroundColor Yellow

try { aws logs create-log-group --log-group-name "/ecs/hospital-backend" --region $AWS_REGION } catch { }
try { aws logs create-log-group --log-group-name "/ecs/hospital-frontend" --region $AWS_REGION } catch { }

Write-Host "CloudWatch log groups created" -ForegroundColor Green

# Step 7: Create Application Load Balancer
Write-Host ""
Write-Host "Step 7: Creating Application Load Balancer..." -ForegroundColor Yellow

$ALB_ARN = aws elbv2 create-load-balancer `
    --name hospital-alb `
    --subnets $SUBNET1_ID $SUBNET2_ID `
    --security-groups $ALB_SG `
    --scheme internet-facing `
    --type application `
    --ip-address-type ipv4 `
    --query 'LoadBalancers[0].LoadBalancerArn' `
    --output text `
    --region $AWS_REGION

$ALB_DNS = aws elbv2 describe-load-balancers --load-balancer-arns $ALB_ARN --query 'LoadBalancers[0].DNSName' --output text --region $AWS_REGION

Write-Host "Application Load Balancer created: $ALB_DNS" -ForegroundColor Green

# Create target groups
$BACKEND_TG_ARN = aws elbv2 create-target-group `
    --name hospital-backend-tg `
    --protocol HTTP `
    --port 8000 `
    --vpc-id $VPC_ID `
    --target-type ip `
    --health-check-path /health `
    --query 'TargetGroups[0].TargetGroupArn' `
    --output text `
    --region $AWS_REGION

$FRONTEND_TG_ARN = aws elbv2 create-target-group `
    --name hospital-frontend-tg `
    --protocol HTTP `
    --port 3000 `
    --vpc-id $VPC_ID `
    --target-type ip `
    --query 'TargetGroups[0].TargetGroupArn' `
    --output text `
    --region $AWS_REGION

Write-Host "Target groups created" -ForegroundColor Green

# Create listeners
$LISTENER_ARN = aws elbv2 create-listener `
    --load-balancer-arn $ALB_ARN `
    --protocol HTTP `
    --port 80 `
    --default-actions Type=forward,TargetGroupArn=$FRONTEND_TG_ARN `
    --query 'Listeners[0].ListenerArn' `
    --output text `
    --region $AWS_REGION

aws elbv2 create-rule `
    --listener-arn $LISTENER_ARN `
    --priority 1 `
    --conditions Field=path-pattern,Values="/api/*" `
    --actions Type=forward,TargetGroupArn=$BACKEND_TG_ARN `
    --region $AWS_REGION

Write-Host "ALB listeners configured" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Infrastructure Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Key Information:" -ForegroundColor Yellow
Write-Host "- VPC ID: $VPC_ID"
Write-Host "- Subnet 1: $SUBNET1_ID"
Write-Host "- Subnet 2: $SUBNET2_ID"
Write-Host "- ALB Security Group: $ALB_SG"
Write-Host "- Backend Security Group: $BACKEND_SG"
Write-Host "- Frontend Security Group: $FRONTEND_SG"
Write-Host "- Database Security Group: $DB_SG"
Write-Host "- Application URL: http://$ALB_DNS"
Write-Host "- Backend Target Group: $BACKEND_TG_ARN"
Write-Host "- Frontend Target Group: $FRONTEND_TG_ARN"
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Wait for RDS database to be available (5-10 minutes)"
Write-Host "2. Update task definitions with actual values"
Write-Host "3. Build and push Docker images to ECR"
Write-Host "4. Create ECS services"
Write-Host ""
Write-Host "Run check-deployment-status.ps1 to monitor progress"
