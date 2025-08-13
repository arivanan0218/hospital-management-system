#!/usr/bin/env python3
"""Script to refresh Google API credentials for Google Meet integration."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google_meet_api import GoogleMeetAPIIntegration
from datetime import datetime, timedelta

def test_google_meet_api():
    """Test and refresh Google Meet API credentials."""
    print("🔧 Testing Google Meet API Integration...")
    print("=" * 50)
    
    try:
        # Initialize the Google Meet API
        google_api = GoogleMeetAPIIntegration()
        
        if google_api.service:
            print("✅ Google Calendar API initialized successfully!")
            
            # Test creating a meeting
            test_time = datetime.now() + timedelta(minutes=10)
            print(f"\n🧪 Testing meeting creation for: {test_time}")
            
            result = google_api.create_meet_event(
                title="Test Meeting - API Check",
                description="Testing Google Meet API integration",
                start_time=test_time,
                duration_minutes=15,
                attendees=["test@example.com"]
            )
            
            if 'meet_link' in result:
                print(f"✅ Google Meet link created successfully!")
                print(f"🔗 Meet Link: {result['meet_link']}")
                print(f"📅 Event ID: {result.get('event_id', 'N/A')}")
            else:
                print(f"❌ Failed to create Google Meet link")
                print(f"Result: {result}")
                
        else:
            print("❌ Google Calendar API initialization failed")
            
    except Exception as e:
        print(f"❌ Error testing Google Meet API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_google_meet_api()
