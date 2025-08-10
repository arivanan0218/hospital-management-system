# Hospital Management System - AWS Infrastructure Setup (PowerShell)
# This script sets up AWS infrastructure for deployment

param(
    [string]$AWSRegion = "us-east-1"
)

Write-Host "🚀 Setting up AWS infrastructure for Hospital Management System..." -ForegroundColor Green

# Check if AWS CLI is installed
if (!(Get-Command "aws" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ AWS CLI is not installed. Please install it first." -ForegroundColor Red
    Write-Host "   Visit: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html" -ForegroundColor Yellow
    exit 1
}

# Check if user is logged in
try {
    $null = aws sts get-caller-identity 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "AWS CLI not configured"
    }
} catch {
    Write-Host "❌ AWS CLI is not configured. Please run 'aws configure' first." -ForegroundColor Red
    exit 1
}

# Set variables
$SecurityGroupName = "hospital-management-sg"
$ECRBackendRepo = "hospital-backend"
$ECRFrontendRepo = "hospital-frontend"
$IAMRoleName = "HospitalManagementEC2Role"
$InstanceProfileName = "HospitalManagementInstanceProfile"

Write-Host "📍 Region: $AWSRegion" -ForegroundColor Cyan

# Get AWS Account ID
$AWSAccountID = (aws sts get-caller-identity --query Account --output text)
Write-Host "🏢 AWS Account ID: $AWSAccountID" -ForegroundColor Cyan

# Create ECR repositories
Write-Host "🐳 Creating ECR repositories..." -ForegroundColor Yellow

try {
    aws ecr create-repository --repository-name $ECRBackendRepo --region $AWSRegion --image-scanning-configuration scanOnPush=true --encryption-configuration encryptionType=AES256 2>$null
    Write-Host "   ✅ Backend repository created" -ForegroundColor Green
} catch {
    Write-Host "   Backend repository already exists" -ForegroundColor Yellow
}

try {
    aws ecr create-repository --repository-name $ECRFrontendRepo --region $AWSRegion --image-scanning-configuration scanOnPush=true --encryption-configuration encryptionType=AES256 2>$null
    Write-Host "   ✅ Frontend repository created" -ForegroundColor Green
} catch {
    Write-Host "   Frontend repository already exists" -ForegroundColor Yellow
}

# Create IAM role for EC2 instance
Write-Host "🔐 Creating IAM role for EC2 instance..." -ForegroundColor Yellow

# Trust policy for EC2
$trustPolicy = @"
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
"@

$trustPolicy | Out-File -FilePath "trust-policy.json" -Encoding UTF8

try {
    aws iam create-role --role-name $IAMRoleName --assume-role-policy-document file://trust-policy.json --description "Role for Hospital Management EC2 instance" 2>$null
    Write-Host "   ✅ IAM role created" -ForegroundColor Green
} catch {
    Write-Host "   IAM role already exists" -ForegroundColor Yellow
}

# Attach managed policies
aws iam attach-role-policy --role-name $IAMRoleName --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore 2>$null
aws iam attach-role-policy --role-name $IAMRoleName --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly 2>$null

# Create instance profile
try {
    aws iam create-instance-profile --instance-profile-name $InstanceProfileName 2>$null
    Write-Host "   ✅ Instance profile created" -ForegroundColor Green
} catch {
    Write-Host "   Instance profile already exists" -ForegroundColor Yellow
}

# Add role to instance profile
aws iam add-role-to-instance-profile --instance-profile-name $InstanceProfileName --role-name $IAMRoleName 2>$null

# Clean up temporary file
Remove-Item "trust-policy.json" -ErrorAction SilentlyContinue

# Create security group
Write-Host "🛡️  Creating security group..." -ForegroundColor Yellow
$VpcId = (aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text --region $AWSRegion)

try {
    $SecurityGroupId = (aws ec2 create-security-group --group-name $SecurityGroupName --description "Security group for Hospital Management System" --vpc-id $VpcId --region $AWSRegion --query 'GroupId' --output text)
    
    # Add security group rules
    aws ec2 authorize-security-group-ingress --group-id $SecurityGroupId --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $AWSRegion
    aws ec2 authorize-security-group-ingress --group-id $SecurityGroupId --protocol tcp --port 443 --cidr 0.0.0.0/0 --region $AWSRegion
    aws ec2 authorize-security-group-ingress --group-id $SecurityGroupId --protocol tcp --port 8000 --cidr 0.0.0.0/0 --region $AWSRegion
    
    Write-Host "   ✅ Security group created: $SecurityGroupId" -ForegroundColor Green
} catch {
    $SecurityGroupId = (aws ec2 describe-security-groups --filters "Name=group-name,Values=$SecurityGroupName" --query 'SecurityGroups[0].GroupId' --output text --region $AWSRegion)
    Write-Host "   Security group already exists: $SecurityGroupId" -ForegroundColor Yellow
}

