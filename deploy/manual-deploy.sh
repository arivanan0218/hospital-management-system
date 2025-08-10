#!/bin/bash
set -e

echo "🚀 Starting Hospital Management System Deployment..."

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="324037286635"
IMAGE_TAG="latest"

# Navigate to application directory
cd /home/ec2-user
mkdir -p hospital-management
cd hospital-management

echo "📁 Working directory: $(pwd)"

# Download docker-compose file
echo "📥 Downloading docker-compose configuration..."
curl -fsSL -o docker-compose.prod.yml https://raw.githubusercontent.com/arivanan0218/hospital-management-system/dev/docker-compose.prod.yml

# Login to ECR
echo "🔐 Logging into AWS ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true

# Pull latest images
echo "📦 Pulling latest Docker images..."
docker pull $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-backend:$IMAGE_TAG
docker pull $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/hospital-frontend:$IMAGE_TAG

# Set environment variables
export AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID
export AWS_REGION=$AWS_REGION
export IMAGE_TAG=$IMAGE_TAG
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-HospitalSecure2024!}"

# Start containers
echo "🚀 Starting containers..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check container status
echo "📊 Container status:"
docker-compose -f docker-compose.prod.yml ps

# Test if services are responding
echo "🔍 Testing service health..."
timeout 30 bash -c 'until curl -f http://localhost:3000 > /dev/null 2>&1; do echo "Waiting for frontend..."; sleep 2; done' && echo "✅ Frontend is responding"
timeout 30 bash -c 'until curl -f http://localhost:8000/health > /dev/null 2>&1; do echo "Waiting for backend..."; sleep 2; done' && echo "✅ Backend is responding"

# Clean up old images
echo "🧹 Cleaning up old Docker images..."
docker image prune -f

echo "✅ Deployment completed successfully!"
echo "🌐 Application should be available at:"
echo "   Frontend: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3000"
echo "   Backend: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
