#!/bin/bash

# AWS Deployment Script for Hospital Management System
# This script will deploy your application to AWS

set -e

echo "🏥 Hospital Management System - AWS Deployment"
echo "=============================================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    echo "Visit: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html"
    exit 1
fi

# Check if user is logged into AWS
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ You are not authenticated with AWS. Please run 'aws configure' first."
    exit 1
fi

# Get AWS Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION="us-east-1"

echo "✅ AWS Account ID: $ACCOUNT_ID"
echo "✅ AWS Region: $AWS_REGION"

# Step 1: Create CloudFormation Stack
echo ""
echo "📋 Step 1: Creating AWS Infrastructure..."
aws cloudformation deploy \
    --template-file aws-infrastructure.yml \
    --stack-name hospital-infrastructure \
    --parameter-overrides \
        VpcCIDR=10.0.0.0/16 \
        PublicSubnet1CIDR=10.0.1.0/24 \
        PublicSubnet2CIDR=10.0.2.0/24 \
    --capabilities CAPABILITY_IAM \
    --region $AWS_REGION

echo "✅ Infrastructure created successfully!"

# Step 2: Create database password in SSM Parameter Store
echo ""
echo "🔐 Step 2: Setting up database password..."
aws ssm put-parameter \
    --name "/hospital/database/password" \
    --value "HospitalSecure123!" \
    --type "SecureString" \
    --overwrite \
    --region $AWS_REGION

echo "✅ Database password stored in SSM Parameter Store"

# Step 3: Get RDS endpoint
echo ""
echo "🗄️ Step 3: Getting database endpoint..."
DB_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name hospital-infrastructure \
    --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
    --output text \
    --region $AWS_REGION)

echo "✅ Database endpoint: $DB_ENDPOINT"

# Step 4: Get ALB DNS name
ALB_DNS=$(aws cloudformation describe-stacks \
    --stack-name hospital-infrastructure \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
    --output text \
    --region $AWS_REGION)

echo "✅ Load balancer DNS: $ALB_DNS"

# Step 5: Update task definitions with actual values
echo ""
echo "📝 Step 5: Updating task definitions..."

# Update backend task definition
sed -i "s/ACCOUNT_ID/$ACCOUNT_ID/g" backend-task-definition.json
sed -i "s/RDS_ENDPOINT/$DB_ENDPOINT/g" backend-task-definition.json
sed -i "s/PASSWORD/HospitalSecure123!/g" backend-task-definition.json

# Update frontend task definition
sed -i "s/ACCOUNT_ID/$ACCOUNT_ID/g" frontend-task-definition.json
sed -i "s/ALB_DNS_NAME/$ALB_DNS/g" frontend-task-definition.json

echo "✅ Task definitions updated"

# Step 6: Create CloudWatch Log Groups
echo ""
echo "📊 Step 6: Creating CloudWatch log groups..."
aws logs create-log-group --log-group-name "/ecs/hospital-backend" --region $AWS_REGION 2>/dev/null || echo "Backend log group already exists"
aws logs create-log-group --log-group-name "/ecs/hospital-frontend" --region $AWS_REGION 2>/dev/null || echo "Frontend log group already exists"

echo "✅ CloudWatch log groups created"

# Step 7: Build and push Docker images
echo ""
echo "🐳 Step 7: Building and pushing Docker images..."

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build and push backend
echo "Building backend image..."
cd backend-python
docker build -t hospital-backend .
docker tag hospital-backend:latest $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-backend:latest
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-backend:latest
cd ..

# Build and push frontend
echo "Building frontend image..."
cd frontend
docker build -t hospital-frontend .
docker tag hospital-frontend:latest $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-frontend:latest
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-frontend:latest
cd ..

echo "✅ Docker images built and pushed"

# Step 8: Register task definitions
echo ""
echo "📋 Step 8: Registering ECS task definitions..."
aws ecs register-task-definition --cli-input-json file://backend-task-definition.json --region $AWS_REGION
aws ecs register-task-definition --cli-input-json file://frontend-task-definition.json --region $AWS_REGION

echo "✅ Task definitions registered"

# Step 9: Create ECS services
echo ""
echo "🚀 Step 9: Creating ECS services..."

# Get subnet IDs
SUBNET_IDS=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$(aws cloudformation describe-stacks --stack-name hospital-infrastructure --query 'Stacks[0].Outputs[?OutputKey==`VPC`].OutputValue' --output text --region $AWS_REGION)" \
    --query 'Subnets[*].SubnetId' \
    --output text \
    --region $AWS_REGION)

SUBNET_ID_1=$(echo $SUBNET_IDS | cut -d' ' -f1)
SUBNET_ID_2=$(echo $SUBNET_IDS | cut -d' ' -f2)

# Get security group IDs
BACKEND_SG=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=*Backend*" \
    --query 'SecurityGroups[0].GroupId' \
    --output text \
    --region $AWS_REGION)

ALB_SG=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=*ALB*" \
    --query 'SecurityGroups[0].GroupId' \
    --output text \
    --region $AWS_REGION)

# Get target group ARNs
BACKEND_TG_ARN=$(aws elbv2 describe-target-groups \
    --names "hospital-backend-tg" \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text \
    --region $AWS_REGION)

FRONTEND_TG_ARN=$(aws elbv2 describe-target-groups \
    --names "hospital-frontend-tg" \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text \
    --region $AWS_REGION)

# Create backend service
aws ecs create-service \
    --cluster hospital-cluster \
    --service-name hospital-backend-service \
    --task-definition hospital-backend-task \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_ID_1,$SUBNET_ID_2],securityGroups=[$BACKEND_SG],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=$BACKEND_TG_ARN,containerName=hospital-backend,containerPort=8000" \
    --region $AWS_REGION

# Create frontend service
aws ecs create-service \
    --cluster hospital-cluster \
    --service-name hospital-frontend-service \
    --task-definition hospital-frontend-task \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_ID_1,$SUBNET_ID_2],securityGroups=[$ALB_SG],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=$FRONTEND_TG_ARN,containerName=hospital-frontend,containerPort=3000" \
    --region $AWS_REGION

echo "✅ ECS services created"

echo ""
echo "🎉 Deployment completed successfully!"
echo "🌐 Your application will be available at: http://$ALB_DNS"
echo ""
echo "📝 Next steps:"
echo "1. Wait 5-10 minutes for services to start"
echo "2. Check ECS service status in AWS Console"
echo "3. Visit your application URL"
echo "4. Set up your GitHub secrets for CI/CD"
echo ""
echo "🔧 GitHub Secrets to add:"
echo "- AWS_ACCESS_KEY_ID"
echo "- AWS_SECRET_ACCESS_KEY"
