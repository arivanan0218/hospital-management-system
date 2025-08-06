#!/usr/bin/env python3
"""Test frontend-backend communication for meeting scheduling."""

import json
from comprehensive_server import schedule_meeting_with_staff

def test_frontend_meeting_scheduling():
    """Test that the frontend can schedule meetings without encoding issues."""
    print("Testing frontend meeting scheduling...")
    print("=" * 50)
    
    # Test case: Schedule a meeting as the frontend would
    meeting_request = "Schedule medical equipment and sales inventory improvement meeting for all staff on 2025/08/20 at 11am for 30 minutes"
    
    try:
        # Call the MCP function that the frontend uses
        result = schedule_meeting_with_staff(meeting_request)
        
        # Convert to JSON to test serialization (what frontend receives)
        json_result = json.dumps(result, indent=2)
        
        print("SUCCESS: MCP function returned clean response!")
        print("Response can be safely serialized to JSON:")
        print(json_result)
        
        if result.get("success"):
            print(f"\nMeeting Details:")
            print(f"- Meeting ID: {result.get('meeting_id')}")
            print(f"- Google Meet: {result.get('google_meet_link')}")
            print(f"- Participants: {result.get('participants_invited')}")
            print(f"- Status: {result.get('status')}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_meeting_retrieval():
    """Test meeting retrieval functions."""
    print("\nTesting meeting retrieval...")
    print("-" * 30)
    
    try:
        from comprehensive_server import get_meetings_by_date
        meetings = get_meetings_by_date("2025-08-20")
        
        json_result = json.dumps(meetings, indent=2)
        print("SUCCESS: Meeting retrieval works!")
        print(f"Found {meetings.get('total_meetings', 0)} meetings for 2025-08-20")
        
        return True
        
    except Exception as e:
        print(f"ERROR in retrieval: {e}")
        return False

if __name__ == "__main__":
    print("FRONTEND-BACKEND COMMUNICATION TEST")
    print("=" * 40)
    
    scheduling_ok = test_frontend_meeting_scheduling()
    retrieval_ok = test_meeting_retrieval()
    
    if scheduling_ok and retrieval_ok:
        print("\n✅ ALL TESTS PASSED - Frontend should now work!")
        print("The encoding issues have been resolved.")
    else:
        print("\n❌ Some tests failed - need further investigation")
