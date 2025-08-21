#!/usr/bin/env python3
"""
Test Email After Deployment Fix
===============================

Run this to verify email functionality is working after the fix
"""

import requests
import json
import time

def test_deployed_email():
    """Test email functionality on deployed system"""
    
    print("🧪 TESTING DEPLOYED EMAIL FUNCTIONALITY")
    print("======================================")
    
    # Your EC2 endpoint
    base_url = "http://54.85.118.65"
    
    print(f"🎯 Testing deployment at: {base_url}")
    
    # Test 1: Health check
    print("\n📡 Step 1: Health Check")
    print("-" * 25)
    
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Server is accessible and healthy")
        else:
            print(f"⚠️ Server returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Test 2: Email functionality
    print("\n📧 Step 2: Email Test")
    print("-" * 20)
    
    email_payload = {
        "params": {
            "name": "send_email",
            "arguments": {
                "to_emails": "shamilmrm2001@gmail.com",
                "subject": "🏥 Hospital Management - Email Test After Fix",
                "message": f"""
Email functionality test successful!

✅ Deployment Status: Working
✅ Email System: Operational
✅ Meeting Notifications: Ready

This confirms that:
- Email configuration is properly loaded
- SMTP connection is working
- Meeting confirmations will be sent

Test completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}
Environment: Production (EC2)
"""
            }
        }
    }
    
    try:
        print("🚀 Sending test email...")
        response = requests.post(
            f"{base_url}/tools/call",
            json=email_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"📨 API Response: {result}")
            
            if result.get('success', False):
                print("✅ EMAIL TEST SUCCESSFUL!")
                print("📧 Check your inbox: shamilmrm2001@gmail.com")
                print("\n🎉 RESULT: Email system is now working!")
                print("✨ Meeting confirmations will be sent for new meetings")
                return True
            else:
                print(f"❌ Email sending failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Email test error: {e}")
        return False

def test_meeting_notification():
    """Test meeting notification workflow"""
    
    print("\n🏥 Step 3: Meeting Notification Test")
    print("-" * 35)
    
    # This would test the actual meeting scheduling with email
    # For now, we'll just show how to test it
    print("To test meeting notifications:")
    print("1. Go to http://54.85.118.65")
    print("2. Click 'Schedule Meeting'")
    print("3. Fill in meeting details")
    print("4. Check if confirmation emails are sent")
    
    return True

if __name__ == "__main__":
    print("Starting email deployment verification...")
    
    email_ok = test_deployed_email()
    test_meeting_notification()
    
    if email_ok:
        print(f"\n🚀 SUCCESS: Email system operational!")
        print(f"🌐 Your system: http://54.85.118.65")
        print(f"📧 Test meetings and check for email confirmations")
    else:
        print(f"\n❌ Email system needs attention")
        print(f"Run the quick-email-fix-ec2.sh script on your EC2 instance")
