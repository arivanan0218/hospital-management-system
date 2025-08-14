#!/usr/bin/env python3
"""Test script for participant extraction and meeting title improvements."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from meeting_scheduler import MeetingSchedulerAgent

def test_participant_extraction():
    """Test participant extraction functionality."""
    scheduler = MeetingSchedulerAgent()
    
    test_queries = [
        "schedule meeting about daily improvement between shamil and nazif tomorrow at 2pm for 15min",
        "meeting about quarterly review with shamil and nazif at 3pm",
        "schedule budget planning meeting between shamil and nazif tomorrow at 10am for 30 minutes"
    ]
    
    print("🧪 Testing Participant Extraction:")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        
        # Test participant extraction
        participants = scheduler.extract_participants_from_query(query)
        print(f"👥 Participants: {participants}")
        
        # Test meeting title extraction
        title = scheduler.extract_meeting_title(query)
        print(f"📋 Meeting Title: {title}")
        
        # Test duration extraction
        duration_min, duration_str = scheduler.parse_duration(query)
        print(f"⏰ Duration: {duration_min} minutes -> '{duration_str}'")
        
        print("-" * 30)

if __name__ == "__main__":
    try:
        test_participant_extraction()
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
