#!/usr/bin/env python3
"""Test the complete meeting scheduling with real Google Meet links."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from meeting_scheduler import MeetingSchedulerAgent

def test_complete_meeting_scheduling():
    """Test complete meeting scheduling with Google Meet integration."""
    print("🧪 Testing Complete Meeting Scheduling:")
    print("=" * 60)
    
    try:
        scheduler = MeetingSchedulerAgent()
        
        # Test query that was having issues before
        test_query = "Schedule Daily Improvement Meeting with Shamil and Nazif specifically on 2025-08-13 at 10:30 PM for 20 minutes to discuss daily workflow improvements and optimization strategies"
        
        print(f"📝 Query: {test_query}")
        print("-" * 60)
        
        # Call the schedule_meeting function
        result = scheduler.schedule_meeting(test_query)
        
        print("\n📊 Result:")
        if result.get("success"):
            print("✅ Meeting scheduled successfully!")
            print(f"📋 Title: {result['data'].get('title')}")
            print(f"⏰ Time: {result['data'].get('time')}")
            print(f"⏱️  Duration: {result['data'].get('duration')}")
            print(f"👥 Participants: {result['data'].get('participants')}")
            print(f"🔗 Google Meet: {result['data'].get('google_meet_link')}")
            print(f"📧 Emails sent: {result['data'].get('emails_sent')}")
        else:
            print(f"❌ Meeting scheduling failed: {result.get('message')}")
            
    except Exception as e:
        print(f"❌ Error testing complete meeting scheduling: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_meeting_scheduling()
