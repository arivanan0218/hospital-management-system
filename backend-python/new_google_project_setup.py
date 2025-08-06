"""
COMPLETE GOOGLE CLOUD PROJECT SETUP FOR REAL GOOGLE MEET LINKS
==============================================================

CURRENT ISSUE:
- Your project "hospitalagent-468118" has OAuth consent screen restrictions
- It's in "Testing" mode which blocks external users
- You need a fresh project with proper configuration

STEP-BY-STEP NEW PROJECT SETUP:
==============================

STEP 1: CREATE NEW PROJECT
--------------------------
1. Go to: https://console.cloud.google.com/
2. Click "Select Project" dropdown at the top
3. Click "NEW PROJECT"
4. Project Name: "Hospital-Management-Prod" 
5. Click "CREATE"
6. Wait for project creation to complete

STEP 2: ENABLE GOOGLE CALENDAR API
----------------------------------
1. Make sure your new project is selected
2. Go to: APIs & Services > Library
3. Search for "Google Calendar API"
4. Click on "Google Calendar API"
5. Click "ENABLE"
6. Wait for activation

STEP 3: CONFIGURE OAUTH CONSENT SCREEN (CRITICAL!)
-------------------------------------------------
1. Go to: APIs & Services > OAuth consent screen
2. Choose "External" (this allows any Google user)
3. Fill in the form:
   - App name: "Hospital Management System"
   - User support email: shamilmrm2001@gmail.com
   - App logo: (optional, skip for now)
   - App domain: (skip for now)
   - Developer contact information: shamilmrm2001@gmail.com

4. Click "SAVE AND CONTINUE"

5. SCOPES SECTION:
   - Click "ADD OR REMOVE SCOPES"
   - Search for "calendar"
   - Select: "../auth/calendar" (View and edit events on all your calendars)
   - Select: "../auth/calendar.events" (View and edit events on all your calendars)
   - Click "UPDATE"
   - Click "SAVE AND CONTINUE"

6. TEST USERS SECTION:
   - Click "ADD USERS"
   - Add: shamilmrm2001@gmail.com
   - Click "SAVE AND CONTINUE"

7. SUMMARY:
   - Review everything
   - Click "BACK TO DASHBOARD"

STEP 4: CREATE NEW CREDENTIALS
------------------------------
1. Go to: APIs & Services > Credentials
2. Click "CREATE CREDENTIALS"
3. Select "OAuth 2.0 Client ID"
4. Application type: "Desktop Application"
5. Name: "Hospital Management Desktop"
6. Click "CREATE"
7. Download the JSON file
8. Rename it to "credentials.json"
9. Replace the old credentials.json in your project

STEP 5: PUBLISH THE APP (IMPORTANT!)
-----------------------------------
1. Go back to: APIs & Services > OAuth consent screen
2. Click "PUBLISH APP" button
3. Confirm "Make app available to all users"
4. This removes the 7-day testing limitation

ALTERNATIVE QUICK FIX FOR TESTING:
=================================
If you want to test with current project:

1. Go to OAuth consent screen
2. Add yourself as a test user: shamilmrm2001@gmail.com
3. Delete any existing token.pickle file
4. Try authentication again

WHAT THIS WILL FIX:
==================
✅ Real Google Meet links (not dummy ones)
✅ Actual Google Calendar events created
✅ Meeting links that work for all participants
✅ No more "Access blocked" errors
✅ Proper integration with hospital management system

AFTER SETUP COMPLETION:
======================
1. Replace credentials.json with new file
2. Delete token.pickle (if exists)
3. Run the Google Meet integration again
4. It will open browser for one-time authentication
5. Grant permissions to access Google Calendar
6. System will then generate REAL Google Meet links!

Let me know when you've completed the new project setup!
"""

print("📋 Google Cloud Project Setup Guide Created!")
print("\n🎯 KEY ACTIONS NEEDED:")
print("1. Create NEW Google Cloud project")
print("2. Enable Google Calendar API")
print("3. Configure OAuth consent screen as 'External'")
print("4. Add required Calendar scopes")
print("5. PUBLISH the app (removes testing restrictions)")
print("6. Create new OAuth credentials")
print("7. Download new credentials.json")
print("\n✅ This will give you REAL Google Meet links that actually work!")
print("\n📞 Current issue: OAuth app is in 'Testing' mode with restrictions")
print("📞 Solution: New project with 'Published' OAuth consent screen")
