"""
Personal Google OAuth Setup Script
==================================

This script helps you set up your own Google OAuth credentials
replacing your friend's credentials with your own.
"""

import json
import os
from pathlib import Path
import webbrowser

def backup_old_credentials():
    """Backup existing credentials before replacing."""
    creds_file = Path("credentials.json")
    backup_file = Path("credentials_friend_backup.json")
    
    if creds_file.exists():
        print("📁 Backing up friend's credentials...")
        # Read current credentials
        with open(creds_file, 'r') as f:
            old_creds = json.load(f)
        
        # Save as backup
        with open(backup_file, 'w') as f:
            json.dump(old_creds, f, indent=2)
        
        print(f"✅ Old credentials backed up to: {backup_file}")
        
        # Show what we're backing up
        if 'installed' in old_creds:
            project_id = old_creds['installed'].get('project_id', 'Unknown')
            print(f"   Backed up project: {project_id}")
        
        return True
    else:
        print("❌ No existing credentials.json found")
        return False

def open_google_cloud_console():
    """Open Google Cloud Console in browser."""
    print("🌐 Opening Google Cloud Console...")
    console_url = "https://console.cloud.google.com/"
    webbrowser.open(console_url)
    print(f"   Opened: {console_url}")
    
    print("\n📋 Steps to follow in the browser:")
    print("1. Create new project or select existing one")
    print("2. Go to APIs & Services > Library")
    print("3. Enable 'Google Calendar API'")
    print("4. Go to APIs & Services > Credentials")
    print("5. Create OAuth 2.0 Client ID (Desktop Application)")
    print("6. Download the JSON file")
    print("7. Replace credentials.json with your downloaded file")

def validate_new_credentials():
    """Validate that new credentials are properly formatted."""
    creds_file = Path("credentials.json")
    
    if not creds_file.exists():
        print("❌ credentials.json not found")
        return False
    
    try:
        with open(creds_file, 'r') as f:
            creds = json.load(f)
        
        if 'installed' not in creds:
            print("❌ Invalid credentials format - missing 'installed' section")
            return False
        
        required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri', 'project_id']
        missing_fields = []
        
        for field in required_fields:
            if field not in creds['installed']:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        project_id = creds['installed']['project_id']
        client_id = creds['installed']['client_id']
        
        print("✅ New credentials validated successfully!")
        print(f"   Your Project ID: {project_id}")
        print(f"   Your Client ID: {client_id[:20]}...")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON format in credentials.json")
        return False
    except Exception as e:
        print(f"❌ Error validating credentials: {e}")
        return False

def clear_old_tokens():
    """Clear old authentication tokens."""
    token_file = Path("token.pickle")
    
    if token_file.exists():
        print("🗑️ Removing old authentication tokens...")
        os.remove(token_file)
        print("✅ Old tokens cleared")
        return True
    else:
        print("ℹ️ No old tokens to clear")
        return False

def setup_oauth_instructions():
    """Provide instructions for OAuth setup."""
    print("\n🔐 OAuth Setup Instructions:")
    print("=" * 50)
    
    print("\n1. CONSENT SCREEN SETUP:")
    print("   - Go to APIs & Services > OAuth consent screen")
    print("   - Choose 'External' user type")
    print("   - Fill in:")
    print("     • App name: Hospital Management System")
    print("     • User support email: your email")
    print("     • Developer contact: your email")
    print("   - Add your email as a test user")
    
    print("\n2. CREATE CREDENTIALS:")
    print("   - Go to APIs & Services > Credentials")
    print("   - Click 'CREATE CREDENTIALS' > 'OAuth 2.0 Client IDs'")
    print("   - Application type: 'Desktop application'")
    print("   - Name: 'Hospital Management Desktop'")
    print("   - Download the JSON file")
    
    print("\n3. ENABLE APIS:")
    print("   - Go to APIs & Services > Library")
    print("   - Enable: Google Calendar API")
    print("   - Optional: Google Meet API (requires Workspace)")
    
    print("\n4. REPLACE CREDENTIALS:")
    print("   - Replace credentials.json with your downloaded file")
    print("   - Run: python setup_your_own_oauth.py")

def main():
    """Main setup function."""
    print("🚀 Setting up YOUR Google OAuth Credentials")
    print("=" * 50)
    
    # Step 1: Backup old credentials
    print("\nSTEP 1: Backing up friend's credentials...")
    backup_old_credentials()
    
    # Step 2: Open Google Cloud Console
    print("\nSTEP 2: Opening Google Cloud Console...")
    open_google_cloud_console()
    
    # Step 3: Provide instructions
    setup_oauth_instructions()
    
    # Step 4: Wait for user to complete setup
    print("\n" + "=" * 50)
    print("⏳ Complete the setup in Google Cloud Console")
    print("📁 Download credentials.json and replace the existing file")
    print("🔄 Then run this script again to validate")
    
    input("\nPress Enter after you've replaced credentials.json with your own...")
    
    # Step 5: Validate new credentials
    print("\nSTEP 3: Validating your new credentials...")
    if validate_new_credentials():
        # Step 6: Clear old tokens
        print("\nSTEP 4: Clearing old authentication tokens...")
        clear_old_tokens()
        
        print("\n✅ Setup complete!")
        print("🔄 Next: Run OAuth authentication flow")
        print("   Command: python -c \"from google_meet_api import GoogleMeetAPI; api = GoogleMeetAPI()\"")
    else:
        print("\n❌ Setup incomplete. Please check your credentials.json file.")

if __name__ == "__main__":
    main()
