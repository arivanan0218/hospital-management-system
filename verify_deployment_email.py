#!/usr/bin/env python3
"""
Deployment Email Verification Script
====================================

Run this script in your DEPLOYMENT environment to verify email configuration.
This will test the exact same code path that meeting notifications use.
"""

import os
import sys
from dotenv import load_dotenv

def verify_deployment_email_config():
    """Verify email configuration in deployment environment"""
    print("🚀 DEPLOYMENT EMAIL VERIFICATION")
    print("=" * 50)
    
    # Load environment variables (same as meeting scheduler does)
    load_dotenv()
    
    # Test 1: Check environment variables
    print("\n📋 Step 1: Environment Variables")
    print("-" * 30)
    
    required_vars = {
        'SMTP_SERVER': os.getenv('SMTP_SERVER'),
        'SMTP_PORT': os.getenv('SMTP_PORT'), 
        'EMAIL_USERNAME': os.getenv('EMAIL_USERNAME'),
        'EMAIL_PASSWORD': os.getenv('EMAIL_PASSWORD'),
        'EMAIL_FROM_NAME': os.getenv('EMAIL_FROM_NAME'),
        'EMAIL_FROM_ADDRESS': os.getenv('EMAIL_FROM_ADDRESS')
    }
    
    missing_vars = []
    for var_name, var_value in required_vars.items():
        if var_value:
            if 'PASSWORD' in var_name:
                print(f"✅ {var_name}: ***configured***")
            else:
                print(f"✅ {var_name}: {var_value}")
        else:
            print(f"❌ {var_name}: MISSING")
            missing_vars.append(var_name)
    
    if missing_vars:
        print(f"\n🚨 CRITICAL ERROR: Missing variables: {', '.join(missing_vars)}")
        print("This explains why emails fail in deployment!")
        print("\nFIX: Set these environment variables in your deployment:")
        for var in missing_vars:
            print(f"   export {var}=your_value_here")
        return False
    
    # Test 2: Test MeetingSchedulerAgent initialization
    print("\n🤖 Step 2: Meeting Scheduler Agent")
    print("-" * 30)
    
    try:
        from meeting_scheduler import MeetingSchedulerAgent
        agent = MeetingSchedulerAgent()
        
        print(f"✅ Agent initialized successfully")
        print(f"✅ Email server: {agent.email_server}")
        print(f"✅ Email port: {agent.email_port}")
        print(f"✅ Email username: {agent.email_username}")
        print(f"✅ Email configured: {'Yes' if agent.email_username and agent.email_password else 'No'}")
        
    except Exception as e:
        print(f"❌ Failed to initialize MeetingSchedulerAgent: {e}")
        return False
    
    # Test 3: Test SMTP connection
    print("\n📧 Step 3: SMTP Connection Test")
    print("-" * 30)
    
    try:
        import smtplib
        
        server = smtplib.SMTP(agent.email_server, agent.email_port)
        print("✅ SMTP connection established")
        
        server.starttls()
        print("✅ TLS encryption started")
        
        server.login(agent.email_username, agent.email_password)
        print("✅ SMTP authentication successful")
        
        server.quit()
        print("✅ Connection closed properly")
        
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        print("\nPossible causes:")
        print("  • Firewall blocking port 587")
        print("  • Invalid email credentials")
        print("  • Network restrictions in deployment")
        return False
    
    # Test 4: Test email notification function (same as meetings use)
    print("\n🧪 Step 4: Email Notification Test")
    print("-" * 30)
    
    try:
        from datetime import datetime, timedelta
        
        # Test the actual email sending function used by meetings
        test_time = datetime.now() + timedelta(hours=1)
        
        # Get a sample staff member to test with
        from database import SessionLocal, Staff, User
        session = SessionLocal()
        sample_staff = session.query(Staff).join(User).filter(User.email.isnot(None)).first()
        
        if sample_staff:
            print(f"Found test recipient: {sample_staff.user.email}")
            
            # This is the exact function meetings use for email notifications
            result = agent.send_meeting_notifications(
                staff_ids=[sample_staff.id],
                meeting_time=test_time,
                subject="Test Meeting - Email System Verification",
                location="Google Meet",
                meet_link="https://meet.google.com/test-deployment-email",
                duration_string="5 minutes",
                meeting_title="Email System Test"
            )
            
            if result.get('success'):
                print(f"✅ Test email sent successfully!")
                print(f"✅ Emails sent: {result.get('emails_sent')}")
                print(f"✅ Total recipients: {result.get('total_recipients')}")
                print(f"📧 Check inbox: {sample_staff.user.email}")
            else:
                print(f"❌ Email sending failed: {result.get('message')}")
                return False
        else:
            print("⚠️ No staff with email found - skipping actual email test")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Email notification test failed: {e}")
        return False
    
    print("\n🎉 DEPLOYMENT EMAIL VERIFICATION COMPLETE")
    print("=" * 50)
    print("✅ All tests passed!")
    print("✅ Email notifications should work for meetings")
    print("✅ Meeting scheduling with emails should work now")
    
    return True

if __name__ == "__main__":
    success = verify_deployment_email_config()
    
    if success:
        print("\n🚀 RESULT: Email system is working in deployment")
        print("Try scheduling a meeting now - emails should be sent!")
    else:
        print("\n❌ RESULT: Email system has issues in deployment")
        print("Fix the errors above, then try again.")
    
    sys.exit(0 if success else 1)
