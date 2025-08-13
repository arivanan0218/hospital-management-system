# EC2 Disk Space Management Guide

## Problem: "no space left on device" during deployment

This error occurs when your EC2 instance runs out of disk space during Docker operations. Here are immediate and long-term solutions:

## 🚨 Immediate Solutions

### 1. Run Emergency Cleanup Script
```bash
# SSH into your EC2 instance
ssh -i hospital-key.pem ec2-user@your-ec2-ip

# Run the emergency cleanup script
chmod +x emergency-cleanup.sh
./emergency-cleanup.sh
```

### 2. Manual Cleanup Commands
If the script fails, run these commands manually:

```bash
# Stop all Docker containers
sudo docker stop $(sudo docker ps -aq)

# Remove all Docker containers and images
sudo docker system prune -af --volumes

# Clean package cache
sudo apt-get clean && sudo apt-get autoremove -y

# Remove temporary files
sudo rm -rf /tmp/* /var/tmp/*

# Clean logs
sudo journalctl --vacuum-time=3d
```

### 3. Check Disk Usage
```bash
# Check overall disk usage
df -h

# Check which directories are using most space
sudo du -sh /* | sort -hr | head -10

# Check Docker space usage
sudo docker system df
```

## 🔧 Long-term Solutions

### 1. Increase EBS Volume Size

#### Option A: Using AWS Console
1. Go to AWS Console → EC2 → Volumes
2. Select your volume and click "Modify Volume"
3. Increase size to at least 20GB (recommended: 30GB)
4. After modification, SSH into EC2 and run:
```bash
sudo resize2fs /dev/xvda1
```

#### Option B: Using AWS CLI
```bash
# Get volume ID
aws ec2 describe-instances --instance-ids i-your-instance-id

# Modify volume size to 20GB
aws ec2 modify-volume --volume-id vol-your-volume-id --size 20

# Resize filesystem
sudo resize2fs /dev/xvda1
```

### 2. Automated Cleanup Cron Job

Create a daily cleanup cron job:

```bash
# Edit crontab
sudo crontab -e

# Add this line for daily cleanup at 2 AM
0 2 * * * /home/ec2-user/emergency-cleanup.sh >> /var/log/cleanup.log 2>&1
```

### 3. Docker Image Optimization

#### Optimize Frontend Dockerfile
```dockerfile
# Use multi-stage build to reduce image size
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Use nginx for serving
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

#### Optimize Backend Dockerfile
```dockerfile
FROM python:3.10-slim
WORKDIR /app

# Install only production dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### 4. Enhanced GitHub Actions Workflow

The workflow has been updated with better cleanup, but you can also:

#### Use Docker BuildKit for more efficient builds:
```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push with cache
  uses: docker/build-push-action@v5
  with:
    context: ./frontend
    push: true
    tags: ${{ env.ECR_REGISTRY }}/hospital-frontend:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## 📊 Monitoring and Prevention

### 1. Set up CloudWatch Alarms
```bash
# Create alarm for disk usage > 80%
aws cloudwatch put-metric-alarm \
  --alarm-name "EC2-DiskSpace-High" \
  --alarm-description "Disk space usage high" \
  --metric-name DiskSpaceUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

### 2. Regular Monitoring Script
Create a monitoring script (`monitor-disk.sh`):
```bash
#!/bin/bash
usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $usage -gt 80 ]; then
    echo "⚠️  Disk usage is ${usage}% - cleanup recommended"
    # Send notification or trigger cleanup
fi
```

### 3. Docker Image Size Analysis
```bash
# Check image sizes
sudo docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Analyze layers
sudo docker history image-name:tag
```

## 🚀 Recommended EC2 Instance Specs

For Hospital Management System:

### Minimum (Development)
- Instance Type: t3.small
- Storage: 20GB GP3
- Memory: 2GB

### Recommended (Production)
- Instance Type: t3.medium or t3.large
- Storage: 30-50GB GP3
- Memory: 4-8GB

### High Traffic (Production)
- Instance Type: t3.xlarge
- Storage: 50-100GB GP3
- Memory: 16GB

## 🔍 Troubleshooting Common Issues

### 1. "Cannot connect to Docker daemon"
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. "Permission denied" during cleanup
```bash
sudo chmod +x emergency-cleanup.sh
sudo chown ec2-user:ec2-user emergency-cleanup.sh
```

### 3. "No space left on device" during npm install
```bash
# Clear npm cache
npm cache clean --force
# Or use emergency cleanup script
```

### 4. Docker build fails with memory issues
```bash
# Add swap space temporarily
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📞 Emergency Contacts

If you continue to have disk space issues:

1. Check AWS Cost Explorer for unexpected charges
2. Consider upgrading to a larger instance type
3. Review application logs for excessive logging
4. Contact AWS Support if volume modification fails

## 📝 Best Practices

1. **Monitor disk usage weekly**
2. **Run cleanup scripts regularly**
3. **Use multi-stage Docker builds**
4. **Implement log rotation**
5. **Set up CloudWatch alarms**
6. **Regular backup and cleanup schedules**

---

**Remember**: Prevention is better than cure. Regular monitoring and cleanup prevent emergency situations!
