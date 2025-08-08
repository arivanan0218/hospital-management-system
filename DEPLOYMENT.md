# Hospital Management System - AWS Deployment Guide

This guide will walk you through deploying the Hospital Management System to AWS using GitHub Actions for CI/CD.

## 🏗️ Architecture Overview

The application will be deployed on AWS using:
- **Amazon ECS (Fargate)** - Container orchestration
- **Amazon ECR** - Container registry
- **Application Load Balancer** - Load balancing and routing
- **Amazon VPC** - Isolated network environment
- **GitHub Actions** - CI/CD pipeline

## 📋 Prerequisites

Before starting, ensure you have:

1. **AWS Account** with administrative access
2. **AWS CLI** installed and configured
3. **GitHub repository** (already set up)
4. **Docker** installed locally (for testing)
5. **API Keys** for AI services:
   - Gemini API Key (required)
   - OpenAI API Key (optional)
   - Claude API Key (optional)
   - Groq API Key (optional)
   - Google API Key (optional)

## 🚀 Deployment Steps

### Step 1: Set up AWS Infrastructure

1. **Configure AWS CLI** (if not already done):
   ```bash
   aws configure
   ```
   Enter your AWS Access Key ID, Secret Access Key, and default region (us-east-1).

2. **Run the infrastructure setup script**:
   ```bash
   cd aws-setup
   chmod +x setup-infrastructure.sh
   ./setup-infrastructure.sh
   ```

   This script will create:
   - VPC with public subnets
   - Security groups
   - Application Load Balancer
   - ECR repositories
   - ECS cluster
   - IAM roles

3. **Note the output values** - you'll need them for the next step.

### Step 2: Create ECS Task Definition and Service

1. **Update the create-task-definition.sh script** with the values from Step 1:
   ```bash
   # Edit create-task-definition.sh and replace:
   TARGET_GROUP_ARN="YOUR_TARGET_GROUP_ARN"
   SUBNET_1_ID="YOUR_SUBNET_1_ID"
   SUBNET_2_ID="YOUR_SUBNET_2_ID"
   SG_ID="YOUR_SECURITY_GROUP_ID"
   ```

2. **Update task-definition.json** with your API keys:
   ```bash
   # Edit task-definition.json and replace:
   "YOUR_GEMINI_API_KEY" with your actual Gemini API key
   "YOUR_CLAUDE_API_KEY" with your actual Claude API key
   # ... and other API keys
   ```

3. **Run the task definition creation script**:
   ```bash
   chmod +x create-task-definition.sh
   ./create-task-definition.sh
   ```

### Step 3: Set up GitHub Secrets

In your GitHub repository, go to Settings > Secrets and variables > Actions, and add these secrets:

```
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
GEMINI_API_KEY=your_gemini_api_key
VITE_OPENAI_API_KEY=your_openai_api_key (optional)
VITE_CLAUDE_API_KEY=your_claude_api_key (optional)
VITE_GROQ_API_KEY=your_groq_api_key (optional)
VITE_GOOGLE_API_KEY=your_google_api_key (optional)
```

### Step 4: Deploy via GitHub Actions

1. **Push your code to the docker branch**:
   ```bash
   git add .
   git commit -m "Add CI/CD pipeline and AWS deployment configuration"
   git push origin docker
   ```

2. **Monitor the deployment**:
   - Go to your GitHub repository
   - Click on the "Actions" tab
   - Watch the "Deploy from Docker Branch" workflow run

3. **Check your application**:
   - Once the deployment is complete, get your Application Load Balancer DNS name:
     ```bash
     aws elbv2 describe-load-balancers --names hospital-alb --query 'LoadBalancers[0].DNSName' --output text
     ```
   - Open the DNS name in your browser to access your application

## 🔧 Configuration

### Environment Variables

The application uses the following environment variables:

**Backend (Python)**:
- `DATABASE_URL` - PostgreSQL connection string
- `GEMINI_API_KEY` - Required for AI features

