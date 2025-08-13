"""
COMPLETE GUIDE: Create New Google Cloud Project for Google Meet Integration
=========================================================================

STEP 1: CREATE NEW GOOGLE CLOUD PROJECT
=======================================

1. Go to Google Cloud Console: https://console.cloud.google.com/

2. Click "Select a project" dropdown at the top
   - Click "NEW PROJECT"
   - Project name: "Hospital-Meet-System" (or your choice)
   - Organization: Leave default or select if you have one
   - Location: Leave default
   - Click "CREATE"

3. Wait for project creation (takes ~1 minute)
   - Make sure the new project is selected in the dropdown

STEP 2: ENABLE GOOGLE CALENDAR API
==================================

1. In your new project, go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click on it and click "ENABLE"
   - Wait for it to be enabled

2. Also enable "Google Meet API" (if available):
   - Search for "Google Meet API" 
   - Click "ENABLE" if found

STEP 3: CONFIGURE OAUTH CONSENT SCREEN (CRITICAL!)
==================================================

1. Go to "APIs & Services" > "OAuth consent screen"

2. Choose User Type:
   - Select "External" (allows any Google account)
   - Click "CREATE"

3. OAuth consent screen setup:
   - App name: "Hospital Management System"
   - User support email: shamilmrm2001@gmail.com
   - App logo: Skip for now
   - App domain: Leave empty for now
   - Authorized domains: Leave empty for now
   - Developer contact information: shamilmrm2001@gmail.com
   - Click "SAVE AND CONTINUE"

4. Scopes page:
   - Click "ADD OR REMOVE SCOPES"
   - Search for "calendar" 
   - Select these scopes:
     * ../auth/calendar (See, edit, share, and permanently delete all the calendars you can access using Google Calendar)
     * ../auth/calendar.events (View and edit events on all your calendars)
   - Click "UPDATE"
   - Click "SAVE AND CONTINUE"

5. Test users page:
   - Click "ADD USERS"
   - Add your email: shamilmrm2001@gmail.com
   - Click "ADD"
   - Click "SAVE AND CONTINUE"

6. Summary page:
   - Review everything
   - Click "BACK TO DASHBOARD"

STEP 4: CREATE OAUTH 2.0 CREDENTIALS
====================================

1. Go to "APIs & Services" > "Credentials"

2. Click "CREATE CREDENTIALS" > "OAuth 2.0 Client ID"

3. Configure OAuth client:
   - Application type: "Desktop application"
   - Name: "Hospital Management Desktop App"
   - Click "CREATE"

4. Download credentials:
   - A popup will show your credentials
   - Click "DOWNLOAD JSON"
   - Save the file as "credentials.json"
   - IMPORTANT: Replace the old credentials.json file in your backend-python folder

STEP 5: UPDATE YOUR PROJECT
===========================

1. Copy the new credentials.json to your project:
   - Replace the file at: backend-python/credentials.json

2. Delete old authentication tokens:
   - Delete "token.pickle" if it exists in backend-python folder
   - This forces re-authentication with new project

3. Update your .env file with new project info:
   - Add: GOOGLE_PROJECT_ID=your-new-project-id
   - Add: GOOGLE_APPLICATION_NAME=Hospital Management System

STEP 6: TEST THE INTEGRATION
============================

1. Run the test command:
   python google_meet_verification.py

2. It should:
   - Open a browser for Google OAuth
   - Ask you to sign in with shamilmrm2001@gmail.com
   - Request permission to access Google Calendar
   - Create a real Google Meet link
   - Save authentication tokens for future use

STEP 7: VERIFY EMAIL INTEGRATION
================================

1. Test the complete flow:
   python -c "
   from meeting_scheduler import MeetingSchedulerAgent
   agent = MeetingSchedulerAgent()
   result = agent.schedule_meeting('Test meeting tomorrow at 3pm for all doctors')
   print('Result:', result)
   "

TROUBLESHOOTING
===============

If you still get "Access blocked":
1. Make sure OAuth consent screen is configured as "External"
2. Make sure your email is added as a test user
3. Make sure Google Calendar API is enabled
4. Try using an incognito browser window for OAuth

If OAuth flow doesn't work:
1. Check that redirect URI includes "http://localhost"
2. Make sure you're using the correct credentials.json
3. Delete token.pickle and try again

IMPORTANT NOTES
===============

1. The new project will have a different project ID
2. You'll need to re-authenticate (browser will open)
3. This should create REAL Google Meet links that work
4. The OAuth consent screen setup is crucial for avoiding "Access blocked"

Let me know once you've completed these steps and I'll help test it!
"""

print("Complete Google Cloud setup guide created!")
print("Follow the steps above to create a new project with proper Google Meet access.")
print("\nKey points:")
print("1. Create NEW project")
print("2. Enable Google Calendar API") 
print("3. Configure OAuth consent screen as 'External'")
print("4. Add your email as test user")
print("5. Download NEW credentials.json")
print("6. Delete old token.pickle file")
print("7. Test the integration")
