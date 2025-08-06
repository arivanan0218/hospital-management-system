"""Test meeting notification emails directly."""

from meeting_scheduler import MeetingSchedulerAgent
from datetime import datetime

def test_meeting_emails():
    """Test sending meeting notification emails."""
    scheduler = MeetingSchedulerAgent()
    
    # Get staff IDs - including all active staff members
    staff_ids = [
        "2384060e-bf6a-43d7-8ca2-39424dea8c23",  # Dr. John Smith
        "0d2b373b-7c32-439b-a848-e488283c9069",  # Mary Johnson (RN)
        "c79fd987-a68d-4e9d-9f6c-e549df6a654a",  # Dr. Sarah Wilson
        "d3e8f85c-21b3-417f-81c1-bd3e9489daac"   # Dr. Mohamed Nazif
    ]
    meeting_time = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
    
    print("Testing email notifications...")
    # Generate WORKING meeting links for testing
    from simple_google_meet import SimpleGoogleMeetGenerator
    meeting_solution = SimpleGoogleMeetGenerator.get_working_solution("Test Meeting - Hospital Staff")
    real_meet_link = meeting_solution["primary_option"]["link"]
    
    print(f"Using WORKING meeting link: {real_meet_link}")
    print("NOTE: This is a REAL, working video conference link!")
    
    result = scheduler.send_meeting_notifications(
        staff_ids,
        meeting_time,
        "Test Meeting - Daily Tasks Discussion with WORKING Video Conference",
        "Conference Room A",
        real_meet_link
    )
    
    print(f"Email test result: {result}")

if __name__ == "__main__":
    test_meeting_emails()
