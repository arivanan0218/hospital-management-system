# Microphone Deployment Guide

## Issue: Microphone Works Locally But Not in Deployed Environment

The microphone functionality works in local development but fails when deployed with the error:
```
🎤 Microphone Error: Cannot read properties of undefined (reading 'getUserMedia')
```

## Root Cause

Modern browsers require **HTTPS** for microphone access in production environments. The `navigator.mediaDevices` API is only available in secure contexts:

1. **Localhost** (always considered secure)
2. **HTTPS websites** (secure connection)
3. **File:// protocol** (local files)

## Solutions

### Option 1: Enable HTTPS on Your Deployment

#### For AWS EC2/ECS Deployment:
1. **Set up SSL Certificate**:
   ```bash
   # Install certbot for Let's Encrypt
   sudo apt-get update
   sudo apt-get install certbot python3-certbot-nginx
   
   # Generate SSL certificate
   sudo certbot --nginx -d your-domain.com
   ```

2. **Update Nginx Configuration**:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       return 301 https://$server_name$request_uri;
   }
   
   server {
       listen 443 ssl;
       server_name your-domain.com;
       
       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
       
       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Auto-renewal Setup**:
   ```bash
   sudo crontab -e
   # Add this line for auto-renewal
   0 12 * * * /usr/bin/certbot renew --quiet
   ```

#### For Docker Deployment:
1. **Update docker-compose.yml**:
   ```yaml
   version: '3.8'
   services:
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
         - /etc/letsencrypt:/etc/letsencrypt:ro
       depends_on:
         - frontend
   ```

### Option 2: Test with HTTPS in Development

1. **Generate Self-Signed Certificate**:
   ```bash
   # Create SSL directory
   mkdir ssl
   cd ssl
   
   # Generate certificate
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
   ```

2. **Update Vite Config** (frontend/vite.config.js):
   ```javascript
   import { defineConfig } from 'vite'
   import react from '@vitejs/plugin-react'
   import fs from 'fs'
   
   export default defineConfig({
     plugins: [react()],
     server: {
       https: {
         key: fs.readFileSync('./ssl/key.pem'),
         cert: fs.readFileSync('./ssl/cert.pem'),
       },
       host: true,
       port: 3000
     }
   })
   ```

### Option 3: Browser Permissions Override (Development Only)

For Chrome development:
```bash
# Start Chrome with insecure flag (NOT for production)
chrome --unsafely-treat-insecure-origin-as-secure=http://your-ip:3000 --user-data-dir=/tmp/foo
```

## Current Implementation Status

✅ **Fixed**: Added microphone availability detection in `DirectMCPChatbot.jsx`:
- Checks `navigator.mediaDevices` availability
- Validates secure context (`window.isSecureContext`)
- Shows appropriate error messages and disabled states
- Provides helpful tooltips explaining HTTPS requirement

## User Experience Improvements

The microphone button now:
1. **Shows disabled state** when microphone is unavailable
2. **Displays helpful tooltips** explaining the HTTPS requirement
3. **Uses crossed-out microphone icon** for unavailable state
4. **Provides clear error messages** about permissions and HTTPS

## Testing Steps

1. **Local Testing**: Should work on `http://localhost:3000`
2. **HTTP Deployment**: Button will be disabled with clear message
3. **HTTPS Deployment**: Button will be enabled and functional

## Browser Compatibility

- ✅ Chrome 47+
- ✅ Firefox 36+
- ✅ Safari 11+
- ✅ Edge 12+

All require HTTPS for microphone access in production.

## Troubleshooting

### Still Getting Errors After HTTPS?

1. **Check Browser Console** for specific error messages
2. **Verify SSL Certificate** is valid and trusted
3. **Test Permissions** by clicking the microphone button
4. **Check Mixed Content** warnings (all resources must be HTTPS)

### Users Need to Grant Permissions

When microphone is first accessed, browsers will prompt:
- "Allow [your-site] to use your microphone?"
- Users must click "Allow" for functionality to work

## Quick Fix Command

To quickly deploy with HTTPS on existing infrastructure:

```bash
# For immediate testing with self-signed certificate
cd frontend
npm run build
python3 -m http.server 3000 --bind 0.0.0.0

# For production deployment
sudo certbot --nginx -d your-domain.com
sudo systemctl reload nginx
```

## Summary

The microphone functionality is now properly implemented with:
- ✅ Secure context detection
- ✅ User-friendly error messages  
- ✅ Proper disabled states
- ✅ Clear deployment guidance

**Next Step**: Set up HTTPS on your deployment server to enable microphone functionality in production.
