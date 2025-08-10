# Hospital Management System - AWS Deployment Guide

This guide will help you deploy the Hospital Management System to AWS using Docker containers and GitHub Actions for CI/CD.

## 🏗️ Architecture Overview

```
GitHub Repository
       ↓ (push to main)
GitHub Actions CI/CD
       ↓ (build & push)
Amazon ECR (Container Registry)
       ↓ (deploy)
EC2 Instance (t2.micro - Free Tier)
  ├── Frontend Container (React + Nginx)
  ├── Backend Container (Python FastAPI)
  └── PostgreSQL Container (Docker)
```

## 📋 Prerequisites

1. **AWS Account** with free tier access
2. **GitHub Repository** with your code
3. **API Keys** for AI services (at least Gemini API key)

## 🚀 Step 1: AWS Infrastructure Setup

### Option A: Automated Setup (Recommended)

1. **Install AWS CLI** on your local machine:
   ```bash
   # On Windows (using chocolatey)
   choco install awscli
   
   # On macOS
   brew install awscli
   
   # On Linux
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

2. **Configure AWS CLI**:
   ```bash
   aws configure
   ```
   Enter your AWS credentials:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region: `us-east-1`
   - Default output format: `json`

3. **Run the setup script**:
   ```bash
   chmod +x setup-aws-infrastructure.sh
   ./setup-aws-infrastructure.sh
   ```

### Option B: Manual Setup

<details>
<summary>Click to expand manual setup instructions</summary>

1. **Create ECR Repositories**:
   ```bash
   aws ecr create-repository --repository-name hospital-backend --region us-east-1
   aws ecr create-repository --repository-name hospital-frontend --region us-east-1
   ```

2. **Create EC2 Key Pair**:
   ```bash
   aws ec2 create-key-pair --key-name hospital-management-key --query 'KeyMaterial' --output text > hospital-management-key.pem
   chmod 400 hospital-management-key.pem
   ```

3. **Create Security Group**:
   ```bash
   # Get default VPC ID
   VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text)
   
   # Create security group
   SECURITY_GROUP_ID=$(aws ec2 create-security-group \
     --group-name hospital-management-sg \
     --description "Security group for Hospital Management System" \
     --vpc-id $VPC_ID \
     --query 'GroupId' \
     --output text)
   
   # Add inbound rules
   aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol tcp --port 22 --cidr 0.0.0.0/0
   aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
   aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol tcp --port 443 --cidr 0.0.0.0/0
   aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol tcp --port 8000 --cidr 0.0.0.0/0
   ```

4. **Launch EC2 Instance**:
   ```bash
   # Get latest Amazon Linux 2 AMI
   AMI_ID=$(aws ec2 describe-images \
     --owners amazon \
     --filters "Name=name,Values=amzn2-ami-hvm-*" "Name=architecture,Values=x86_64" \
     --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
     --output text)
   
   # Launch instance
   INSTANCE_ID=$(aws ec2 run-instances \
     --image-id $AMI_ID \
     --count 1 \
     --instance-type t2.micro \
     --key-name hospital-management-key \
     --security-group-ids $SECURITY_GROUP_ID \
     --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=hospital-management-server}]" \
     --query 'Instances[0].InstanceId' \
     --output text)
   ```

</details>

## 🔧 Step 2: GitHub Secrets Configuration

Add the following secrets to your GitHub repository (`Settings` → `Secrets and variables` → `Actions`):

### Required Secrets:
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `EC2_HOST`: Public IP address of your EC2 instance
- `EC2_PRIVATE_KEY`: Contents of your EC2 private key (.pem file)
- `POSTGRES_PASSWORD`: Secure password for PostgreSQL database
- `GEMINI_API_KEY`: Your Google Gemini API key

### Optional API Keys:
- `VITE_CLAUDE_API_KEY`: Anthropic Claude API key
- `VITE_OPENAI_API_KEY`: OpenAI API key
- `VITE_GROQ_API_KEY`: Groq API key
- `VITE_GOOGLE_API_KEY`: Google AI API key

## 🚀 Step 3: Deploy

1. **Push to main branch**:
   ```bash
   git add .
   git commit -m "Add AWS deployment configuration"
   git push origin main
   ```

2. **Monitor deployment**:
   - Go to your GitHub repository
   - Click on "Actions" tab
   - Watch the CI/CD pipeline run

3. **Access your application**:
   - Frontend: `http://your-ec2-public-ip`
   - Backend API: `http://your-ec2-public-ip:8000`
   - API Docs: `http://your-ec2-public-ip:8000/docs`

## 📱 Step 4: Local Development

For local development and testing:

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your preferred editor

# Run locally
chmod +x setup-local.sh
./setup-local.sh
```

## 🔍 Monitoring and Maintenance

### Check Application Status:
```bash
# SSH into EC2 instance
ssh -i hospital-management-key.pem ec2-user@your-ec2-public-ip

# Check running containers
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs [service-name]

# Restart services
docker-compose -f docker-compose.prod.yml restart [service-name]
```

### Update Application:
1. Push changes to main branch
2. GitHub Actions will automatically build and deploy
3. Or manually pull latest images:
   ```bash
   # On EC2 instance
   docker-compose -f docker-compose.prod.yml pull
   docker-compose -f docker-compose.prod.yml up -d
   ```

## 🛡️ Security Best Practices

1. **API Keys**: Store all API keys in GitHub Secrets, never in code
2. **Database**: Use strong passwords and limit database access
3. **EC2**: Regularly update the instance and limit security group access
4. **HTTPS**: Consider adding SSL certificate for production use
5. **Backups**: Regularly backup your PostgreSQL data

## 💰 Cost Optimization

### Free Tier Usage:
- **EC2 t2.micro**: 750 hours/month (free for 12 months)
- **ECR**: 500 MB storage (always free)
- **Data Transfer**: 1 GB/month (always free)

### Cost Monitoring:
- Set up AWS billing alerts
- Monitor ECR storage usage
- Consider shutting down during development breaks

## 🚨 Troubleshooting

### Common Issues:

1. **Build Failures**:
   - Check GitHub Actions logs
   - Verify all secrets are set correctly
   - Ensure AWS credentials have necessary permissions

2. **Deployment Failures**:
   - Check EC2 instance logs: `ssh` into instance and run `docker-compose logs`
   - Verify security group allows necessary ports
   - Check if ECR images were pushed successfully

3. **Application Not Accessible**:
   - Verify EC2 instance is running
   - Check security group inbound rules
   - Ensure services are running: `docker-compose ps`

4. **Database Connection Issues**:
   - Check PostgreSQL container status
   - Verify database credentials in environment variables
   - Check container networking

### Getting Help:
- Check application logs: `docker-compose logs`
- Monitor GitHub Actions for CI/CD issues
- Review AWS CloudWatch for infrastructure issues

## 📚 Additional Resources

- [AWS Free Tier](https://aws.amazon.com/free/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
