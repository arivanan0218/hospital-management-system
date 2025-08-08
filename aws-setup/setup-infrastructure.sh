#!/bin/bash

# Hospital Management System AWS Infrastructure Setup
# This script creates the necessary AWS resources for deployment

set -e

# Configuration
AWS_REGION="us-east-1"
CLUSTER_NAME="hospital-cluster"
SERVICE_NAME="hospital-management-service"
TASK_DEFINITION_NAME="hospital-task-definition"
ECR_BACKEND_REPO="hospital-backend"
ECR_FRONTEND_REPO="hospital-frontend"
ECR_MCP_REPO="hospital-mcp-manager"
VPC_NAME="hospital-vpc"
SUBNET_PREFIX="hospital-subnet"
SG_NAME="hospital-security-group"
ALB_NAME="hospital-alb"
TARGET_GROUP_NAME="hospital-targets"

echo "🚀 Setting up AWS infrastructure for Hospital Management System..."

# 1. Create ECR repositories
echo "📦 Creating ECR repositories..."

aws ecr create-repository \
    --repository-name $ECR_BACKEND_REPO \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    || echo "Backend repository might already exist"

aws ecr create-repository \
    --repository-name $ECR_FRONTEND_REPO \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    || echo "Frontend repository might already exist"

aws ecr create-repository \
    --repository-name $ECR_MCP_REPO \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    || echo "MCP repository might already exist"

# 2. Create VPC and networking
echo "🌐 Creating VPC and networking components..."

# Create VPC
VPC_ID=$(aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16 \
    --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=$VPC_NAME}]" \
    --query 'Vpc.VpcId' \
    --output text)

echo "Created VPC: $VPC_ID"

# Enable DNS hostnames
aws ec2 modify-vpc-attribute \
    --vpc-id $VPC_ID \
    --enable-dns-hostnames

# Create Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway \
    --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=${VPC_NAME}-igw}]" \
    --query 'InternetGateway.InternetGatewayId' \
    --output text)

echo "Created Internet Gateway: $IGW_ID"

# Attach Internet Gateway to VPC
aws ec2 attach-internet-gateway \
    --internet-gateway-id $IGW_ID \
    --vpc-id $VPC_ID

# Create public subnets
SUBNET_1_ID=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.1.0/24 \
    --availability-zone ${AWS_REGION}a \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${SUBNET_PREFIX}-public-1}]" \
    --query 'Subnet.SubnetId' \
    --output text)

SUBNET_2_ID=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.2.0/24 \
    --availability-zone ${AWS_REGION}b \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${SUBNET_PREFIX}-public-2}]" \
    --query 'Subnet.SubnetId' \
    --output text)

echo "Created subnets: $SUBNET_1_ID, $SUBNET_2_ID"

# Enable auto-assign public IPs
aws ec2 modify-subnet-attribute \
    --subnet-id $SUBNET_1_ID \
    --map-public-ip-on-launch

aws ec2 modify-subnet-attribute \
    --subnet-id $SUBNET_2_ID \
    --map-public-ip-on-launch

# Create route table
ROUTE_TABLE_ID=$(aws ec2 create-route-table \
    --vpc-id $VPC_ID \
    --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=${VPC_NAME}-public-rt}]" \
    --query 'RouteTable.RouteTableId' \
    --output text)

# Add route to Internet Gateway
aws ec2 create-route \
    --route-table-id $ROUTE_TABLE_ID \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id $IGW_ID

# Associate subnets with route table
aws ec2 associate-route-table \
    --subnet-id $SUBNET_1_ID \
    --route-table-id $ROUTE_TABLE_ID

aws ec2 associate-route-table \
    --subnet-id $SUBNET_2_ID \
    --route-table-id $ROUTE_TABLE_ID

# 3. Create Security Group
echo "🔒 Creating security group..."

SG_ID=$(aws ec2 create-security-group \
    --group-name $SG_NAME \
    --description "Security group for Hospital Management System" \
    --vpc-id $VPC_ID \
    --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=$SG_NAME}]" \
    --query 'GroupId' \
    --output text)

echo "Created Security Group: $SG_ID"

# Add security group rules
aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 8000 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 3001 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 5432 \
    --cidr 10.0.0.0/16

# 4. Create Application Load Balancer
echo "⚖️ Creating Application Load Balancer..."

ALB_ARN=$(aws elbv2 create-load-balancer \
    --name $ALB_NAME \
    --subnets $SUBNET_1_ID $SUBNET_2_ID \
    --security-groups $SG_ID \
    --scheme internet-facing \
    --type application \
    --ip-address-type ipv4 \
    --query 'LoadBalancers[0].LoadBalancerArn' \
    --output text)

echo "Created ALB: $ALB_ARN"

# Create target group
TG_ARN=$(aws elbv2 create-target-group \
    --name $TARGET_GROUP_NAME \
    --protocol HTTP \
    --port 80 \
    --vpc-id $VPC_ID \
    --target-type ip \
    --health-check-path / \
    --health-check-interval-seconds 30 \
    --health-check-timeout-seconds 5 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 2 \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)

echo "Created Target Group: $TG_ARN"

# Create listener
aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=$TG_ARN

# 5. Create ECS Cluster
echo "🐳 Creating ECS cluster..."

aws ecs create-cluster \
    --cluster-name $CLUSTER_NAME \
    --capacity-providers FARGATE \
    --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1

# 6. Create IAM roles
echo "🔑 Creating IAM roles..."

# ECS Task Execution Role
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role \
    --role-name ecsTaskExecutionRole \
    --assume-role-policy-document file://trust-policy.json \
    || echo "Role might already exist"

aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# ECS Task Role
aws iam create-role \
    --role-name ecsTaskRole \
    --assume-role-policy-document file://trust-policy.json \
    || echo "Role might already exist"

rm trust-policy.json

echo "✅ AWS infrastructure setup complete!"
echo ""
echo "📋 Summary of created resources:"
echo "VPC ID: $VPC_ID"
echo "Subnet IDs: $SUBNET_1_ID, $SUBNET_2_ID"
echo "Security Group ID: $SG_ID"
echo "ALB ARN: $ALB_ARN"
echo "Target Group ARN: $TG_ARN"
echo ""
echo "🔧 Next steps:"
echo "1. Create the ECS task definition using create-task-definition.sh"
echo "2. Set up GitHub secrets with your AWS credentials"
echo "3. Push your code to trigger the CI/CD pipeline"
