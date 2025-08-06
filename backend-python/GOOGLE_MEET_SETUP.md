# Google Meet Integration Setup Instructions

## Step 1: Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable Google Calendar API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

## Step 2: Create Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Configure OAuth consent screen if prompted
4. Choose Application type: "Desktop application"
5. Name it: "Hospital Management Meeting Scheduler"
6. Click "Create"
7. Download the JSON file and save it as `credentials.json` in the backend-python folder

## Step 3: Test the Integration

Run this command to test the Google Meet integration:

```bash
python test_google_meet.py
```

## Step 4: Authentication Flow

The first time you run the meeting scheduler:
1. A browser window will open
2. Sign in to your Google account
3. Grant permissions to the Hospital Management System
4. The system will save authentication tokens for future use

## Features

✅ **Automatic Google Meet Links**: Every meeting gets a unique Google Meet link
✅ **Calendar Integration**: Meetings are added to Google Calendar
✅ **Email Notifications**: Staff receive emails with Meet links
✅ **Attendee Management**: All staff are automatically added as attendees
✅ **Reminders**: Automatic email and popup reminders

## Fallback System

If Google API is unavailable, the system will:
- Generate a simple Meet link based on meeting ID
- Still send confirmation emails
- Continue working without Calendar integration
