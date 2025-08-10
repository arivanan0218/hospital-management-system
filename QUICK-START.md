# 🏥 Hospital Management System - Complete Deployment Guide

## What We've Built

Your hospital management system now has a complete containerized deployment setup with:

- **Frontend**: React app with Nginx (Port 80)
- **Backend**: Python FastAPI with MCP server (Port 8000)
- **Database**: PostgreSQL in Docker container (Port 5432)
- **CI/CD**: GitHub Actions pipeline
- **Infrastructure**: AWS EC2 with automated deployment

## 📋 Step-by-Step Deployment Process

### 1. Prerequisites Setup

First, ensure you have:
- AWS CLI installed and configured
- Valid AWS account with permissions
- GitHub account with this repository

### 2. Get AWS Information

Run this script to get your AWS account details:

```bash
# For Linux/Mac
chmod +x scripts/get-aws-info.sh
./scripts/get-aws-info.sh

# For Windows (use Git Bash or WSL)
bash scripts/get-aws-info.sh
```

### 3. Set Up AWS Infrastructure

```bash
# Make scripts executable
chmod +x scripts/setup-aws.sh
chmod +x scripts/user-data.sh

# Run the AWS setup
cd scripts
./setup-aws.sh
```

This creates:
- ✅ ECR repositories for Docker images
- ✅ EC2 instance with Docker pre-installed
- ✅ Security groups with proper ports
- ✅ SSH key pair for access

### 4. Configure GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions

Add these **required** secrets:

#### AWS Configuration:
```
AWS_ACCESS_KEY_ID: your_aws_access_key
AWS_SECRET_ACCESS_KEY: your_aws_secret_key
AWS_ACCOUNT_ID: your_12_digit_account_id
```

#### EC2 Configuration:
```
EC2_HOST: your_ec2_public_ip
EC2_USER: ubuntu
EC2_SSH_PRIVATE_KEY: content_of_your_pem_file
```

#### Application Configuration:
```
POSTGRES_PASSWORD: YourSecurePassword123!
GEMINI_API_KEY: your_gemini_api_key
```

#### Optional AI API Keys:
```
VITE_OPENAI_API_KEY: your_openai_key
VITE_CLAUDE_API_KEY: your_claude_key
VITE_GROQ_API_KEY: your_groq_key
VITE_GOOGLE_API_KEY: your_google_key
```

### 5. Get Required API Keys

#### 🔑 Gemini API Key (Required)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create new API key
3. Copy and add as `GEMINI_API_KEY` secret

#### 🔑 Optional API Keys
- **OpenAI**: [Platform OpenAI](https://platform.openai.com/api-keys)
- **Claude**: [Anthropic Console](https://console.anthropic.com/)
- **Groq**: [Groq Console](https://console.groq.com/keys)

### 6. Deploy to Production

The deployment is **automatically triggered** when you push to the `dev` branch:

```bash
# Your changes are already committed and pushed!
# Check GitHub Actions tab to monitor deployment
```

### 7. Monitor Deployment

1. Go to GitHub → Actions tab
2. Watch the deployment progress
3. Deployment includes:
   - ✅ Running tests
   - ✅ Building Docker images
   - ✅ Pushing to AWS ECR
   - ✅ Deploying to EC2

### 8. Access Your Application

Once deployed, access at:
- **Frontend**: `http://YOUR_EC2_PUBLIC_IP`
- **Backend API**: `http://YOUR_EC2_PUBLIC_IP:8000`
- **Health Check**: `http://YOUR_EC2_PUBLIC_IP:8000/health`

## 🧪 Test Locally First (Optional)

Before deploying, test locally:

```bash
# For Windows users
powershell scripts/quick-start.ps1

# For Linux/Mac users
cp .env.example .env
# Edit .env with your API keys
docker-compose up -d
```

Access locally at:
- Frontend: http://localhost
- Backend: http://localhost:8000

## 🛠️ Architecture Overview

```
Internet → EC2 Instance → Docker Containers
                       ├── Nginx (Frontend) :80
                       ├── FastAPI (Backend) :8000
                       └── PostgreSQL (Database) :5432
```

## 🔍 Troubleshooting

### Check Deployment Status
```bash
# SSH into EC2
ssh -i hospital-key-pair.pem ubuntu@YOUR_EC2_IP

# Check containers
docker ps

# View logs
docker-compose logs -f

# Check health
curl http://localhost:8000/health
```

### Common Issues & Solutions

1. **GitHub Actions Failing**
   - ❌ Missing secrets → Add all required secrets
   - ❌ Wrong AWS permissions → Check IAM policies
   - ❌ EC2 not accessible → Check security groups

2. **Application Not Loading**
   - ❌ Database connection → Check `POSTGRES_PASSWORD`
   - ❌ API keys invalid → Verify and regenerate keys
   - ❌ Docker not running → SSH and check `docker ps`

3. **Health Check Failing**
   - ❌ Backend not started → Check backend logs
   - ❌ Database connection → Verify PostgreSQL container

## 📊 Production Checklist

Before going live:
- ✅ All GitHub secrets configured
- ✅ Valid API keys added
- ✅ AWS infrastructure created
- ✅ SSH access tested
- ✅ Health checks passing
- ✅ Application accessible

## 🚀 What's Next?

Your system is now production-ready! Consider these enhancements:

1. **SSL Certificate**: Add HTTPS with Let's Encrypt
2. **Domain Name**: Point a domain to your EC2 IP
3. **Monitoring**: Set up CloudWatch alerts
4. **Backup**: Automated database backups
5. **Scaling**: Load balancer for multiple instances

## 🆘 Need Help?

If you encounter issues:

1. **Check GitHub Actions logs** for build/deployment errors
2. **SSH into EC2** to check application logs
3. **Verify all secrets** are correctly set in GitHub
4. **Test API keys** independently to ensure they work

## 🎉 Congratulations!

You've successfully deployed a complete hospital management system with:
- ✅ Containerized architecture
- ✅ Automated CI/CD pipeline
- ✅ Cloud infrastructure
- ✅ Scalable database
- ✅ Production-ready setup

Your hospital management system is now live and ready for use!
