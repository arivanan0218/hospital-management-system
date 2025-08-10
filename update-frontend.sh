#!/bin/bash

# Update Frontend Container Script
echo "🔄 Updating frontend container with latest image..."

# Stop and remove current frontend container
echo "Stopping current frontend container..."
sudo docker stop hospital-frontend 2>/dev/null || true
sudo docker rm hospital-frontend 2>/dev/null || true

# Pull latest image
echo "Pulling latest frontend image..."
sudo docker pull 324037286635.dkr.ecr.us-east-1.amazonaws.com/hospital-frontend:latest

# Start new frontend container
echo "Starting new frontend container..."
sudo docker run -d \
  --name hospital-frontend \
  --network hospital-network \
  --restart unless-stopped \
  324037286635.dkr.ecr.us-east-1.amazonaws.com/hospital-frontend:latest

echo "✅ Frontend container updated successfully!"

# Show running containers
echo "📋 Current running containers:"
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
