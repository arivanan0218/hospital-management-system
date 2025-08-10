#!/bin/bash

# EC2 User Data Script
# This script runs when the EC2 instance first starts

# Update system
apt-get update -y
apt-get upgrade -y

# Install Docker
apt-get install -y docker.io docker-compose-plugin
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install AWS CLI
apt-get install -y awscli

# Install other useful tools
apt-get install -y curl wget git htop unzip

# Create application directory
mkdir -p /home/ubuntu/hospital-app
chown ubuntu:ubuntu /home/ubuntu/hospital-app

# Install Node.js (for any additional tools)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt-get install -y nodejs

echo "EC2 instance setup complete!" > /home/ubuntu/setup-complete.txt
