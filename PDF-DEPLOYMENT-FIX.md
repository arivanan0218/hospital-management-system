# 🏥 PDF Deployment Fix Guide

## Problem Summary
✅ **Local PDF generation works perfectly** (verified with comprehensive testing)  
❌ **Deployment PDF fails** with "Failed to load PDF document"

## Root Cause
Your Docker image in deployment doesn't have `reportlab` and `markdown2` dependencies, even though they're listed in `pyproject.toml`.

## 🔧 Solution Steps

### Step 1: Install Docker Desktop (if not already installed)
1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Install and start Docker Desktop
3. Verify installation: `docker --version`

### Step 2: Rebuild Backend Docker Image
```bash
# Navigate to backend directory
cd "backend-python"

# Rebuild with fresh dependencies (no cache)
docker build --no-cache -t hospital-backend:latest .

# Test the image locally
docker run -d --name test-pdf -p 8001:8000 hospital-backend:latest

# Wait 10 seconds, then test PDF dependencies
docker exec test-pdf python -c "
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate
    import markdown2
    print('✅ PDF dependencies available!')
except ImportError as e:
    print('❌ Missing:', e)
"

# Cleanup test container
docker stop test-pdf
docker rm test-pdf
```

### Step 3: Tag for ECR
```bash
# Tag for your ECR repository
docker tag hospital-backend:latest 135878023409.dkr.ecr.us-east-1.amazonaws.com/hospital-backend:latest
```

### Step 4: Push to ECR
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 135878023409.dkr.ecr.us-east-1.amazonaws.com

# Push the new image
docker push 135878023409.dkr.ecr.us-east-1.amazonaws.com/hospital-backend:latest
```

### Step 5: Update Deployment
SSH to your EC2 instance and run:
```bash
# Stop current backend
docker stop hospital-backend

# Pull the new image
docker pull 135878023409.dkr.ecr.us-east-1.amazonaws.com/hospital-backend:latest

# Restart with docker-compose
docker-compose up -d

# Or manually restart the backend container
docker run -d \
  --name hospital-backend \
  --network hospital-network \
  --restart unless-stopped \
  -e DATABASE_URL="postgresql://postgres:postgres@postgres:5432/hospital_db" \
  135878023409.dkr.ecr.us-east-1.amazonaws.com/hospital-backend:latest
```

### Step 6: Verify Fix
1. Wait 2-3 minutes for containers to fully start
2. Test PDF download in your web interface
3. Check backend logs: `docker logs hospital-backend`

## 🧪 Quick Deployment Test
Once deployed, SSH to EC2 and run this test:
```bash
# Test PDF generation on EC2
docker exec hospital-backend python -c "
import os
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    import markdown2
    
    # Create test PDF
    doc = SimpleDocTemplate('/tmp/test.pdf', pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph('Deployment Test Success!', styles['Title'])]
    doc.build(story)
    
    size = os.path.getsize('/tmp/test.pdf')
    print(f'✅ PDF created successfully ({size} bytes)')
    os.remove('/tmp/test.pdf')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

## 📋 Alternative: Direct EC2 Fix
If rebuilding Docker is complex, you can install dependencies directly:
```bash
# SSH to EC2 and run in backend container
docker exec -it hospital-backend pip install reportlab>=4.0.0 markdown2>=2.4.0

# Restart container to apply changes
docker restart hospital-backend
```

## 🎯 Expected Results
After this fix:
- ✅ PDF generation works in deployment
- ✅ Discharge reports download successfully
- ✅ No more "Failed to load PDF document" errors
- ✅ File sizes will be similar to local (1,676+ bytes for simple PDFs, 50,000+ bytes for full reports)

## 🚨 If Still Failing
Check these additional issues:
1. **Nginx Configuration**: Ensure PDF files are served with correct MIME type
2. **File Permissions**: Backend can write to upload directories  
3. **Network Issues**: Files transfer correctly from backend to frontend
4. **Browser Issues**: PDF viewer can handle the generated files

The diagnostic script confirmed local generation works perfectly, so this Docker image rebuild should resolve the deployment issue.
