# 🚀 Quick Start Guide

This is a quick start guide to get your Hospital Management System up and running either locally or on AWS.

## 🏠 Local Development (5 minutes)

### Windows
```batch
setup-local.bat
```

### Linux/macOS
```bash
chmod +x setup-local.sh
./setup-local.sh
```

Then:
1. Edit `.env` file with your API keys
2. Run `docker-compose restart`
3. Visit http://localhost

## ☁️ AWS Deployment (30 minutes)

### Prerequisites
- AWS Account with admin access
- AWS CLI configured
- Domain name (optional)

### Quick Deploy
1. **Set up AWS infrastructure**:
   ```bash
   cd aws-setup
   chmod +x setup-infrastructure.sh
   ./setup-infrastructure.sh
   ```

2. **Create ECS service** (update the script with output values from step 1):
   ```bash
   # Edit create-task-definition.sh with your values
   chmod +x create-task-definition.sh
   ./create-task-definition.sh
   ```

3. **Set up GitHub secrets**:
   - Go to GitHub repo > Settings > Secrets and variables > Actions
   - Add: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `GEMINI_API_KEY`, etc.

4. **Deploy**:
   ```bash
   git add .
   git commit -m "Deploy to AWS"
   git push origin docker
   ```

5. **Get your URL**:
   ```bash
   aws elbv2 describe-load-balancers --names hospital-alb --query 'LoadBalancers[0].DNSName' --output text
   ```

## 🔧 Configuration

### Required
- `GEMINI_API_KEY` - For AI features

### Optional
- `VITE_OPENAI_API_KEY` - OpenAI integration
- `VITE_CLAUDE_API_KEY` - Claude integration  
- `VITE_GROQ_API_KEY` - Groq integration
- `VITE_GOOGLE_API_KEY` - Google AI integration

## 📚 Detailed Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete AWS deployment guide
- **[README.md](README.md)** - Full project documentation

## 🆘 Need Help?

1. Check the logs: `docker-compose logs -f`
2. Restart services: `docker-compose restart`
3. Clean rebuild: `docker-compose down && docker-compose up --build`

## 🎯 Next Steps

1. **Secure your deployment** - Set up HTTPS and custom domain
2. **Monitor your app** - CloudWatch alerts and logging
3. **Scale as needed** - ECS auto-scaling configuration
4. **Backup strategy** - Database backup automation
