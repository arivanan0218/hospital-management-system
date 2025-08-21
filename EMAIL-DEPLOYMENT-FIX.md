# 📧 EMAIL DEPLOYMENT TROUBLESHOOTING GUIDE

## 🔍 **Problem Identified**
Meeting scheduling works, but **email notifications fail in deployment** while working perfectly locally.

## ✅ **Root Cause**
Environment variables for email configuration are not being properly loaded in the deployment environment.

**Local Environment:** ✅ Working (`.env` file loaded correctly)
**Deployment Environment:** ❌ Failing (environment variables not available)

## 🛠️ **DEPLOYMENT FIXES**

### **1. Docker/Container Deployment**
If using Docker, ensure environment variables are passed:

```bash
# Option A: Pass individual variables
docker run -e SMTP_SERVER=smtp.gmail.com \
           -e SMTP_PORT=587 \
           -e EMAIL_USERNAME=shamilmrm2001@gmail.com \
           -e EMAIL_PASSWORD="wqle yhlg iprs ggjg" \
           -e EMAIL_FROM_NAME="Hospital Management System" \
           -e EMAIL_FROM_ADDRESS=shamilmrm2001@gmail.com \
           your-hospital-image

# Option B: Use .env file
docker run --env-file .env your-hospital-image
```

### **2. AWS/Cloud Deployment**
Set environment variables in your cloud service:

**AWS ECS/Fargate:**
```json
{
  "environment": [
    {"name": "SMTP_SERVER", "value": "smtp.gmail.com"},
    {"name": "SMTP_PORT", "value": "587"},
    {"name": "EMAIL_USERNAME", "value": "shamilmrm2001@gmail.com"},
    {"name": "EMAIL_PASSWORD", "value": "wqle yhlg iprs ggjg"},
    {"name": "EMAIL_FROM_NAME", "value": "Hospital Management System"},
    {"name": "EMAIL_FROM_ADDRESS", "value": "shamilmrm2001@gmail.com"}
  ]
}
```

**AWS Lambda/Elastic Beanstalk:**
Set environment variables in AWS Console

### **3. Kubernetes Deployment**
Create a secret and configmap:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: email-secret
type: Opaque
stringData:
  EMAIL_PASSWORD: "wqle yhlg iprs ggjg"
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: email-config
data:
  SMTP_SERVER: "smtp.gmail.com"
  SMTP_PORT: "587"
  EMAIL_USERNAME: "shamilmrm2001@gmail.com"
  EMAIL_FROM_NAME: "Hospital Management System"
  EMAIL_FROM_ADDRESS: "shamilmrm2001@gmail.com"
```

### **4. Heroku Deployment**
Set config vars in Heroku dashboard or CLI:

```bash
heroku config:set SMTP_SERVER=smtp.gmail.com
heroku config:set SMTP_PORT=587
heroku config:set EMAIL_USERNAME=shamilmrm2001@gmail.com
heroku config:set EMAIL_PASSWORD="wqle yhlg iprs ggjg"
heroku config:set EMAIL_FROM_NAME="Hospital Management System"
heroku config:set EMAIL_FROM_ADDRESS=shamilmrm2001@gmail.com
```

### **5. Manual Server Deployment**
Ensure `.env` file exists in deployment directory:

```bash
# Copy .env file to server
scp .env user@server:/path/to/hospital-system/backend-python/

# Or set system environment variables
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export EMAIL_USERNAME=shamilmrm2001@gmail.com
export EMAIL_PASSWORD="wqle yhlg iprs ggjg"
export EMAIL_FROM_NAME="Hospital Management System"
export EMAIL_FROM_ADDRESS=shamilmrm2001@gmail.com
```

## 🧪 **Testing the Fix**

### **Option 1: Quick Test (Recommended)**
Run this command in your deployment environment:

```bash
cd /path/to/backend-python
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('EMAIL_USERNAME:', os.getenv('EMAIL_USERNAME'))
print('SMTP_SERVER:', os.getenv('SMTP_SERVER'))
"
```

**Expected Output:**
```
EMAIL_USERNAME: shamilmrm2001@gmail.com
SMTP_SERVER: smtp.gmail.com
```

### **Option 2: Full Email Test**
```bash
python -c "
from meeting_scheduler import MeetingSchedulerAgent
agent = MeetingSchedulerAgent()
print('Email configured:', agent.email_username is not None)
"
```

## 🔐 **Security Best Practices**

### **For Production Deployment:**
1. **Use App Passwords** (not regular Gmail password)
2. **Use environment variables** (never hardcode credentials)
3. **Use secrets management** (AWS Secrets Manager, Azure Key Vault)
4. **Consider dedicated email service** (AWS SES, SendGrid)

### **Alternative Email Solutions:**
If Gmail continues to cause issues in deployment:

```bash
# AWS SES Configuration
SMTP_SERVER=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
EMAIL_USERNAME=your-ses-access-key
EMAIL_PASSWORD=your-ses-secret-key
```

## 🎯 **Expected Result**
After applying the fix, you should see:
```
✅ Meeting scheduled successfully
✅ Google Meet link generated  
✅ Email notifications sent to all staff (X/X emails sent)
```

Instead of:
```
✅ Meeting scheduled successfully
✅ Google Meet link generated
❌ Issue with sending confirmation emails
```

## 📞 **Next Steps**
1. **Apply the appropriate deployment fix** from above
2. **Restart your deployment service**
3. **Test meeting scheduling again**
4. **Verify emails are received by staff members**

---
**This guide should resolve the email notification issue in deployment while maintaining local functionality.**
