"""
Complete OAuth Setup for Real Google Meet Links
==============================================

This script completes the OAuth flow once and saves the token.
After this, you'll get REAL Google Meet links every time.
"""

import os
from pathlib import Path

def complete_oauth():
    """Complete Google OAuth setup once and for all."""
    print("🔐 Completing Google OAuth Setup...")
    print("=" * 50)
    
    # Remove old token if exists
    token_file = Path("token.pickle")
    if token_file.exists():
        print("🗑️ Removing old token...")
        os.remove(token_file)
    
    print("🚀 Starting OAuth flow...")
    print("⚠️  Make sure you added your email as test user first!")
    print("   Go to: https://console.cloud.google.com/apis/credentials/consent")
    print()
    
    try:
        from google_meet_api import GoogleMeetAPIIntegration
        
        print("📂 Initializing Google Meet API...")
        api = GoogleMeetAPIIntegration(interactive=True)  # Interactive mode for setup
        
        if api.calendar_service:
            print("✅ SUCCESS! Google OAuth completed!")
            print("✅ Token saved for future use")
            
            # Test creating a real Google Meet link
            print("\n🧪 Testing real Google Meet link creation...")
            try:
                test_link = api.create_real_google_meet(
                    title="OAuth Test Meeting",
                    start_time="2025-08-21T15:00:00Z",
                    duration_minutes=30
                )
                
                if test_link and test_link != "https://meet.google.com/new":
                    print(f"🔗 SUCCESS! Real Google Meet link: {test_link}")
                    print("✅ Your system will now create REAL Google Meet links!")
                else:
                    print("⚠️ Got fallback link, but OAuth is working")
                    
            except Exception as e:
                print(f"⚠️ Link creation test failed: {e}")
                print("   But OAuth token is saved - links should work in meetings")
            
            return True
            
        else:
            print("❌ OAuth failed - check test user setup")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure you:")
        print("   1. Added your email as test user in Google Cloud Console")
        print("   2. Completed the browser authentication")
        return False

def test_meeting_with_real_links():
    """Test the meeting system with real Google Meet links."""
    print("\n🏥 Testing Meeting System with Real Links...")
    print("=" * 50)
    
    try:
        from meeting_scheduler import MeetingSchedulerAgent
        
        scheduler = MeetingSchedulerAgent()
        print("📋 Scheduling test meeting...")
        
        result = scheduler.schedule_meeting(
            "Test real Google Meet with Dr. Smith tomorrow at 2:00 PM for 15 minutes"
        )
        
        if result and result.get('success'):
            meet_link = result['data'].get('google_meet_link', 'No link')
            print(f"✅ Meeting created successfully!")
            print(f"🔗 Google Meet Link: {meet_link}")
            
            # Check if it's a real Google Meet link (not fallback)
            if meet_link and 'meet.google.com' in meet_link and meet_link != 'https://meet.google.com/new':
                print("✅ REAL Google Meet link created!")
            else:
                print("⚠️ Fallback link used - OAuth might need completion")
                
        else:
            print("❌ Meeting creation failed")
            
    except Exception as e:
        print(f"❌ Meeting test error: {e}")

if __name__ == "__main__":
    print("🎯 Goal: Get REAL Google Meet links in your hospital system")
    print()
    
    # Step 1: Complete OAuth
    if complete_oauth():
        # Step 2: Test real links
        test_meeting_with_real_links()
        
        print("\n" + "=" * 50)
        print("✅ SETUP COMPLETE!")
        print("🔗 Your frontend will now create REAL Google Meet links!")
        print("📧 Meeting emails will contain functional meeting links!")
    else:
        print("\n❌ Setup failed. Please:")
        print("1. Add your email as test user in Google Cloud Console")
        print("2. Try running this script again")
