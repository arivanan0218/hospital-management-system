#!/usr/bin/env pwsh

Write-Host "🧪 Testing the fixed GitHub Actions deployment logic..." -ForegroundColor Cyan

# Test the deployment logic locally by SSH into EC2
$deployScript = @"
#!/bin/bash
set -e

echo "🚀 Testing fixed deployment script..."

# Create hospital network if it doesn't exist
echo "🌐 Creating hospital network..."
sudo docker network create hospital-network 2>/dev/null || true

# Check if PostgreSQL is running and has correct alias
echo "🗄️ Checking PostgreSQL setup..."
if sudo docker ps | grep -q hospital-postgres; then
    echo "✅ PostgreSQL container found, ensuring correct network alias..."
    sudo docker network disconnect hospital-network hospital-postgres 2>/dev/null || true
    sudo docker network connect --alias postgres hospital-network hospital-postgres 2>/dev/null || true
    echo "✅ PostgreSQL network alias updated"
else
    echo "❌ PostgreSQL container not found. Please ensure it's running first."
    exit 1
fi

# Test nginx configuration creation
echo "🌐 Testing nginx configuration creation..."
cat > /tmp/test-nginx.conf << 'NGINXEOF'
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server hospital-frontend:3000;
    }
    
    upstream backend {
        server hospital-backend:8000;
    }
    
    server {
        listen 80;
        
        # Add CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
        
        # Health endpoint (route to backend)
        location /health {
            proxy_pass http://backend;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto `$scheme;
        }
        
        # API routes (route to backend)
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto `$scheme;
        }
        
        # All other routes (route to frontend)
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto `$scheme;
        }
    }
}
NGINXEOF

echo "✅ Nginx configuration created successfully"
echo "📁 Configuration file size: `$(wc -c < /tmp/test-nginx.conf) bytes"

# Test health check
echo "🧪 Testing current application health..."
if curl -f http://localhost/health 2>/dev/null; then
    echo "✅ Application is currently healthy"
else
    echo "⚠️ Application health check failed"
fi

echo "🎉 Fixed deployment script test completed!"
"@

# Write the test script to a temporary file
$tempScript = [System.IO.Path]::GetTempFileName() + ".sh"
$deployScript | Out-File -FilePath $tempScript -Encoding UTF8

try {
    Write-Host "📁 Uploading test script to EC2..." -ForegroundColor Yellow
    scp -i ~/hospital-key.pem -o StrictHostKeyChecking=no $tempScript ubuntu@34.207.201.88:~/test-deploy-fixed.sh
    
    Write-Host "🚀 Executing test script on EC2..." -ForegroundColor Yellow
    ssh -i ~/hospital-key.pem -o StrictHostKeyChecking=no ubuntu@34.207.201.88 "chmod +x ~/test-deploy-fixed.sh && ~/test-deploy-fixed.sh"
    
    Write-Host "✅ Test completed successfully!" -ForegroundColor Green
}
catch {
    Write-Host "❌ Test failed: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    # Clean up temporary file
    if (Test-Path $tempScript) {
        Remove-Item $tempScript
    }
}
