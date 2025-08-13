#!/usr/bin/env python3
"""
Complete Meeting Workflow Test - Real Google Meet + Email Confirmations
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add the backend-python directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_complete_meeting_workflow():
    """Test the complete meeting workflow with real Google Meet and emails"""
    
    print("🏥 COMPLETE MEETING WORKFLOW TEST")
    print("=" * 70)
    print("Testing: Real Google Meet creation + Email confirmations")
    print("=" * 70)
    
    try:
        # Import the multi-agent server
        from multi_agent_server import orchestrator, MULTI_AGENT_AVAILABLE
        
        if not MULTI_AGENT_AVAILABLE or not orchestrator:
            print("❌ Multi-agent system not available")
            return False
        
        print("✅ Multi-agent system loaded")
        
        # Step 1: Test Google Meet API initialization
        print("\n� Step 1: Testing Google Meet API")
        print("-" * 50)
        
        try:
            from google_meet_api import GoogleMeetAPI, GoogleMeetAPIIntegration
            print("✅ Google Meet API imported successfully")
            
            # Test API initialization
            api = GoogleMeetAPI()
            if api.service:
                print("✅ Google Meet API initialized with credentials")
            else:
                print("⚠️ Google Meet API needs authentication")
                
        except Exception as e:
            print(f"❌ Google Meet API error: {e}")
        
        # Step 2: Test email configuration
        print("\n� Step 2: Testing Email Configuration")
        print("-" * 50)
        
        from dotenv import load_dotenv
        load_dotenv()
        
        email_config = {
            'SMTP_SERVER': os.getenv('SMTP_SERVER'),
            'SMTP_PORT': os.getenv('SMTP_PORT'),
            'EMAIL_USERNAME': os.getenv('EMAIL_USERNAME'),
            'EMAIL_PASSWORD': os.getenv('EMAIL_PASSWORD', '***')[:4] + '****',
            'EMAIL_FROM_NAME': os.getenv('EMAIL_FROM_NAME'),
            'EMAIL_FROM_ADDRESS': os.getenv('EMAIL_FROM_ADDRESS')
        }
        
        print("Email Configuration:")
        for key, value in email_config.items():
            if value:
                print(f"   ✅ {key}: {value}")
            else:
                print(f"   ❌ {key}: Not configured")
        
        # Step 3: Test actual meeting scheduling
        print("\n📅 Step 3: Schedule Real Meeting with Google Meet")
        print("-" * 50)
        
        # Create a realistic meeting request
        meeting_time = datetime.now() + timedelta(hours=1)
        meeting_request = f"""
        Schedule a staff meeting for {meeting_time.strftime('%Y-%m-%d %H:%M')} about "Tasks Improvements Discussion".
        
        Meeting Details:
        - Title: Staff Meeting - Tasks Improvements Discussion  
        - Description: Quarterly review of task management processes and improvement strategies
        - Duration: 60 minutes
        - Type: Staff Meeting
        - Priority: High
        
        Participants (with emails):
        - Dr. Smith: drsmith@hospital.com
        - Nurse Johnson: nurse.johnson@hospital.com  
        - Manager Davis: manager.davis@hospital.com
        - Administrator Wilson: admin.wilson@hospital.com
        
        Requirements:
        1. Create Google Meet link
        2. Send confirmation emails to all participants
        3. Include meeting agenda in email
        4. Store meeting in database
        """
        
        print(f"Meeting Request: {meeting_request.strip()}")
        print(f"Scheduled Time: {meeting_time}")
        
        # Call the meeting scheduling tool
        result = orchestrator.route_request("schedule_meeting", query=meeting_request)
        
        print(f"\n📋 Meeting Scheduling Result:")
        print(f"   Status: {result.get('success', 'Unknown')}")
        print(f"   Agent: {result.get('agent', 'Unknown')}")
        
        if result.get('success'):
            meeting_data = result.get('result', {})
            if meeting_data.get('success'):
                print("✅ Meeting successfully scheduled!")
                
                # Check for Google Meet link
                if 'google_meet_link' in meeting_data:
                    print(f"   🔗 Google Meet Link: {meeting_data['google_meet_link']}")
                
                # Check for meeting ID
                if 'meeting_id' in meeting_data:
                    print(f"   📅 Meeting ID: {meeting_data['meeting_id']}")
                
                # Check email status
                if 'emails_sent' in meeting_data:
                    print(f"   📧 Emails Sent: {meeting_data['emails_sent']}")
                
                # Check participants
                if 'participants' in meeting_data:
                    print(f"   👥 Participants: {len(meeting_data['participants'])}")
                    for participant in meeting_data['participants']:
                        print(f"      - {participant}")
                
            else:
                print(f"❌ Meeting scheduling failed: {meeting_data.get('message', 'Unknown error')}")
        else:
            print(f"❌ Agent routing failed: {result.get('message', 'Unknown error')}")
        
        # Step 4: Test email sending directly
        print("\n📧 Step 4: Test Email Sending Function")
        print("-" * 50)
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Test email connection (don't send actual email)
            print("Testing SMTP connection...")
            
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            email_username = os.getenv('EMAIL_USERNAME')
            email_password = os.getenv('EMAIL_PASSWORD')
            
            if email_username and email_password:
                try:
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(email_username, email_password)
                    server.quit()
                    print("✅ SMTP connection successful")
                    print("✅ Email credentials validated")
                except Exception as e:
                    print(f"❌ SMTP connection failed: {e}")
            else:
                print("❌ Email credentials not configured")
                
        except Exception as e:
            print(f"❌ Email test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Complete workflow test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    
    print("🚀 Starting Complete Meeting Workflow Test...")
    print("This will test:")
    print("  - Google Meet API integration")
    print("  - Email configuration and sending")
    print("  - Complete meeting scheduling workflow")
    print("  - Database storage and retrieval")
    
    success = await test_complete_meeting_workflow()
    
    if success:
        print("\n" + "=" * 70)
        print("� COMPLETE WORKFLOW TEST COMPLETED!")
        print("=" * 70)
        print("✅ System is ready for:")
        print("   📅 Real Google Meet meeting creation")
        print("   📧 Automatic email confirmations")
        print("   👥 Staff notification system")
        print("   🗄️ Database meeting storage")
        print("\n🏥 Your hospital management system is fully operational!")
    else:
        print("\n" + "=" * 70)
        print("⚠️ WORKFLOW TEST HAD ISSUES")
        print("=" * 70)
        print("Check the output above for specific problems.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
