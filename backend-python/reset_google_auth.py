#!/usr/bin/env python3
"""Script to regenerate Google API credentials."""

import os
import pickle
from pathlib import Path

def reset_google_credentials():
    """Reset Google credentials to force re-authentication."""
    
    print("🔧 Resetting Google API Credentials...")
    print("=" * 50)
    
    # Remove existing token file
    token_file = Path("token.pickle")
    if token_file.exists():
        try:
            os.remove(token_file)
            print("✅ Removed expired token.pickle file")
        except Exception as e:
            print(f"❌ Error removing token file: {e}")
    else:
        print("ℹ️  No token.pickle file found")
    
    # Check if credentials.json exists
    credentials_file = Path("credentials.json")
    if credentials_file.exists():
        print("✅ credentials.json file found")
        print("\n📋 Next steps:")
        print("1. Run the hospital management system again")
        print("2. When prompted, it will open a browser for Google OAuth")
        print("3. Sign in with your Google account")
        print("4. Grant calendar permissions")
        print("5. The system will create fresh tokens")
        
        # Try to initialize Google API now
        try:
            from google_meet_api import GoogleMeetAPIIntegration
            print("\n🔄 Attempting to initialize Google API...")
            google_api = GoogleMeetAPIIntegration()
            
            if google_api.service:
                print("✅ Google API credentials successfully refreshed!")
                return True
            else:
                print("⚠️  Google API initialization needs manual OAuth")
                return False
        except Exception as e:
            print(f"⚠️  Manual OAuth required: {e}")
            return False
        
    else:
        print("❌ credentials.json file not found!")
        print("\n📋 To fix this:")
        print("1. Go to: https://console.cloud.google.com/apis/credentials")
        print("2. Create OAuth 2.0 Client ID (Desktop application)")
        print("3. Download as credentials.json")
        print("4. Place credentials.json in the backend-python folder")
        return False

if __name__ == "__main__":
    reset_google_credentials()
