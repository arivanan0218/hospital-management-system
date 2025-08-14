"""
GOOGLE OAUTH CONSENT SCREEN SETUP GUIDE
=======================================

The "Access blocked" error occurs because your Google Cloud project needs proper OAuth consent configuration.

STEP-BY-STEP FIX:
================

1. GO TO GOOGLE CLOUD CONSOLE
   - Visit: https://console.cloud.google.com/
   - Select your project: "hospitalagent-468118"

2. CONFIGURE OAUTH CONSENT SCREEN
   - Go to: APIs & Services > OAuth consent screen
   - Choose "External" (for testing with any Google account)
   - Fill in required fields:
     * App name: "Hospital Management System" 
     * User support email: shamilmrm2001@gmail.com
     * Developer contact information: shamilmrm2001@gmail.com

3. ADD TEST USERS
   - In OAuth consent screen, go to "Test users" section
   - Click "Add Users"
   - Add your email: shamilmrm2001@gmail.com
   - This allows your account to access the app during testing

4. ADD SCOPES
   - Go to "Scopes" section
   - Add these scopes:
     * https://www.googleapis.com/auth/calendar
     * https://www.googleapis.com/auth/calendar.events

5. VERIFY CREDENTIALS
   - Go to: APIs & Services > Credentials
   - Make sure your OAuth 2.0 Client ID exists
   - Download the JSON file again if needed

ALTERNATIVE QUICK FIX:
====================
If you want to test immediately without full verification:

1. Set OAuth consent screen to "Internal" (if you have Google Workspace)
2. OR add your email as a test user in "External" mode
3. Make sure Google Calendar API is enabled

AFTER SETUP:
===========
- Delete any existing token.pickle file
- Run the Google Meet integration again
- It should now allow authentication

Let me know once you've completed these steps!
"""

print("Google OAuth Setup Guide Created!")
print("Please follow the steps above to fix the 'Access blocked' error.")
print("\nKey steps:")
print("1. Configure OAuth consent screen in Google Cloud Console")
print("2. Add your email as a test user") 
print("3. Enable required scopes")
print("4. Try authentication again")
