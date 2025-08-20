"""
Google OAuth Setup Guide
========================

To add your new Google OAuth token, follow these steps:

STEP 1: Update credentials.json (if needed)
------------------------------------------
1. Go to: https://console.cloud.google.com/apis/credentials
2. Select your project
3. Click "Create Credentials" > "OAuth 2.0 Client IDs"
4. Application type: "Desktop application"
5. Download the JSON file
6. Replace the existing credentials.json file with your new one

STEP 2: Clear old token and re-authenticate
-------------------------------------------
1. Delete the old token.pickle file:
   rm token.pickle

2. Run authentication:
   python -c "from google_meet_api import GoogleMeetAPI; api = GoogleMeetAPI()"

3. Follow the browser OAuth flow

STEP 3: Verify setup
-------------------
Run: python verify_google_meet_setup.py

REQUIRED GOOGLE CLOUD API PERMISSIONS:
=====================================
- Google Calendar API
- Google Meet API (requires Google Workspace)

CURRENT FILES:
=============
- credentials.json: Your OAuth 2.0 client credentials
- token.pickle: Your access and refresh tokens (auto-generated)

TROUBLESHOOTING:
===============
- Error "invalid_grant": Token expired → Delete token.pickle and re-authenticate
- Error "credentials not found": Download new credentials.json
- Error "insufficient permissions": Enable Google Calendar API in Cloud Console
"""

import json
from pathlib import Path

def check_current_setup():
    """Check current Google OAuth setup."""
    print("🔍 Checking current Google OAuth setup...")
    
    # Check credentials.json
    creds_file = Path("credentials.json")
    if creds_file.exists():
        print("✅ credentials.json found")
        try:
            with open(creds_file) as f:
                creds = json.load(f)
                if 'installed' in creds:
                    project_id = creds['installed'].get('project_id', 'Unknown')
                    client_id = creds['installed'].get('client_id', 'Unknown')
                    print(f"   Project ID: {project_id}")
                    print(f"   Client ID: {client_id[:20]}...")
                else:
                    print("❌ Invalid credentials.json format")
        except Exception as e:
            print(f"❌ Error reading credentials.json: {e}")
    else:
        print("❌ credentials.json NOT found")
    
    # Check token.pickle
    token_file = Path("token.pickle")
    if token_file.exists():
        print("✅ token.pickle found (contains your OAuth tokens)")
        import os
        size = os.path.getsize(token_file)
        print(f"   Token file size: {size} bytes")
        
        # Try to check token validity
        try:
            import pickle
            with open(token_file, 'rb') as f:
                token_data = pickle.load(f)
                if hasattr(token_data, 'expired'):
                    if token_data.expired:
                        print("⚠️  Token appears to be expired")
                    else:
                        print("✅ Token appears to be valid")
                else:
                    print("ℹ️  Token status unknown")
        except Exception as e:
            print(f"⚠️  Could not validate token: {e}")
    else:
        print("❌ token.pickle NOT found")

if __name__ == "__main__":
    check_current_setup()
