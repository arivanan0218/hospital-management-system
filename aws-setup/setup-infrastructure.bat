@echo off
REM Hospital Management System AWS Infrastructure Setup for Windows
REM This script creates the necessary AWS resources for deployment

echo 🚀 Setting up AWS infrastructure for Hospital Management System...

REM Configuration
set AWS_REGION=us-east-1
set CLUSTER_NAME=hospital-cluster
set SERVICE_NAME=hospital-management-service
set TASK_DEFINITION_NAME=hospital-task-definition
set ECR_BACKEND_REPO=hospital-backend
set ECR_FRONTEND_REPO=hospital-frontend
set ECR_MCP_REPO=hospital-mcp-manager
set VPC_NAME=hospital-vpc
set SUBNET_PREFIX=hospital-subnet
set SG_NAME=hospital-security-group
set ALB_NAME=hospital-alb
set TARGET_GROUP_NAME=hospital-targets

REM Check if AWS CLI is installed
aws --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ AWS CLI is not installed. Please install it first from: https://aws.amazon.com/cli/
    pause
    exit /b 1
)

echo ✅ AWS CLI found

REM Check if AWS is configured
aws sts get-caller-identity >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ AWS CLI is not configured. Please run: aws configure
    pause
    exit /b 1
)

echo ✅ AWS CLI configured

REM 1. Create ECR repositories
echo 📦 Creating ECR repositories...

aws ecr create-repository --repository-name %ECR_BACKEND_REPO% --region %AWS_REGION% --image-scanning-configuration scanOnPush=true 2>nul || echo Backend repository might already exist

aws ecr create-repository --repository-name %ECR_FRONTEND_REPO% --region %AWS_REGION% --image-scanning-configuration scanOnPush=true 2>nul || echo Frontend repository might already exist

aws ecr create-repository --repository-name %ECR_MCP_REPO% --region %AWS_REGION% --image-scanning-configuration scanOnPush=true 2>nul || echo MCP repository might already exist

REM 2. Create VPC and networking
echo 🌐 Creating VPC and networking components...

REM Create VPC
for /f "tokens=*" %%i in ('aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=%VPC_NAME%}]" --query "Vpc.VpcId" --output text') do set VPC_ID=%%i

echo Created VPC: %VPC_ID%

REM Enable DNS hostnames
aws ec2 modify-vpc-attribute --vpc-id %VPC_ID% --enable-dns-hostnames

REM Create Internet Gateway
for /f "tokens=*" %%i in ('aws ec2 create-internet-gateway --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=%VPC_NAME%-igw}]" --query "InternetGateway.InternetGatewayId" --output text') do set IGW_ID=%%i

echo Created Internet Gateway: %IGW_ID%

REM Attach Internet Gateway to VPC
aws ec2 attach-internet-gateway --internet-gateway-id %IGW_ID% --vpc-id %VPC_ID%

REM Create public subnets
for /f "tokens=*" %%i in ('aws ec2 create-subnet --vpc-id %VPC_ID% --cidr-block 10.0.1.0/24 --availability-zone %AWS_REGION%a --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=%SUBNET_PREFIX%-public-1}]" --query "Subnet.SubnetId" --output text') do set SUBNET_1_ID=%%i

for /f "tokens=*" %%i in ('aws ec2 create-subnet --vpc-id %VPC_ID% --cidr-block 10.0.2.0/24 --availability-zone %AWS_REGION%b --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=%SUBNET_PREFIX%-public-2}]" --query "Subnet.SubnetId" --output text') do set SUBNET_2_ID=%%i

echo Created subnets: %SUBNET_1_ID%, %SUBNET_2_ID%

REM Enable auto-assign public IPs
aws ec2 modify-subnet-attribute --subnet-id %SUBNET_1_ID% --map-public-ip-on-launch
aws ec2 modify-subnet-attribute --subnet-id %SUBNET_2_ID% --map-public-ip-on-launch

REM Create route table
for /f "tokens=*" %%i in ('aws ec2 create-route-table --vpc-id %VPC_ID% --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=%VPC_NAME%-public-rt}]" --query "RouteTable.RouteTableId" --output text') do set ROUTE_TABLE_ID=%%i

REM Add route to Internet Gateway
aws ec2 create-route --route-table-id %ROUTE_TABLE_ID% --destination-cidr-block 0.0.0.0/0 --gateway-id %IGW_ID%

