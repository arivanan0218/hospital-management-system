#!/bin/bash

# Hospital Management System AWS Infrastructure Setup
# This script sets up the necessary AWS resources for deployment

set -e

echo "🚀 Setting up AWS infrastructure for Hospital Management System..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is logged in
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

# Set variables
AWS_REGION=${AWS_REGION:-us-east-1}
KEY_NAME="hospital-management-key"
SECURITY_GROUP_NAME="hospital-management-sg"
ECR_BACKEND_REPO="hospital-backend"
ECR_FRONTEND_REPO="hospital-frontend"

echo "📍 Region: $AWS_REGION"

# Create ECR repositories
echo "🐳 Creating ECR repositories..."

aws ecr create-repository \
    --repository-name $ECR_BACKEND_REPO \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256 \
    2>/dev/null || echo "Backend repository already exists"

aws ecr create-repository \
    --repository-name $ECR_FRONTEND_REPO \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256 \
    2>/dev/null || echo "Frontend repository already exists"

# Create key pair for EC2 access
echo "🔑 Creating EC2 key pair..."
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME --region $AWS_REGION &> /dev/null; then
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --region $AWS_REGION \
        --query 'KeyMaterial' \
        --output text > ${KEY_NAME}.pem
    
    chmod 400 ${KEY_NAME}.pem
    echo "✅ Key pair created and saved as ${KEY_NAME}.pem"
    echo "⚠️  IMPORTANT: Save this key file securely! You'll need it to access your EC2 instance."
else
    echo "Key pair already exists"
fi

# Create security group
echo "🛡️  Creating security group..."
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text --region $AWS_REGION)

if ! aws ec2 describe-security-groups --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" --region $AWS_REGION &> /dev/null; then
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name $SECURITY_GROUP_NAME \
        --description "Security group for Hospital Management System" \
        --vpc-id $VPC_ID \
        --region $AWS_REGION \
        --query 'GroupId' \
        --output text)
    
    # Add security group rules
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region $AWS_REGION
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0 \
        --region $AWS_REGION
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0 \
        --region $AWS_REGION
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 8000 \
        --cidr 0.0.0.0/0 \
        --region $AWS_REGION
    
    echo "✅ Security group created: $SECURITY_GROUP_ID"
else
    SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" --query 'SecurityGroups[0].GroupId' --output text --region $AWS_REGION)
    echo "Security group already exists: $SECURITY_GROUP_ID"
fi

# Launch EC2 instance (t2.micro for free tier)
echo "🖥️  Launching EC2 instance..."

# Get latest Amazon Linux 2 AMI
AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=amzn2-ami-hvm-*" "Name=architecture,Values=x86_64" "Name=state,Values=available" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text \
    --region $AWS_REGION)

# User data script to set up Docker and AWS CLI
USER_DATA=$(cat << 'EOF'
#!/bin/bash
yum update -y
yum install -y docker git

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Start Docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Create directory for the application
mkdir -p /home/ec2-user/hospital-management
chown ec2-user:ec2-user /home/ec2-user/hospital-management
EOF
)

# Check if instance already exists
INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=hospital-management-server" "Name=instance-state-name,Values=running,pending" \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text \
    --region $AWS_REGION 2>/dev/null)

if [ "$INSTANCE_ID" != "None" ] && [ "$INSTANCE_ID" != "" ]; then
    echo "EC2 instance already exists: $INSTANCE_ID"
    PUBLIC_IP=$(aws ec2 describe-instances \
        --instance-ids $INSTANCE_ID \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text \
        --region $AWS_REGION)
else
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --count 1 \
        --instance-type t2.micro \
        --key-name $KEY_NAME \
        --security-group-ids $SECURITY_GROUP_ID \
        --user-data "$USER_DATA" \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=hospital-management-server}]" \
        --region $AWS_REGION \
        --query 'Instances[0].InstanceId' \
        --output text)
    
    echo "✅ EC2 instance launched: $INSTANCE_ID"
    echo "⏳ Waiting for instance to be running..."
    
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $AWS_REGION
    
    PUBLIC_IP=$(aws ec2 describe-instances \
        --instance-ids $INSTANCE_ID \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text \
        --region $AWS_REGION)
fi

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo ""
echo "🎉 AWS Infrastructure Setup Complete!"
echo ""
echo "📋 Summary:"
echo "   • AWS Region: $AWS_REGION"
echo "   • AWS Account ID: $AWS_ACCOUNT_ID"
echo "   • ECR Backend Repository: $ECR_BACKEND_REPO"
echo "   • ECR Frontend Repository: $ECR_FRONTEND_REPO"
echo "   • EC2 Instance ID: $INSTANCE_ID"
echo "   • EC2 Public IP: $PUBLIC_IP"
echo "   • Security Group: $SECURITY_GROUP_ID"
echo "   • Key Pair: $KEY_NAME"
echo ""
echo "🔧 Next Steps:"
echo "1. Add these GitHub Secrets to your repository:"
echo "   • AWS_ACCESS_KEY_ID"
echo "   • AWS_SECRET_ACCESS_KEY"
echo "   • EC2_HOST: $PUBLIC_IP"
echo "   • POSTGRES_PASSWORD: (choose a secure password)"
echo "   • GEMINI_API_KEY: (your Gemini API key)"
echo "   • VITE_CLAUDE_API_KEY: (optional)"
echo "   • VITE_OPENAI_API_KEY: (optional)"
echo "   • VITE_GROQ_API_KEY: (optional)"
echo "   • VITE_GOOGLE_API_KEY: (optional)"
echo ""
echo "2. Add the EC2 private key to GitHub Secrets as EC2_PRIVATE_KEY:"
echo "   Copy the contents of ${KEY_NAME}.pem"
echo ""
echo "3. Test SSH connection:"
echo "   ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP"
echo ""
echo "4. Push your code to trigger the CI/CD pipeline!"
echo ""
echo "🌐 Your application will be available at: http://$PUBLIC_IP"
