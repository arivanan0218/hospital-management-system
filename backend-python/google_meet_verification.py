"""
Google Meet Integration Verification Tool
=========================================

Run this after setting up the new Google Cloud project to verify everything works.
"""

import os
from pathlib import Path
from datetime import datetime, timedelta

def verify_files():
    """Verify required files exist."""
    print("🔍 Checking required files...")
    
    required_files = [
        "credentials.json",
        ".env",
        "google_meet_api.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"✅ {file} found")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    return True

def verify_credentials():
    """Verify credentials.json has new project info."""
    print("\n🔍 Checking credentials.json...")
    
    try:
        import json
        with open("credentials.json", "r") as f:
            creds = json.load(f)
        
        project_id = creds.get("installed", {}).get("project_id", "")
        client_id = creds.get("installed", {}).get("client_id", "")
        
        print(f"✅ Project ID: {project_id}")
        print(f"✅ Client ID: {client_id[:50]}...")
        
        if project_id == "hospitalagent-468118":
            print("⚠️  WARNING: Still using old project ID")
            print("   Please create a new Google Cloud project")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")
        return False

def test_google_meet_api():
    """Test Google Meet API integration."""
    print("\n🧪 Testing Google Meet API...")
    
    try:
        from google_meet_api import GoogleMeetAPIIntegration
        
        # Initialize the API
        print("Initializing Google Meet API...")
        api = GoogleMeetAPIIntegration()
        
        if not api.service:
            print("❌ Google Calendar API not initialized")
            print("   This will trigger OAuth flow when you run it")
            return False
        
        # Try to create a test meeting
        print("Creating test meeting...")
        test_time = datetime.now() + timedelta(minutes=5)
        
        result = api.create_meet_event(
            title="TEST - Hospital System Verification",
            description="Testing Google Meet integration",
            start_time=test_time,
            duration_minutes=15,
            attendees=["test@example.com"]
        )
        
        if 'meet_link' in result and result['meet_link']:
            print(f"✅ SUCCESS! Real Google Meet link created:")
            print(f"   {result['meet_link']}")
            print(f"   Event ID: {result.get('event_id', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to create Google Meet link")
            print(f"   Result: {result}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Install: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_meeting_scheduler():
    """Test the complete meeting scheduler."""
    print("\n🧪 Testing Meeting Scheduler...")
    
    try:
        from meeting_scheduler import MeetingSchedulerAgent
        
        agent = MeetingSchedulerAgent()
        
        result = agent.schedule_meeting(
            "Test Google Meet integration tomorrow at 2pm for all doctors"
        )
        
        if result.get('success'):
            meet_link = result.get('data', {}).get('google_meet_link', '')
            if 'meet.google.com' in meet_link and meet_link != 'https://meet.google.com/new':
                print(f"✅ SUCCESS! Meeting scheduled with real Google Meet:")
                print(f"   Link: {meet_link}")
                print(f"   Meeting ID: {result.get('data', {}).get('meeting_id', 'N/A')}")
                return True
            else:
                print(f"❌ Meeting scheduled but with fallback link: {meet_link}")
                return False
        else:
            print(f"❌ Failed to schedule meeting: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing scheduler: {e}")
        return False

def run_verification():
    """Run complete verification."""
    print("🏥 HOSPITAL MANAGEMENT - GOOGLE MEET VERIFICATION")
    print("=" * 60)
    
    # Check files
    if not verify_files():
        print("\n❌ VERIFICATION FAILED: Missing required files")
        return False
    
    # Check credentials
    if not verify_credentials():
        print("\n❌ VERIFICATION FAILED: Invalid credentials")
        return False
    
    # Clean up old tokens
    token_file = Path("token.pickle")
    if token_file.exists():
        print(f"\n🧹 Removing old token.pickle...")
        token_file.unlink()
        print("   This will force re-authentication with new project")
    
    print("\n" + "=" * 60)
    print("✅ BASIC VERIFICATION PASSED")
    print("=" * 60)
    
    print("\n📋 NEXT STEPS:")
    print("1. Run this verification again to test API")
    print("2. The first run will open a browser for OAuth")
    print("3. Sign in with: shamilmrm2001@gmail.com")
    print("4. Grant calendar permissions")
    print("5. Check if real Google Meet links are created")
    
    print("\n🚀 TO TEST API NOW:")
    print("python google_meet_verification.py --test-api")

def main():
    import sys
    
    if "--test-api" in sys.argv:
        print("🧪 TESTING GOOGLE MEET API...")
        print("=" * 60)
        
        if test_google_meet_api():
            print("\n🎉 API TEST PASSED!")
            
            if test_meeting_scheduler():
                print("\n🎉 MEETING SCHEDULER TEST PASSED!")
                print("\n✅ FULL VERIFICATION SUCCESSFUL!")
                print("Your Google Meet integration is working correctly!")
            else:
                print("\n❌ Meeting scheduler test failed")
        else:
            print("\n❌ API test failed")
            print("\nTROUBLESHOOTING:")
            print("1. Make sure you created a NEW Google Cloud project")
            print("2. Enable Google Calendar API")
            print("3. Configure OAuth consent screen as 'External'")
            print("4. Add your email as test user")
            print("5. Download NEW credentials.json")
    else:
        run_verification()

if __name__ == "__main__":
    main()
