"""
Search for AI Development Meeting
================================
"""

from meeting_management import MeetingManager, Meeting
from sqlalchemy import or_

def search_ai_meetings():
    manager = MeetingManager()
    
    # Search for meetings with AI or Development in title
    meetings = manager.session.query(Meeting).filter(
        or_(
            Meeting.title.contains('AI'),
            Meeting.title.contains('Development'),
            Meeting.title.contains('AI Development'),
            Meeting.description.contains('AI'),
            Meeting.description.contains('Development')
        )
    ).all()
    
    print(f"🔍 Found {len(meetings)} meetings with AI/Development:")
    print("=" * 60)
    
    for meeting in meetings:
        print(f"📝 Title: {meeting.title}")
        print(f"🆔 Meeting ID: {meeting.id}")
        print(f"🔗 Google Meet Link: {meeting.google_meet_link}")
        print(f"📅 Date/Time: {meeting.meeting_datetime}")
        print(f"📋 Status: {meeting.status}")
        print(f"📝 Description: {meeting.description[:100]}...")
        print("-" * 40)
    
    # Also search all meetings from today
    from datetime import date
    today = date.today()
    all_today_meetings = manager.session.query(Meeting).filter(
        Meeting.meeting_datetime >= today,
        Meeting.meeting_datetime < today.replace(day=today.day + 1)
    ).all()
    
    print(f"\n📅 All meetings for today ({today}):")
    print("=" * 60)
    
    for meeting in all_today_meetings:
        print(f"📝 Title: {meeting.title}")
        print(f"🆔 Meeting ID: {meeting.id}")
        print(f"🔗 Google Meet Link: {meeting.google_meet_link}")
        print(f"📅 Date/Time: {meeting.meeting_datetime}")
        print("-" * 40)
    
    manager.close()
    return meetings

if __name__ == "__main__":
    search_ai_meetings()
