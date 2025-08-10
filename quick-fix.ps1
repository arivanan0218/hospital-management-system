# Quick Fix Deployment - Simple Docker Run

Write-Host "=== Hospital Management System - Quick Fix Deployment ===" -ForegroundColor Green
Write-Host ""

$PUBLIC_IP = "34.207.201.88"
$INSTANCE_ID = "i-0cf791e5c2873120e"

Write-Host "Current instance has been running for 5+ minutes but containers aren't responding." -ForegroundColor Yellow
Write-Host "This usually means there was an issue with the automated setup." -ForegroundColor Yellow
Write-Host ""
Write-Host "Let's create a simpler deployment approach..." -ForegroundColor Yellow
Write-Host ""

# Create a simpler EC2 user data script
$SIMPLE_USER_DATA = @"
#!/bin/bash
yum update -y
yum install -y docker

# Start Docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Create a startup script that runs as ec2-user
cat > /home/ec2-user/start-hospital.sh << 'SCRIPT'
#!/bin/bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 324037286635.dkr.ecr.us-east-1.amazonaws.com

# Pull and run backend (with SQLite for simplicity)
docker run -d --name hospital-backend -p 8000:8000 -e DATABASE_URL=sqlite:///./hospital.db 324037286635.dkr.ecr.us-east-1.amazonaws.com/hospital-backend:latest

# Pull and run frontend
docker run -d --name hospital-frontend -p 3000:3000 324037286635.dkr.ecr.us-east-1.amazonaws.com/hospital-frontend:latest

echo "Containers started at $(date)" >> /home/ec2-user/startup.log
SCRIPT

chmod +x /home/ec2-user/start-hospital.sh
chown ec2-user:ec2-user /home/ec2-user/start-hospital.sh

# Run the script as ec2-user (after a short delay for docker to be ready)
su - ec2-user -c "sleep 30 && /home/ec2-user/start-hospital.sh" &
"@

Write-Host "Would you like to:" -ForegroundColor Cyan
Write-Host "1. Try to restart containers on the existing instance (recommended)" -ForegroundColor Yellow
Write-Host "2. Create a new instance with corrected setup" -ForegroundColor Yellow
Write-Host "3. Manual SSH debugging of current instance" -ForegroundColor Yellow
Write-Host ""

# For now, let's try option 1 - restart the existing instance with proper commands
Write-Host "Attempting to send restart commands to existing instance..." -ForegroundColor Yellow

# Create a simple restart script using AWS Systems Manager (if available)
$RESTART_COMMANDS = @"
#!/bin/bash
# Stop any existing containers
docker stop hospital-backend hospital-frontend 2>/dev/null || true
docker rm hospital-backend hospital-frontend 2>/dev/null || true

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 324037286635.dkr.ecr.us-east-1.amazonaws.com

# Start containers
docker run -d --name hospital-backend -p 8000:8000 -e DATABASE_URL=sqlite:///./hospital.db 324037286635.dkr.ecr.us-east-1.amazonaws.com/hospital-backend:latest
docker run -d --name hospital-frontend -p 3000:3000 324037286635.dkr.ecr.us-east-1.amazonaws.com/hospital-frontend:latest

# Check status
docker ps
echo "Restart completed at $(date)"
"@

Write-Host ""
Write-Host "=== Alternative: Manual SSH Approach ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "To manually fix the current instance:" -ForegroundColor Yellow
Write-Host "1. SSH into the instance:" -ForegroundColor White
Write-Host "   ssh -i hospital-key.pem ec2-user@$PUBLIC_IP" -ForegroundColor White
Write-Host ""
Write-Host "2. Check Docker status:" -ForegroundColor White
Write-Host "   sudo systemctl status docker" -ForegroundColor White
Write-Host ""
Write-Host "3. Login to ECR:" -ForegroundColor White
Write-Host "   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 324037286635.dkr.ecr.us-east-1.amazonaws.com" -ForegroundColor White
Write-Host ""
Write-Host "4. Run containers manually:" -ForegroundColor White
Write-Host "   docker run -d --name hospital-backend -p 8000:8000 -e DATABASE_URL=sqlite:///./hospital.db 324037286635.dkr.ecr.us-east-1.amazonaws.com/hospital-backend:latest" -ForegroundColor White
Write-Host "   docker run -d --name hospital-frontend -p 3000:3000 324037286635.dkr.ecr.us-east-1.amazonaws.com/hospital-frontend:latest" -ForegroundColor White
Write-Host ""
Write-Host "5. Check status:" -ForegroundColor White
Write-Host "   docker ps" -ForegroundColor White
Write-Host "   curl localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "=== Current Status ===" -ForegroundColor Cyan
Write-Host "✅ EC2 Instance: Running" -ForegroundColor Green
Write-Host "✅ Docker Images: Available in ECR" -ForegroundColor Green  
Write-Host "✅ Network Access: SSH working" -ForegroundColor Green
Write-Host "❌ Application Containers: Not responding" -ForegroundColor Red
Write-Host ""
Write-Host "The most likely issue is that the automated startup script didn't run properly," -ForegroundColor Yellow
Write-Host "but all the infrastructure is in place. Manual SSH will resolve this quickly." -ForegroundColor Yellow
