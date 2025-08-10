# Hospital Management System - AWS Deployment Guide


This guide will walk you through deploying your Hospital Management System to AWS using GitHub Actions, Docker, and EC2.

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **GitHub Account** with this repository
3. **Local AWS CLI** installed and configured
4. **API Keys** for AI services (at least Gemini API key is required)

## Step-by-Step Deployment Process

### 1. Set Up AWS Infrastructure

First, run the AWS setup script to create the necessary infrastructure:

```bash
# Make the script executable
chmod +x scripts/setup-aws.sh
chmod +x scripts/user-data.sh

# Run the setup script
cd scripts
./setup-aws.sh
```

This script will create:
- ECR repositories for your Docker images
- EC2 instance with Docker installed
- Security groups with proper ports open
- SSH key pair for access

### 2. Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions, and add these secrets:

#### AWS Configuration:
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_ACCOUNT_ID`: Your 12-digit AWS account ID

#### EC2 Configuration:
- `EC2_HOST`: Public IP of your EC2 instance (from setup script output)
- `EC2_USER`: `ubuntu`
- `EC2_SSH_PRIVATE_KEY`: Contents of the generated `.pem` file

#### Application Configuration:
- `POSTGRES_PASSWORD`: Secure password for PostgreSQL (e.g., `MySecurePassword123!`)
- `GEMINI_API_KEY`: Your Google Gemini API key (required)

#### Optional AI API Keys:
- `VITE_OPENAI_API_KEY`: OpenAI API key
- `VITE_CLAUDE_API_KEY`: Anthropic Claude API key
- `VITE_GROQ_API_KEY`: Groq API key
- `VITE_GOOGLE_API_KEY`: Google AI API key

### 3. Get Required API Keys

#### Gemini API Key (Required):
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key and add it as `GEMINI_API_KEY` secret

#### Optional API Keys:
- **OpenAI**: [OpenAI API Keys](https://platform.openai.com/api-keys)
- **Claude**: [Anthropic Console](https://console.anthropic.com/)
- **Groq**: [Groq Console](https://console.groq.com/keys)

### 4. Update Environment Configuration

Create a `.env` file locally for development:

```bash
# Copy the example file
cp .env.example .env

# Edit with your values
nano .env
```

Fill in at least the `GEMINI_API_KEY` and `POSTGRES_PASSWORD`.

### 5. Test Locally (Optional)

Before deploying, you can test the application locally:

```bash
# Start the application
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f

# Access the application at http://localhost
```

### 6. Deploy to GitHub

Push your changes to the `dev` branch to trigger deployment:

```bash
# Add all files
git add .

# Commit changes
git commit -m "Add Docker configuration and CI/CD pipeline"

# Push to dev branch (this will trigger deployment)
git push origin dev
```

### 7. Monitor Deployment

1. Go to your GitHub repository → Actions tab
2. Watch the CI/CD pipeline run
3. The deployment process includes:
   - Running tests
   - Building Docker images
   - Pushing to ECR
   - Deploying to EC2

### 8. Access Your Application

Once deployment is complete:

1. **Frontend**: `http://YOUR_EC2_PUBLIC_IP`
2. **Backend API**: `http://YOUR_EC2_PUBLIC_IP:8000`
3. **Health Check**: `http://YOUR_EC2_PUBLIC_IP:8000/health`

## Application Components

### Services Running:
1. **PostgreSQL Database** (Port 5432) - Dockerized database
2. **Backend Python API** (Port 8000) - FastAPI with MCP server
3. **Frontend React App** (Port 80) - Nginx serving React build

### Database:
- **Type**: PostgreSQL 15 (Docker container)
- **Data Persistence**: Docker volume (`postgres_data`)
- **Initialization**: Automatic schema creation on first run

## Troubleshooting

### Check Application Status:
```bash
# SSH into your EC2 instance
ssh -i hospital-key-pair.pem ubuntu@YOUR_EC2_PUBLIC_IP

# Check running containers
docker ps

# View logs
docker-compose logs -f

# Check container health
docker-compose ps
```

### Common Issues:

1. **Database Connection Failed**:
   - Check if PostgreSQL container is running
   - Verify `POSTGRES_PASSWORD` secret is set correctly

2. **API Keys Not Working**:
   - Verify API keys are valid and have sufficient quota
   - Check GitHub secrets are set correctly

3. **Docker Build Fails**:
   - Check Dockerfile syntax
   - Ensure all dependencies are correctly specified

4. **EC2 Access Issues**:
   - Verify security group allows ports 22, 80, and 8000
   - Check SSH key permissions (`chmod 400 hospital-key-pair.pem`)

### Useful Commands:

```bash
# Restart services
docker-compose restart

# Rebuild and restart
docker-compose up -d --build

# View database logs
docker-compose logs db

# Access database directly
docker-compose exec db psql -U postgres -d hospital_management
```

## Security Considerations

1. **API Keys**: Store securely in GitHub secrets, never commit to code
2. **Database**: Use strong passwords, consider encryption for production
3. **SSH Access**: Use key-based authentication, restrict source IPs if possible
4. **HTTPS**: Consider adding SSL certificate for production use

## Scaling and Production

For production environments, consider:

1. **Load Balancer**: Use AWS Application Load Balancer
2. **Auto Scaling**: Set up EC2 Auto Scaling groups
3. **Database**: Consider RDS for managed PostgreSQL
4. **Monitoring**: Set up CloudWatch for monitoring and alerts
5. **Backup**: Implement automated database backups
6. **SSL/HTTPS**: Use AWS Certificate Manager for SSL certificates

## Support

If you encounter issues:

1. Check the GitHub Actions logs for deployment errors
2. SSH into the EC2 instance to check application logs
3. Verify all required secrets are configured in GitHub
4. Test API keys independently to ensure they're working

## Next Steps

After successful deployment:

1. Set up monitoring and alerting
2. Configure automated backups
3. Implement proper logging and error tracking
4. Consider setting up a staging environment
5. Add more comprehensive tests to the CI/CD pipeline
