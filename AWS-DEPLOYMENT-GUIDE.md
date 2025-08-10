# 🏥 Hospital Management System - Complete AWS Deployment Guide

This guide will walk you through deploying your Hospital Management System to AWS using GitHub Actions for CI/CD, completely free using AWS Free Tier.

## 📋 Prerequisites

Before starting, make sure you have:
- A GitHub account
- An AWS account (sign up at https://aws.amazon.com/free/)
- Git installed on your computer
- Docker installed (for local testing)

## 🚀 Step-by-Step Deployment Process

### Phase 1: AWS Account Setup

#### Step 1: Create AWS Account
1. Go to [AWS Free Tier](https://aws.amazon.com/free/)
2. Click "Create a Free Account"
3. Fill in your details (email, password, account name)
4. Add a payment method (required even for free tier, but you won't be charged for free tier usage)
5. Verify your phone number
6. Choose "Basic Support - Free"

#### Step 2: Install AWS CLI
**Windows (PowerShell):**
```powershell
# Download and install AWS CLI v2
Invoke-WebRequest -Uri "https://awscli.amazonaws.com/AWSCLIV2.msi" -OutFile "AWSCLIV2.msi"
Start-Process msiexec.exe -Wait -ArgumentList '/I AWSCLIV2.msi /quiet'
```

**Verify installation:**
```powershell
aws --version
```

#### Step 3: Create IAM User for Deployment
1. Go to AWS Console → IAM → Users
2. Click "Create user"
3. Username: `hospital-deploy-user`
4. Select "Programmatic access"
5. Attach policies:
   - `PowerUserAccess` (for this tutorial - in production, use more restricted permissions)
6. Download the CSV file with access keys
7. **IMPORTANT**: Save the Access Key ID and Secret Access Key securely

#### Step 4: Configure AWS CLI
```powershell
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key
# Default region: us-east-1
# Default output format: json
```

### Phase 2: Prepare Your Code

#### Step 5: Create GitHub Repository
1. Go to GitHub and create a new repository named `hospital-management-system`
2. Make it public (required for free GitHub Actions)
3. Don't initialize with README (we'll push existing code)

#### Step 6: Push Your Code to GitHub
```powershell
# Navigate to your project directory
cd "C:\Users\Arivanan\hospital-management-system"

# Initialize git if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit - Hospital Management System"

# Add GitHub remote (replace YOUR-USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR-USERNAME/hospital-management-system.git

# Push to GitHub
git push -u origin main
```

### Phase 3: Set up GitHub Secrets

#### Step 7: Add GitHub Secrets
1. Go to your GitHub repository
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret" and add:

| Secret Name | Value |
|-------------|-------|
| `AWS_ACCESS_KEY_ID` | Your AWS Access Key ID from Step 3 |
| `AWS_SECRET_ACCESS_KEY` | Your AWS Secret Access Key from Step 3 |

### Phase 4: Deploy Infrastructure

#### Step 8: Deploy AWS Infrastructure
Run the deployment script in PowerShell:

```powershell
# Make sure you're in the project directory
cd "C:\Users\Arivanan\hospital-management-system"

# Run the deployment script
.\deploy-to-aws.ps1
```

This script will:
- ✅ Create VPC, subnets, security groups
- ✅ Set up RDS PostgreSQL database
- ✅ Create ECR repositories for Docker images
- ✅ Set up ECS cluster and services
- ✅ Create Application Load Balancer
- ✅ Configure CloudWatch logging

**Expected output:**
```
🏥 Hospital Management System - AWS Deployment
==============================================
✅ AWS Account ID: 123456789012
✅ AWS Region: us-east-1
📋 Step 1: Creating AWS Infrastructure...
✅ Infrastructure created successfully!
🔐 Step 2: Setting up database password...
✅ Database password stored in SSM Parameter Store
🗄️ Step 3: Getting database endpoint...
✅ Database endpoint: hospital-postgres.xxxxx.us-east-1.rds.amazonaws.com
✅ Load balancer DNS: hospital-alb-xxxxx.us-east-1.elb.amazonaws.com
📝 Step 5: Updating task definitions...
✅ Task definitions updated
📊 Step 6: Creating CloudWatch log groups...
✅ CloudWatch log groups created
🎉 Initial setup completed!
🌐 Your application will be available at: http://hospital-alb-xxxxx.us-east-1.elb.amazonaws.com
```

### Phase 5: Automatic Deployment with GitHub Actions

#### Step 9: Trigger Deployment
Now that infrastructure is set up, GitHub Actions will handle deployments:

1. Make any change to your code
2. Commit and push:
```powershell
git add .
git commit -m "Trigger deployment"
git push
```

3. Go to GitHub → your repository → "Actions" tab
4. Watch the deployment process

### Phase 6: Verify Deployment

#### Step 10: Check Your Application
1. **Wait 5-10 minutes** for services to start
2. Visit the ALB DNS name from Step 8 output
3. Your application should be running!

#### Step 11: Monitor Services
**Check ECS Services:**
```powershell
aws ecs describe-services --cluster hospital-cluster --services hospital-backend-service hospital-frontend-service
```

**Check Logs:**
```powershell
# Backend logs
aws logs tail /ecs/hospital-backend --follow

# Frontend logs  
aws logs tail /ecs/hospital-frontend --follow
```

## 🔧 Troubleshooting

### Common Issues:

1. **Services won't start**
   - Check CloudWatch logs in AWS Console
   - Verify environment variables in task definitions

2. **Database connection issues**
   - Ensure security groups allow traffic on port 5432
   - Check RDS instance status

3. **GitHub Actions failing**
   - Verify AWS secrets are correctly set
   - Check Actions tab for error details

### Useful Commands:

```powershell
# Check AWS resources
aws cloudformation describe-stacks --stack-name hospital-infrastructure

# Check ECS service status
aws ecs describe-services --cluster hospital-cluster --services hospital-backend-service

# View recent logs
aws logs tail /ecs/hospital-backend --since 1h

# Update service (force new deployment)
aws ecs update-service --cluster hospital-cluster --service hospital-backend-service --force-new-deployment
```

## 💰 Cost Breakdown (Free Tier)

All services used are within AWS Free Tier limits:

- ✅ **RDS PostgreSQL**: db.t3.micro (750 hours/month free)
- ✅ **ECS Fargate**: 20GB storage + compute (free tier eligible)
- ✅ **Application Load Balancer**: 750 hours/month free
- ✅ **CloudWatch Logs**: 5GB/month free
- ✅ **ECR**: 500MB storage/month free

**Estimated monthly cost: $0** (within free tier limits)

## 🔄 Making Updates

To update your application:

1. Make changes to your code
2. Commit and push to GitHub:
```powershell
git add .
git commit -m "Your update message"
git push
```
3. GitHub Actions automatically builds and deploys
4. No manual intervention needed!

## 🛡️ Security Best Practices

1. **Rotate AWS keys regularly**
2. **Use least privilege IAM policies** (after testing)
3. **Enable CloudTrail for audit logging**
4. **Set up AWS Config for compliance monitoring**
5. **Use HTTPS in production** (add SSL certificate to ALB)

## 📞 Support

If you encounter issues:
1. Check CloudWatch logs first
2. Review GitHub Actions logs
3. Verify AWS service status
4. Check security group rules

Your Hospital Management System is now running on AWS with automated CI/CD! 🎉
