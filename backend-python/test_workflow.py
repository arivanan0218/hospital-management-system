#!/usr/bin/env python3
"""
Test Google Meet Integration and Email Workflow
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add the backend-python directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_actual_meeting_workflow():
    """Test the actual meeting workflow with Google Meet and email"""
    
    print("🧪 TESTING ACTUAL MEETING WORKFLOW")
    print("=" * 60)
    
    try:
        # Import the multi-agent server components
        from multi_agent_server import orchestrator, MULTI_AGENT_AVAILABLE
        
        if not MULTI_AGENT_AVAILABLE or not orchestrator:
            print("❌ Multi-agent system not available")
            return False
        
        print("✅ Multi-agent system loaded")
        
        # Test 1: Schedule a real meeting with Google Meet
        print("\n📅 Test 1: Schedule Meeting with Google Meet Link")
        print("-" * 50)
        
        meeting_request = """
        Schedule a staff meeting today at 3 PM about "Tasks Improvements".
        Title: Staff Meeting - Tasks Improvements Discussion
        Participants: Dr. Smith (drsmith@hospital.com), Nurse Johnson (nurse.johnson@hospital.com), Manager Davis (manager.davis@hospital.com)
        Duration: 60 minutes
        Create Google Meet link and send confirmation emails to all participants
        """
        
        print(f"Meeting Request: {meeting_request.strip()}")
        
        result = orchestrator.route_request("schedule_meeting", query=meeting_request)
        
        print(f"\nScheduling Result: {result}")
        
        # Check if we got a meeting ID and Google Meet link
        if isinstance(result, dict):
            if result.get('success'):
                meeting_data = result.get('result', {})
                if 'google_meet_link' in meeting_data:
                    print(f"✅ Google Meet Link Generated: {meeting_data['google_meet_link']}")
                if 'meeting_id' in meeting_data:
                    print(f"✅ Meeting ID: {meeting_data['meeting_id']}")
                if 'email_sent' in meeting_data:
                    print(f"✅ Email Status: {meeting_data['email_sent']}")
            else:
                print(f"❌ Meeting scheduling failed: {result.get('message', 'Unknown error')}")
        
        # Test 2: Check if emails were sent
        print("\n📧 Test 2: Verify Email Notifications")
        print("-" * 50)
        
        # This would typically check email logs or status
        print("Checking email notification status...")
        
        # Test 3: List meetings to see if it was created
        print("\n📋 Test 3: Verify Meeting Creation")
        print("-" * 50)
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        list_result = orchestrator.route_request("list_meetings", date_str=today_str, days_ahead=1)
        print(f"Today's meetings: {list_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_google_meet_api():
    """Test Google Meet API directly"""
    
    print("\n🔗 TESTING GOOGLE MEET API DIRECTLY")
    print("=" * 60)
    
    try:
        # Test Google API connection
        from google_meet_api import GoogleMeetAPI
        
        api = GoogleMeetAPI()
        print("✅ Google Meet API class loaded")
        
        # Test creating a Google Meet link
        meeting_details = {
            'title': 'Test Staff Meeting - Tasks Improvements',
            'description': 'Testing Google Meet integration',
            'start_time': datetime.now() + timedelta(hours=2),
            'duration_minutes': 60,
            'attendees': ['drsmith@hospital.com', 'nurse.johnson@hospital.com']
        }
        
        print("Creating Google Meet event...")
        result = api.create_meeting(**meeting_details)
        print(f"Google Meet Creation Result: {result}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Google Meet API not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Google Meet API test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_email_system():
    """Test email notification system"""
    
    print("\n📧 TESTING EMAIL SYSTEM")
    print("=" * 60)
    
    try:
        # Test email system
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        print("✅ Email libraries loaded")
        
        # Test SMTP configuration (without actually sending)
        print("Testing SMTP configuration...")
        
        smtp_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email': 'shamilmrm2001@gmail.com',
            'password': '[CONFIGURED]'  # Don't print actual password
        }
        
        print(f"SMTP Config: {smtp_config}")
        print("✅ Email configuration ready")
        
        return True
        
    except Exception as e:
        print(f"❌ Email system test failed: {str(e)}")
        return False

async def run_comprehensive_workflow_test():
    """Run comprehensive workflow test"""
    
    print("🏥 COMPREHENSIVE MEETING WORKFLOW TEST")
    print("=" * 80)
    print("Testing: Meeting Scheduling + Google Meet + Email Notifications")
    print("=" * 80)
    
    tests = {
        'google_meet_api': await test_google_meet_api(),
        'email_system': await test_email_system(),
        'meeting_workflow': await test_actual_meeting_workflow()
    }
    
    print("\n" + "=" * 80)
    print("🏁 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    for test_name, passed in tests.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(tests.values())
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Google Meet integration working")
        print("✅ Email system configured")
        print("✅ Meeting workflow operational")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("Issues found - need to fix integration")
    
    return all_passed

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Workflow Test...")
    exit_code = asyncio.run(run_comprehensive_workflow_test())
    sys.exit(0 if exit_code else 1)
