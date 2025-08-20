"""
Complete Google OAuth Setup for Real Google Meet Links
======================================================

STEP 1: Add Yourself as Test User
--------------------------------
1. Go to: https://console.cloud.google.com/apis/credentials/consent?project=meta-glazing-469613-p9
2. Scroll down to "Test users" section
3. Click "ADD USERS"
4. Enter your email address (the one you'll use for authentication)
5. Click "SAVE"

STEP 2: Complete OAuth Flow Once
-------------------------------
After adding yourself as test user, run this command to complete OAuth:

cd "E:\Rise Ai\Hospital Management System\hospital-management-system\backend-python"
python complete_oauth_setup.py

This will:
- Open your browser for Google authentication
- Save the token for future use
- Test creating a real Google Meet link

STEP 3: Verify Real Links Work
-----------------------------
After OAuth is complete, test with:
python test_real_meet_links.py

Then your frontend will create REAL Google Meet links every time!
"""

print("🔐 Google OAuth Setup Guide")
print("=" * 40)
print("1. Add yourself as test user in Google Cloud Console")
print("2. Complete OAuth flow once") 
print("3. Get real Google Meet links forever!")
print("\nNext: Go to Google Cloud Console and add your email as test user")