**Frontend (React)**:
- `VITE_MCP_BRIDGE_URL` - URL to the MCP process manager
- `VITE_CLAUDE_API_KEY` - Claude AI API key (optional)
- `VITE_OPENAI_API_KEY` - OpenAI API key (optional)
- `VITE_GROQ_API_KEY` - Groq API key (optional)
- `VITE_GOOGLE_API_KEY` - Google AI API key (optional)

**MCP Process Manager**:
- `PORT` - Server port (3001)
- `NODE_ENV` - Environment (production)
- `DATABASE_URL` - PostgreSQL connection string

### Scaling

To scale your application:

```bash
# Scale the ECS service
aws ecs update-service \
    --cluster hospital-cluster \
    --service hospital-management-service \
    --desired-count 3
```

### Monitoring

Check your application logs:

```bash
# View service status
aws ecs describe-services \
    --cluster hospital-cluster \
    --services hospital-management-service

# View task logs in CloudWatch
aws logs get-log-events \
    --log-group-name /ecs/hospital-management \
    --log-stream-name frontend/hospital-frontend/TASK_ID
```

## 🛠️ Troubleshooting

### Common Issues

1. **Task Definition Registration Fails**:
   - Check that all ECR repositories exist
   - Verify IAM roles are created correctly
   - Ensure account ID is correctly replaced in task-definition.json

2. **Service Won't Start**:
   - Check CloudWatch logs for container errors
   - Verify security group allows necessary ports
   - Ensure subnets have internet access

3. **Application Not Accessible**:
   - Check Application Load Balancer health checks
   - Verify target group configuration
   - Ensure containers are running on correct ports

4. **GitHub Actions Fails**:
   - Verify all secrets are set correctly
   - Check that ECR repositories exist
   - Ensure AWS credentials have necessary permissions

### Useful Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster hospital-cluster --services hospital-management-service

# View running tasks
aws ecs list-tasks --cluster hospital-cluster --service-name hospital-management-service

# Get load balancer DNS
aws elbv2 describe-load-balancers --names hospital-alb --query 'LoadBalancers[0].DNSName' --output text

# Check target group health
aws elbv2 describe-target-health --target-group-arn YOUR_TARGET_GROUP_ARN
```

## 🔄 CI/CD Pipeline

The GitHub Actions workflow:

1. **Test Phase**:
   - Runs unit tests for Python backend
   - Runs tests for Node.js MCP manager
   - Builds the React frontend

2. **Build Phase** (only on main branch):
   - Builds Docker images for all services
   - Pushes images to Amazon ECR
   - Tags images with git commit SHA and 'latest'

3. **Deploy Phase**:
   - Updates ECS task definition with new image tags
   - Deploys updated task definition to ECS service
   - Waits for deployment to stabilize

## 📱 Application Access

Once deployed, your Hospital Management System will be available at:
- **Frontend**: `http://YOUR_ALB_DNS_NAME`
- **Backend API**: `http://YOUR_ALB_DNS_NAME:8000`
- **MCP Manager**: `http://YOUR_ALB_DNS_NAME:3001`

## 💰 Cost Optimization

To minimize AWS costs:

1. **Use appropriate instance sizes** - Start with the smallest Fargate configuration
2. **Set up auto-scaling** - Scale down during low usage periods
3. **Use CloudWatch alarms** - Monitor and alert on unusual usage
4. **Regular cleanup** - Remove unused ECR images and CloudWatch logs

## 🔒 Security Best Practices

1. **Use AWS Secrets Manager** for sensitive data instead of environment variables
2. **Enable VPC Flow Logs** for network monitoring
3. **Set up AWS WAF** for web application firewall protection
4. **Use HTTPS** with SSL certificates from AWS Certificate Manager
5. **Implement least privilege IAM policies**

## 📈 Next Steps

1. **Set up custom domain** with Route 53 and SSL certificate
2. **Implement backup strategies** for your database
3. **Set up monitoring and alerting** with CloudWatch
4. **Configure auto-scaling** based on CPU/memory usage
5. **Implement blue-green deployments** for zero-downtime updates
