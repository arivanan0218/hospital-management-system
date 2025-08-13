#!/bin/bash

echo "🚨 EMERGENCY DISK CLEANUP SCRIPT 🚨"
echo "=================================="

echo "📊 Disk space BEFORE cleanup:"
df -h

echo ""
echo "🛑 Step 0: Stopping all Docker containers to free resources..."
sudo docker stop $(sudo docker ps -aq) 2>/dev/null || true

echo ""
echo "🧹 Step 1: Cleaning Docker images and containers..."
sudo docker container prune -f
sudo docker image prune -af
sudo docker system prune -af --volumes
sudo docker volume prune -f
sudo docker network prune -f

echo ""
echo "🧹 Step 2: Cleaning package cache..."
sudo apt-get clean
sudo apt-get autoclean
sudo apt-get autoremove --purge -y
sudo rm -rf /var/lib/apt/lists/*
sudo rm -rf /var/cache/apt/*

echo ""
echo "🧹 Step 3: Cleaning temporary files..."
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*

echo ""
echo "🧹 Step 4: Cleaning journal logs..."
sudo journalctl --vacuum-size=50M
sudo journalctl --vacuum-time=3d

echo ""
echo "🧹 Step 5: Cleaning old kernels..."
sudo apt-get autoremove --purge -y

echo ""
echo "🧹 Step 6: Cleaning build artifacts..."
sudo find /home -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
sudo find /home -name "dist" -type d -exec rm -rf {} + 2>/dev/null || true
sudo find /home -name ".cache" -type d -exec rm -rf {} + 2>/dev/null || true
sudo find /home -name ".npm" -type d -exec rm -rf {} + 2>/dev/null || true

echo ""
echo "🧹 Step 7: Cleaning old log files..."
sudo find /var/log -type f -name "*.log" -mtime +3 -delete 2>/dev/null || true
sudo find /var/log -type f -name "*.gz" -mtime +3 -delete 2>/dev/null || true

echo ""
echo "🧹 Step 8: Cleaning swap..."
sudo swapoff -a 2>/dev/null || true
sudo swapon -a 2>/dev/null || true

echo ""
echo "📊 Disk space AFTER cleanup:"
df -h

echo ""
echo "🎯 Docker space usage:"
sudo docker system df

# Check if we have enough space
available_space=$(df / | tail -1 | awk '{print $4}')
available_gb=$(echo "scale=2; $available_space/1024/1024" | bc 2>/dev/null || echo "N/A")

echo ""
if [ "$available_space" -lt 1048576 ]; then
    echo "⚠️  WARNING: Less than 1GB free space available!"
    echo "🔧 Consider expanding your EBS volume immediately."
    echo "💡 To expand EBS volume:"
    echo "   1. Go to AWS Console → EC2 → Volumes"
    echo "   2. Select your volume and click 'Modify Volume'"
    echo "   3. Increase size (recommend at least 20GB)"
    echo "   4. Run: sudo resize2fs /dev/xvda1"
else
    echo "✅ Sufficient disk space available: ${available_gb}GB"
    echo "🚀 You can now retry your deployment!"
fi

echo ""
echo "✅ Emergency cleanup completed!"
