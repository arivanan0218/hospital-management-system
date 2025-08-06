#!/usr/bin/env python3
"""Test meeting retrieval functionality."""

from comprehensive_server import get_meetings_by_time_range, get_meetings_by_date
import datetime

def test_meeting_functions():
    """Test all meeting retrieval functions."""
    print("🧪 Testing Meeting Retrieval Functions")
    print("=" * 50)
    
    # Test 1: Get meetings by date
    print("\n📅 TEST 1: Get meetings by date (today)")
    today = datetime.date.today().strftime('%Y-%m-%d')
    meetings_today = get_meetings_by_date(today)
    print(f"Date: {today}")
    print(f"Total meetings found: {len(meetings_today.get('meetings', []))}")
    for i, meeting in enumerate(meetings_today.get('meetings', [])[:3]):
        print(f"  {i+1}. {meeting['title']}")
        print(f"     Time: {meeting['meeting_datetime']}")
        print(f"     Google Meet: {meeting['google_meet_link']}")
        print()
    
    # Test 2: Get meetings by time range
    print("\n⏰ TEST 2: Get meetings by time range (9 PM - 11 PM)")
    meetings_evening = get_meetings_by_time_range('2025-08-06 21:00', '2025-08-06 23:00')
    print(f"Time range: 9:00 PM - 11:00 PM")
    print(f"Total meetings found: {len(meetings_evening.get('meetings', []))}")
    for i, meeting in enumerate(meetings_evening.get('meetings', [])):
        print(f"  {i+1}. {meeting['title']}")
        print(f"     Time: {meeting['meeting_datetime']}")
        print(f"     Google Meet: {meeting['google_meet_link']}")
        print()
    
    # Test 3: Get tomorrow's meetings
    print("\n📅 TEST 3: Get tomorrow's meetings")
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    meetings_tomorrow = get_meetings_by_date(tomorrow)
    print(f"Date: {tomorrow}")
    print(f"Total meetings found: {len(meetings_tomorrow.get('meetings', []))}")
    for i, meeting in enumerate(meetings_tomorrow.get('meetings', [])[:3]):
        print(f"  {i+1}. {meeting['title']}")
        print(f"     Time: {meeting['meeting_datetime']}")
        print(f"     Google Meet: {meeting['google_meet_link']}")
        print()
    
    print("\n✅ Meeting retrieval functionality test completed!")

if __name__ == "__main__":
    test_meeting_functions()
