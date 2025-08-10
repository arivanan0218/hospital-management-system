#!/bin/bash

echo "🔧 Quick fix for nginx configuration..."

# Update nginx configuration directly on the container
sudo docker exec nginx-proxy sh -c 'cat > /etc/nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server hospital-backend:8000;
    }
    
    upstream frontend {
        server hospital-frontend:3000;
    }

    server {
        listen 80;
        
        # Backend API routes
        location /health {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            add_header Access-Control-Allow-Origin *;
        }
        
        location /docs {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            add_header Access-Control-Allow-Origin *;
        }
        
        location /tools/ {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            add_header Access-Control-Allow-Origin *;
        }
        
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            add_header Access-Control-Allow-Origin *;
        }
        
        # Frontend routes (catch-all)
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
        }
    }
}
EOF'

# Reload nginx
sudo docker exec nginx-proxy nginx -s reload

echo "✅ Nginx configuration updated!"
echo "🧪 Testing health endpoint..."
curl -s http://localhost/health
echo ""
echo "✅ Quick fix complete!"
