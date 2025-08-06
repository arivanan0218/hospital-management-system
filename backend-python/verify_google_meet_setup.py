"""
Google Meet Integration Verification Tool
==========================================

This tool verifies if your Google Cloud setup can create REAL Google Meet links.
"""

import os
from pathlib import Path
from datetime import datetime, timedelta

def check_credentials():
    """Check if credentials.json exists and is valid."""
    creds_file = Path("credentials.json")
    
    if not creds_file.exists():
        print("❌ credentials.json NOT FOUND")
        return False
    
    try:
        import json
        with open(creds_file, 'r') as f:
            creds_data = json.load(f)
        
        # Check if it's the right format
        if 'installed' in creds_data:
            client_id = creds_data['installed'].get('client_id', '')
            project_id = creds_data['installed'].get('project_id', '')
            
            print(f"✅ credentials.json found")
            print(f"📋 Project ID: {project_id}")
            print(f"🆔 Client ID: {client_id[:20]}...")
            
            # Check if it's the old blocked project
            if project_id == "hospitalagent-468118":
                print("⚠️  WARNING: This is the old project with access restrictions!")
                print("⚠️  You should create a NEW project for full access")
                return False
            else:
                print("✅ Using different project - good!")
                return True
        else:
            print("❌ Invalid credentials.json format")
            return False
            
    except Exception as e:
        print(f"❌ Error reading credentials.json: {e}")
        return False

def test_google_meet_creation():
    """Test if Google Meet links can be created."""
    print("\n🧪 TESTING GOOGLE MEET CREATION")
    print("=" * 40)
    
    try:
        # Try to import and use the Google Meet API
        from google_meet_api import GoogleMeetAPIIntegration
        
        print("📚 Initializing Google Meet API...")
        integration = GoogleMeetAPIIntegration()
        
        if integration.service:
            print("✅ Google Calendar API connected successfully!")
            
            # Try to create a test meeting
            print("🔄 Creating test Google Meet room...")
            test_time = datetime.now() + timedelta(minutes=5)
            
            result = integration.create_meet_event(
                title="Hospital Test Meeting",
                description="Testing real Google Meet integration",
                start_time=test_time,
                duration_minutes=15,
                attendees=["shamilmrm2001@gmail.com"]
            )
            
            if 'meet_link' in result and result['meet_link']:
                meet_link = result['meet_link']
                print(f"✅ SUCCESS! Real Google Meet link created:")
                print(f"🔗 {meet_link}")
                print(f"📅 Event ID: {result.get('event_id', 'N/A')}")
                
                # Verify it's a real Google Meet link
                if "meet.google.com" in meet_link and len(meet_link.split('/')[-1]) > 10:
                    print("✅ VERIFIED: This is a REAL Google Meet link!")
                    return True
                else:
                    print("❌ This appears to be a dummy/fallback link")
                    return False
            else:
                print("❌ Failed to create Google Meet link")
                print(f"📋 Result: {result}")
                return False
        else:
            print("❌ Failed to connect to Google Calendar API")
            print("💡 This usually means OAuth consent issues")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Google Meet creation: {e}")
        return False

def verify_oauth_setup():
    """Verify OAuth consent screen setup."""
    print("\n🔐 OAUTH CONSENT SCREEN CHECKLIST")
    print("=" * 35)
    
    print("Please verify these settings in Google Cloud Console:")
    print("1. ✅ OAuth consent screen configured as 'External'")
    print("2. ✅ App status should be 'In production' (Published)")
    print("3. ✅ Scopes include 'https://www.googleapis.com/auth/calendar'")
    print("4. ✅ Your email added as test user (if still in testing)")
    print("5. ✅ Google Calendar API is enabled")
    
    response = input("\nHave you completed all the above steps? (y/n): ").lower()
    return response == 'y'

def main():
    """Main verification process."""
    print("🏥 HOSPITAL GOOGLE MEET INTEGRATION VERIFICATION")
    print("=" * 50)
    
    # Step 1: Check credentials
    print("STEP 1: Checking credentials...")
    if not check_credentials():
        print("\n❌ CREDENTIALS ISSUE DETECTED")
        print("Please create a new Google Cloud project with proper setup")
        return False
    
    # Step 2: Verify OAuth setup
    print("\nSTEP 2: OAuth consent verification...")
    if not verify_oauth_setup():
        print("\n❌ OAUTH SETUP INCOMPLETE")
        print("Please complete OAuth consent screen setup")
        return False
    
    # Step 3: Test Google Meet creation
    print("\nSTEP 3: Testing Google Meet creation...")
    if test_google_meet_creation():
        print("\n🎉 SUCCESS! Your Google Meet integration is working!")
        print("✅ You can now generate REAL Google Meet links for hospital staff")
        return True
    else:
        print("\n❌ GOOGLE MEET TEST FAILED")
        print("Please check your Google Cloud project configuration")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🚀 NEXT STEPS:")
        print("1. Your Google Meet integration is ready!")
        print("2. Test the meeting scheduler with staff")
        print("3. Send meeting invitations with real Google Meet links")
    else:
        print("\n🔧 TROUBLESHOOTING NEEDED:")
        print("1. Create new Google Cloud project")
        print("2. Follow the complete setup guide")
        print("3. Ensure OAuth consent screen is published")
        print("4. Run this verification tool again")
