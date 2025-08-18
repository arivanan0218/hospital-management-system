# 📧 Email Configuration Troubleshooting Guide

## Overview
This guide helps resolve email-related issues in the Hospital Management System where emails work locally but fail in deployment.

## Quick Diagnosis

### 1. Check if Email Works Locally
```bash
cd backend-python
python ../test-email-config.py
```

Expected result: ✅ Test email received in inbox

### 2. Check Docker Environment
```bash
# Start only the backend service
docker-compose up backend

# Check environment variables inside container
docker exec -it hospital_backend env | grep EMAIL
docker exec -it hospital_backend env | grep SMTP
```

Expected variables:
- `EMAIL_USERNAME=your-email@gmail.com`
- `EMAIL_PASSWORD=your-app-password`
- `SMTP_SERVER=smtp.gmail.com`
- `SMTP_PORT=587`

### 3. Test Email in Docker Container
```bash
docker exec -it hospital_backend python ../test-email-config.py
```

## Common Issues & Solutions

### Issue 1: "Email credentials not configured"
**Symptoms:**
- Local works, Docker fails
- Error: "Email credentials not configured"

**Cause:** Missing environment variables in Docker container

**Solution:**
1. Ensure `.env` file exists in root directory (not backend-python)
2. Check `docker-compose.yml` has email environment variables
3. Restart Docker containers: `docker-compose down && docker-compose up`

### Issue 2: "Authentication failed"
**Symptoms:**
- Error: "535-5.7.8 Username and Password not accepted"
- Local and Docker both fail

**Cause:** Gmail App Password not set correctly

**Solution:**
1. Enable 2-Factor Authentication on Gmail
2. Generate App Password: Google Account → Security → 2-Step Verification → App passwords
3. Use 16-character app password (not regular Gmail password)
4. Update `.env` file with correct app password

### Issue 3: "Connection timeout" or "Network unreachable"
**Symptoms:**
- Error: "Connection timeout" 
- Error: "Network is unreachable"

**Cause:** Network/firewall blocking SMTP

**Solution:**
1. Check firewall allows outbound port 587
2. For AWS EC2: Check Security Group allows outbound SMTP
3. Some networks block SMTP - try different network/VPN

### Issue 4: AWS ECS Deployment Email Fails
**Symptoms:**
- Local works, Docker works, AWS deployment fails
- Error in ECS task logs: "Email credentials not configured"

**Cause:** AWS Parameter Store not configured

**Solution:**
1. Run `./setup-email-aws-params.ps1` to set up parameters
2. Verify ECS task role has `ssm:GetParameter` permission
3. Check parameter names in `backend-task-definition.json` match Parameter Store
4. Redeploy ECS service

### Issue 5: "Less secure app access" Error
**Symptoms:**
- Error: "Please log in via your web browser"
- Authentication fails despite correct credentials

**Cause:** Google disabled "less secure apps" - must use App Password

**Solution:**
1. **Never** enable "less secure apps" (security risk)
2. Use App Password instead (see Issue 2 solution)
3. Ensure 2FA is enabled on Google account

## Configuration Files Checklist

### ✅ Root `.env` file (for Docker)
Location: `hospital-management-system/.env`
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
EMAIL_FROM_NAME=Hospital Management System
EMAIL_FROM_ADDRESS=your-email@gmail.com
```

### ✅ Docker Compose Configuration
File: `docker-compose.yml`
```yaml
backend:
  environment:
    - SMTP_SERVER=${SMTP_SERVER}
    - SMTP_PORT=${SMTP_PORT}
    - EMAIL_USERNAME=${EMAIL_USERNAME}
    - EMAIL_PASSWORD=${EMAIL_PASSWORD}
    - EMAIL_FROM_NAME=${EMAIL_FROM_NAME}
    - EMAIL_FROM_ADDRESS=${EMAIL_FROM_ADDRESS}
```

### ✅ AWS Parameter Store (for ECS)
Required parameters:
- `/hospital/email-username`
- `/hospital/email-password` 
- `/hospital/email-from-address`

### ✅ ECS Task Definition
File: `backend-task-definition.json`
```json
"secrets": [
  {
    "name": "EMAIL_USERNAME",
    "valueFrom": "arn:aws:ssm:us-east-1:ACCOUNT_ID:parameter/hospital/email-username"
  }
]
```

## Testing Commands

### Test Email Function Directly
```python
# In Python REPL or script
import os
os.environ['EMAIL_USERNAME'] = 'your-email@gmail.com'
os.environ['EMAIL_PASSWORD'] = 'your-app-password'
os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
os.environ['SMTP_PORT'] = '587'

from backend-python.multi_agent_server import send_email
result = send_email('test@example.com', 'Test', 'Test message')
print(result)
```

### Check SMTP Connection
```python
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
print("✅ SMTP connection successful!")
server.quit()
```

## Environment-Specific Fixes

### Local Development
- Use `backend-python/.env` file
- Test with `python test-email-config.py`

### Docker Compose
- Use root `.env` file 
- Environment variables passed to container
- Test with `docker exec hospital_backend python ../test-email-config.py`

### AWS ECS Production
- Use AWS Parameter Store for secrets
- Environment variables in task definition
- Check CloudWatch logs for errors

## Emergency Workaround

If email still doesn't work, temporarily disable email in code:

```python
# In multi_agent_server.py, modify send_email function:
def send_email(to_emails: str, subject: str, message: str, from_name: str = "Hospital Management System") -> Dict[str, Any]:
    # TEMPORARY: Skip email sending
    print(f"Email would be sent to: {to_emails}")
    print(f"Subject: {subject}")
    print(f"Message: {message}")
    return {"success": True, "message": "Email disabled temporarily"}
```

## Getting Help

1. Check logs: `docker logs hospital_backend`
2. Verify environment: `docker exec hospital_backend env | grep EMAIL`
3. Test SMTP manually with Python script above
4. Check Gmail security settings and app passwords
