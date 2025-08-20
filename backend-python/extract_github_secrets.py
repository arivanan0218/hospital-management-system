"""
Extract GitHub Secrets from credentials.json
===========================================

This script helps you get the exact values to add to GitHub Secrets.
"""

import json
from pathlib import Path

def extract_credentials():
    """Extract credentials for GitHub Secrets setup."""
    creds_file = Path("credentials.json")
    
    if not creds_file.exists():
        print("❌ credentials.json not found!")
        return
    
    try:
        with open(creds_file, 'r') as f:
            creds = json.load(f)
        
        if 'installed' not in creds:
            print("❌ Invalid credentials format")
            return
        
        installed = creds['installed']
        
        print("🔐 GitHub Secrets Setup")
        print("=" * 50)
        
        print("\n1. GOOGLE_OAUTH_CREDENTIALS:")
        print("   Copy the entire credentials.json content:")
        print("   " + "-" * 45)
        print(json.dumps(creds, indent=2))
        print("   " + "-" * 45)
        
        print(f"\n2. GOOGLE_PROJECT_ID:")
        print(f"   {installed.get('project_id', 'Not found')}")
        
        print(f"\n3. GOOGLE_CLIENT_ID:")
        print(f"   {installed.get('client_id', 'Not found')}")
        
        print(f"\n4. GOOGLE_CLIENT_SECRET:")
        print(f"   {installed.get('client_secret', 'Not found')}")
        
        print("\n" + "=" * 50)
        print("📋 Instructions:")
        print("1. Go to: https://github.com/arivanan0218/hospital-management-system")
        print("2. Settings > Secrets and variables > Actions")
        print("3. Click 'New repository secret'")
        print("4. Add each secret with the exact name and value shown above")
        
        print("\n✅ After adding secrets, your deployment will have:")
        print("   • Real Google Meet links in production")
        print("   • Working Google Calendar integration")
        print("   • Proper OAuth authentication")
        
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")

if __name__ == "__main__":
    extract_credentials()
