#!/bin/bash

# AWS Infrastructure Setup Script for Hospital Management System
# This script creates the necessary AWS resources for deployment

set -e

# Configuration
REGION="us-east-1"
APP_NAME="hospital-management"
KEY_PAIR_NAME="hospital-key-pair"
INSTANCE_TYPE="t3.medium"
SECURITY_GROUP_NAME="hospital-sg"

echo "🚀 Setting up AWS infrastructure for Hospital Management System..."

# 1. Create ECR repositories
echo "📦 Creating ECR repositories..."
aws ecr create-repository --repository-name hospital-frontend --region $REGION || echo "Frontend repository already exists"
aws ecr create-repository --repository-name hospital-backend --region $REGION || echo "Backend repository already exists"

# 2. Create VPC and Security Group
echo "🔒 Creating security group..."
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text --region $REGION)

SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name $SECURITY_GROUP_NAME \
    --description "Security group for Hospital Management System" \
    --vpc-id $VPC_ID \
    --region $REGION \
    --query 'GroupId' \
    --output text 2>/dev/null || \
    aws ec2 describe-security-groups \
    --group-names $SECURITY_GROUP_NAME \
    --query 'SecurityGroups[0].GroupId' \
    --output text \
    --region $REGION)

echo "Security Group ID: $SECURITY_GROUP_ID"

# 3. Configure security group rules
echo "🔐 Configuring security group rules..."
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 \
    --region $REGION 2>/dev/null || echo "SSH rule already exists"

aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0 \
    --region $REGION 2>/dev/null || echo "HTTP rule already exists"

aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0 \
    --region $REGION 2>/dev/null || echo "HTTPS rule already exists"

aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 8000 \
    --cidr 0.0.0.0/0 \
    --region $REGION 2>/dev/null || echo "Backend API rule already exists"

# 4. Create key pair if it doesn't exist
echo "🔑 Creating key pair..."
if ! aws ec2 describe-key-pairs --key-names $KEY_PAIR_NAME --region $REGION >/dev/null 2>&1; then
    aws ec2 create-key-pair \
        --key-name $KEY_PAIR_NAME \
        --query 'KeyMaterial' \
        --output text \
        --region $REGION > ${KEY_PAIR_NAME}.pem
    chmod 400 ${KEY_PAIR_NAME}.pem
    echo "Key pair created and saved as ${KEY_PAIR_NAME}.pem"
else
    echo "Key pair already exists"
fi

# 5. Get latest Ubuntu AMI
echo "🖥️  Finding latest Ubuntu AMI..."
AMI_ID=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters 'Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*' \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text \
    --region $REGION)

echo "Using AMI: $AMI_ID"

# 6. Create EC2 instance
echo "🚀 Creating EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --count 1 \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_PAIR_NAME \
    --security-group-ids $SECURITY_GROUP_ID \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${APP_NAME}-server}]" \
    --user-data file://user-data.sh \
    --region $REGION \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "Instance ID: $INSTANCE_ID"

# 7. Wait for instance to be running
echo "⏳ Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION

# 8. Get instance public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text \
    --region $REGION)

echo "✅ Setup complete!"
echo ""
echo "📋 Summary:"
echo "  - Region: $REGION"
echo "  - Instance ID: $INSTANCE_ID"
echo "  - Public IP: $PUBLIC_IP"
echo "  - Security Group: $SECURITY_GROUP_ID"
echo "  - Key Pair: ${KEY_PAIR_NAME}.pem"
echo ""
echo "🔧 Next steps:"
echo "  1. Add these secrets to your GitHub repository:"
echo "     - AWS_ACCESS_KEY_ID"
echo "     - AWS_SECRET_ACCESS_KEY"
echo "     - AWS_ACCOUNT_ID"
echo "     - EC2_HOST: $PUBLIC_IP"
echo "     - EC2_USER: ubuntu"
echo "     - EC2_SSH_PRIVATE_KEY: (content of ${KEY_PAIR_NAME}.pem)"
echo "     - POSTGRES_PASSWORD: (your secure password)"
echo "     - GEMINI_API_KEY: (your API key)"
echo ""
echo "  2. Test SSH connection:"
echo "     ssh -i ${KEY_PAIR_NAME}.pem ubuntu@$PUBLIC_IP"
echo ""
echo "  3. Your application will be available at:"
echo "     http://$PUBLIC_IP"