# Launch EC2 instance
Write-Host "🖥️  Launching EC2 instance..." -ForegroundColor Yellow

# Get latest Amazon Linux 2 AMI
$AmiId = (aws ec2 describe-images --owners amazon --filters "Name=name,Values=amzn2-ami-hvm-*" "Name=architecture,Values=x86_64" "Name=state,Values=available" --query 'sort_by(Images, &CreationDate)[-1].ImageId' --output text --region $AWSRegion)

# User data script
$userData = @"
#!/bin/bash
yum update -y

# Install Docker
yum install -y docker git
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-`$(uname -s)-`$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Install Systems Manager Agent
yum install -y amazon-ssm-agent
systemctl enable amazon-ssm-agent
systemctl start amazon-ssm-agent

# Create directory for the application
mkdir -p /home/ec2-user/hospital-management
chown ec2-user:ec2-user /home/ec2-user/hospital-management

echo "User data script completed successfully" > /tmp/userdata-complete.log
"@

# Check if instance already exists
$InstanceId = (aws ec2 describe-instances --filters "Name=tag:Name,Values=hospital-management-server" "Name=instance-state-name,Values=running,pending" --query 'Reservations[0].Instances[0].InstanceId' --output text --region $AWSRegion 2>$null)

if ($InstanceId -and $InstanceId -ne "None") {
    Write-Host "   EC2 instance already exists: $InstanceId" -ForegroundColor Yellow
    $PublicIP = (aws ec2 describe-instances --instance-ids $InstanceId --query 'Reservations[0].Instances[0].PublicIpAddress' --output text --region $AWSRegion)
} else {
    # Wait for instance profile to be ready
    Write-Host "   ⏳ Waiting for IAM instance profile to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10

    $InstanceId = (aws ec2 run-instances --image-id $AmiId --count 1 --instance-type t2.micro --security-group-ids $SecurityGroupId --iam-instance-profile Name=$InstanceProfileName --user-data $userData --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=hospital-management-server},{Key=Project,Value=HospitalManagement}]" --region $AWSRegion --query 'Instances[0].InstanceId' --output text)
    
    Write-Host "   ✅ EC2 instance launched: $InstanceId" -ForegroundColor Green
    Write-Host "   ⏳ Waiting for instance to be running..." -ForegroundColor Yellow
    
    aws ec2 wait instance-running --instance-ids $InstanceId --region $AWSRegion
    
    # Wait for Systems Manager agent to be ready
    Write-Host "   ⏳ Waiting for Systems Manager agent to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    $PublicIP = (aws ec2 describe-instances --instance-ids $InstanceId --query 'Reservations[0].Instances[0].PublicIpAddress' --output text --region $AWSRegion)
}

Write-Host ""
Write-Host "🎉 AWS Infrastructure Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "   • AWS Region: $AWSRegion"
Write-Host "   • AWS Account ID: $AWSAccountID"
Write-Host "   • ECR Backend Repository: $ECRBackendRepo"
Write-Host "   • ECR Frontend Repository: $ECRFrontendRepo"
Write-Host "   • EC2 Instance ID: $InstanceId"
Write-Host "   • EC2 Public IP: $PublicIP"
Write-Host "   • Security Group: $SecurityGroupId"
Write-Host "   • IAM Role: $IAMRoleName"
Write-Host ""
Write-Host "🔧 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Add these GitHub Secrets to your repository:"
Write-Host "   Go to: https://github.com/yourusername/hospital-management-system/settings/secrets/actions"
Write-Host ""
Write-Host "   Required Secrets:"
Write-Host "   • AWS_ACCESS_KEY_ID: (your AWS access key)"
Write-Host "   • AWS_SECRET_ACCESS_KEY: (your AWS secret key)"
Write-Host "   • AWS_ACCOUNT_ID: $AWSAccountID"
Write-Host "   • POSTGRES_PASSWORD: (choose a secure password)"
Write-Host "   • GEMINI_API_KEY: (your Gemini API key from https://aistudio.google.com/app/apikey)"
Write-Host ""
Write-Host "   Optional API Keys (for additional AI models):"
Write-Host "   • VITE_CLAUDE_API_KEY: (Anthropic Claude API key)"
Write-Host "   • VITE_OPENAI_API_KEY: (OpenAI API key)"
Write-Host "   • VITE_GROQ_API_KEY: (Groq API key)"
Write-Host "   • VITE_GOOGLE_API_KEY: (Google AI API key)"
Write-Host ""
Write-Host "2. Push your code to the dev branch to trigger deployment:"
Write-Host "   git add ."
Write-Host "   git commit -m 'Add AWS deployment configuration'"
Write-Host "   git push origin dev"
Write-Host ""
Write-Host "🌐 Your application will be available at: http://$PublicIP" -ForegroundColor Green
Write-Host "📊 Backend API docs will be at: http://$PublicIP" -NoNewline -ForegroundColor Green
Write-Host ":8000/docs" -ForegroundColor Green
