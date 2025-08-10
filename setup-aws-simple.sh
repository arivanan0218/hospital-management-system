#!/bin/bash

# Simplified AWS Infrastructure Setup for Hospital Management System
# This version uses AWS Systems Manager for deployment (no SSH keys needed)

set -e

echo "🚀 Setting up AWS infrastructure for Hospital Management System..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    echo "   Visit: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check if user is logged in
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

# Set variables
AWS_REGION=${AWS_REGION:-us-east-1}
SECURITY_GROUP_NAME="hospital-management-sg"
ECR_BACKEND_REPO="hospital-backend"
ECR_FRONTEND_REPO="hospital-frontend"
IAM_ROLE_NAME="HospitalManagementEC2Role"
INSTANCE_PROFILE_NAME="HospitalManagementInstanceProfile"

echo "📍 Region: $AWS_REGION"

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "🏢 AWS Account ID: $AWS_ACCOUNT_ID"

# Create ECR repositories
echo "🐳 Creating ECR repositories..."

aws ecr create-repository \
    --repository-name $ECR_BACKEND_REPO \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256 \
    2>/dev/null || echo "   Backend repository already exists"

aws ecr create-repository \
    --repository-name $ECR_FRONTEND_REPO \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256 \
    2>/dev/null || echo "   Frontend repository already exists"

# Create IAM role for EC2 instance (for Systems Manager and ECR access)
echo "🔐 Creating IAM role for EC2 instance..."

# Trust policy for EC2
cat > trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Create IAM role
aws iam create-role \
    --role-name $IAM_ROLE_NAME \
    --assume-role-policy-document file://trust-policy.json \
    --description "Role for Hospital Management EC2 instance" \
    2>/dev/null || echo "   IAM role already exists"

# Attach managed policies
aws iam attach-role-policy \
    --role-name $IAM_ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore \
    2>/dev/null || true

aws iam attach-role-policy \
    --role-name $IAM_ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly \
    2>/dev/null || true

# Create instance profile
aws iam create-instance-profile \
    --instance-profile-name $INSTANCE_PROFILE_NAME \
    2>/dev/null || echo "   Instance profile already exists"

# Add role to instance profile
aws iam add-role-to-instance-profile \
    --instance-profile-name $INSTANCE_PROFILE_NAME \
    --role-name $IAM_ROLE_NAME \
    2>/dev/null || true

# Clean up temporary file
rm -f trust-policy.json

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
    
    echo "   ✅ Security group created: $SECURITY_GROUP_ID"
else
    SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" --query 'SecurityGroups[0].GroupId' --output text --region $AWS_REGION)
    echo "   Security group already exists: $SECURITY_GROUP_ID"
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

# Install Docker
yum install -y docker git
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Install Systems Manager Agent (should be pre-installed on Amazon Linux 2)
yum install -y amazon-ssm-agent
systemctl enable amazon-ssm-agent
systemctl start amazon-ssm-agent

# Create directory for the application
mkdir -p /home/ec2-user/hospital-management
chown ec2-user:ec2-user /home/ec2-user/hospital-management

# Signal that user data script is complete
echo "User data script completed successfully" > /tmp/userdata-complete.log
EOF
)

# Check if instance already exists
INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=hospital-management-server" "Name=instance-state-name,Values=running,pending" \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text \
    --region $AWS_REGION 2>/dev/null)

if [ "$INSTANCE_ID" != "None" ] && [ "$INSTANCE_ID" != "" ]; then
    echo "   EC2 instance already exists: $INSTANCE_ID"
    PUBLIC_IP=$(aws ec2 describe-instances \
        --instance-ids $INSTANCE_ID \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text \
        --region $AWS_REGION)
else
    # Wait for instance profile to be ready
    echo "   ⏳ Waiting for IAM instance profile to be ready..."
    sleep 10

    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --count 1 \
        --instance-type t2.micro \
        --security-group-ids $SECURITY_GROUP_ID \
        --iam-instance-profile Name=$INSTANCE_PROFILE_NAME \
        --user-data "$USER_DATA" \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=hospital-management-server},{Key=Project,Value=HospitalManagement}]" \
        --region $AWS_REGION \
        --query 'Instances[0].InstanceId' \
        --output text)
    
    echo "   ✅ EC2 instance launched: $INSTANCE_ID"
    echo "   ⏳ Waiting for instance to be running..."
    
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $AWS_REGION
    
    # Wait for Systems Manager agent to be ready
    echo "   ⏳ Waiting for Systems Manager agent to be ready..."
    sleep 30
    
    PUBLIC_IP=$(aws ec2 describe-instances \
        --instance-ids $INSTANCE_ID \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text \
        --region $AWS_REGION)
fi

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
echo "   • IAM Role: $IAM_ROLE_NAME"
echo ""
echo "🔧 Next Steps:"
echo "1. Add these GitHub Secrets to your repository:"
echo "   Go to: https://github.com/yourusername/hospital-management-system/settings/secrets/actions"
echo ""
echo "   Required Secrets:"
echo "   • AWS_ACCESS_KEY_ID: (your AWS access key)"
echo "   • AWS_SECRET_ACCESS_KEY: (your AWS secret key)"
echo "   • AWS_ACCOUNT_ID: $AWS_ACCOUNT_ID"
echo "   • POSTGRES_PASSWORD: (choose a secure password)"
echo "   • GEMINI_API_KEY: (your Gemini API key from https://aistudio.google.com/app/apikey)"
echo ""
echo "   Optional API Keys (for additional AI models):"
echo "   • VITE_CLAUDE_API_KEY: (Anthropic Claude API key)"
echo "   • VITE_OPENAI_API_KEY: (OpenAI API key)"
echo "   • VITE_GROQ_API_KEY: (Groq API key)"
echo "   • VITE_GOOGLE_API_KEY: (Google AI API key)"
echo ""
echo "2. Push your code to the main branch to trigger deployment:"
echo "   git add ."
echo "   git commit -m \"Add AWS deployment configuration\""
echo "   git push origin main"
echo ""
echo "3. Monitor the deployment:"
echo "   • Go to your GitHub repository"
echo "   • Click on the 'Actions' tab"
echo "   • Watch the CI/CD pipeline run"
echo ""
echo "🌐 Your application will be available at: http://$PUBLIC_IP"
echo "📊 Backend API docs will be at: http://$PUBLIC_IP:8000/docs"
echo ""
echo "📚 For detailed deployment instructions, see DEPLOYMENT.md"
echo ""
echo "⚠️  Important Notes:"
echo "   • This setup uses AWS Free Tier resources"
echo "   • Make sure to monitor your AWS usage"
echo "   • The instance will be accessible from the internet"
echo "   • Consider adding SSL/TLS for production use"
