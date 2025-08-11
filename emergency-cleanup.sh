#!/bin/bash

echo "🚨 EMERGENCY DISK CLEANUP SCRIPT 🚨"
echo "=================================="

echo "📊 Disk space BEFORE cleanup:"
df -h

echo ""
echo "🧹 Step 1: Cleaning Docker images and containers..."
sudo docker system prune -af --volumes
sudo docker image prune -af

echo ""
echo "🧹 Step 2: Cleaning package cache..."
sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/*

echo ""
echo "🧹 Step 3: Cleaning temporary files..."
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*

echo ""
echo "🧹 Step 4: Cleaning journal logs..."
sudo journalctl --vacuum-size=50M

echo ""
echo "🧹 Step 5: Cleaning old kernels..."
sudo apt-get autoremove --purge -y

echo ""
echo "📊 Disk space AFTER cleanup:"
df -h

echo ""
echo "🎯 Docker space usage:"
sudo docker system df

echo ""
echo "✅ Emergency cleanup completed!"