REM Associate subnets with route table
aws ec2 associate-route-table --subnet-id %SUBNET_1_ID% --route-table-id %ROUTE_TABLE_ID%
aws ec2 associate-route-table --subnet-id %SUBNET_2_ID% --route-table-id %ROUTE_TABLE_ID%

REM 3. Create Security Group
echo 🔒 Creating security group...

for /f "tokens=*" %%i in ('aws ec2 create-security-group --group-name %SG_NAME% --description "Security group for Hospital Management System" --vpc-id %VPC_ID% --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=%SG_NAME%}]" --query "GroupId" --output text') do set SG_ID=%%i

echo Created Security Group: %SG_ID%

REM Add security group rules
aws ec2 authorize-security-group-ingress --group-id %SG_ID% --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id %SG_ID% --protocol tcp --port 443 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id %SG_ID% --protocol tcp --port 8000 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id %SG_ID% --protocol tcp --port 3001 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id %SG_ID% --protocol tcp --port 5432 --cidr 10.0.0.0/16

REM 4. Create Application Load Balancer
echo ⚖️ Creating Application Load Balancer...

for /f "tokens=*" %%i in ('aws elbv2 create-load-balancer --name %ALB_NAME% --subnets %SUBNET_1_ID% %SUBNET_2_ID% --security-groups %SG_ID% --scheme internet-facing --type application --ip-address-type ipv4 --query "LoadBalancers[0].LoadBalancerArn" --output text') do set ALB_ARN=%%i

echo Created ALB: %ALB_ARN%

REM Create target group
for /f "tokens=*" %%i in ('aws elbv2 create-target-group --name %TARGET_GROUP_NAME% --protocol HTTP --port 80 --vpc-id %VPC_ID% --target-type ip --health-check-path / --health-check-interval-seconds 30 --health-check-timeout-seconds 5 --healthy-threshold-count 2 --unhealthy-threshold-count 2 --query "TargetGroups[0].TargetGroupArn" --output text') do set TG_ARN=%%i

echo Created Target Group: %TG_ARN%

REM Create listener
aws elbv2 create-listener --load-balancer-arn %ALB_ARN% --protocol HTTP --port 80 --default-actions Type=forward,TargetGroupArn=%TG_ARN%

REM 5. Create ECS Cluster
echo 🐳 Creating ECS cluster...

aws ecs create-cluster --cluster-name %CLUSTER_NAME% --capacity-providers FARGATE --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1

REM 6. Create IAM roles
echo 🔑 Creating IAM roles...

REM Create trust policy
echo { > trust-policy.json
echo   "Version": "2012-10-17", >> trust-policy.json
echo   "Statement": [ >> trust-policy.json
echo     { >> trust-policy.json
echo       "Effect": "Allow", >> trust-policy.json
echo       "Principal": { >> trust-policy.json
echo         "Service": "ecs-tasks.amazonaws.com" >> trust-policy.json
echo       }, >> trust-policy.json
echo       "Action": "sts:AssumeRole" >> trust-policy.json
echo     } >> trust-policy.json
echo   ] >> trust-policy.json
echo } >> trust-policy.json

aws iam create-role --role-name ecsTaskExecutionRole --assume-role-policy-document file://trust-policy.json 2>nul || echo Role might already exist

aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

aws iam create-role --role-name ecsTaskRole --assume-role-policy-document file://trust-policy.json 2>nul || echo Role might already exist

del trust-policy.json

echo ✅ AWS infrastructure setup complete!
echo.
echo 📋 Summary of created resources:
echo VPC ID: %VPC_ID%
echo Subnet IDs: %SUBNET_1_ID%, %SUBNET_2_ID%
echo Security Group ID: %SG_ID%
echo ALB ARN: %ALB_ARN%
echo Target Group ARN: %TG_ARN%
echo.

REM Save values to file for next script
echo set TARGET_GROUP_ARN=%TG_ARN% > aws-values.bat
echo set SUBNET_1_ID=%SUBNET_1_ID% >> aws-values.bat
echo set SUBNET_2_ID=%SUBNET_2_ID% >> aws-values.bat
echo set SG_ID=%SG_ID% >> aws-values.bat
echo set VPC_ID=%VPC_ID% >> aws-values.bat
echo set ALB_ARN=%ALB_ARN% >> aws-values.bat

echo 💾 Values saved to aws-values.bat
echo.
echo 🔧 Next steps:
echo 1. Run create-task-definition.bat to create the ECS service
echo 2. Set up GitHub secrets with your AWS credentials
echo 3. Push your code to trigger the CI/CD pipeline
echo.
pause
