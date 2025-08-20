"""
Google App Verification Guide
=============================

Your app needs Google verification because it requests Calendar API access.

OPTION 1: Use Unverified App (Quick)
===================================
1. When you see "Google hasn't verified this app"
2. Click "Advanced" at bottom
3. Click "Go to hospital-management-system (unsafe)"
4. Complete authentication

OPTION 2: Submit for Verification (Recommended)
==============================================
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Click "SUBMIT FOR VERIFICATION"
3. Fill out the verification form:

   Required Information:
   - App Name: Hospital Management System
   - App Description: Hospital management system with meeting scheduling and Google Meet integration
   - Why you need access: To create calendar events and Google Meet links for hospital staff meetings
   - Privacy Policy: Required for verification
   - Terms of Service: Required for verification

4. Upload screenshots of your app
5. Wait 1-7 days for Google review

OPTION 3: Keep in Testing Mode (Alternative)
==========================================
If you prefer, you can:
1. Go back to OAuth consent screen
2. Set status back to "Testing"
3. Add your email as test user
4. Use without verification warnings

For Hospital Management System, I recommend Option 1 (use unverified) 
for now to get real Google Meet links working immediately.
"""

def show_verification_options():
    print("🔐 Google App Verification Options")
    print("=" * 40)
    print("1. ⚡ Quick: Use unverified app (click Advanced)")
    print("2. 🏆 Best: Submit for Google verification") 
    print("3. 🧪 Alternative: Switch back to testing mode")
    print()
    print("For immediate real Google Meet links: Choose Option 1")

if __name__ == "__main__":
    show_verification_options()
