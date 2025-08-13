#!/usr/bin/env python3
"""Check meetings in database."""

from database import SessionLocal
from staff_meetings import StaffMeeting

def check_meetings():
    session = SessionLocal()
    try:
        all_meetings = session.query(StaffMeeting).all()
        print(f"📊 Total meetings in database: {len(all_meetings)}")
        
        if all_meetings:
            print("\n🕐 Recent meetings:")
            for i, meeting in enumerate(all_meetings[-5:]):  # Last 5 meetings
                print(f"{i+1}. {meeting.title}")
                print(f"   Date/Time: {meeting.meeting_time}")
                print(f"   Google Meet: {meeting.google_meet_link}")
                print(f"   Meeting ID: {meeting.id}")
                print()
        
        # Check today's and tomorrow's meetings
        from datetime import datetime, timedelta
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        today_meetings = [m for m in all_meetings if m.meeting_time.date() == today]
        tomorrow_meetings = [m for m in all_meetings if m.meeting_time.date() == tomorrow]
        
        print(f"📅 Meetings for today ({today}): {len(today_meetings)}")
        print(f"📅 Meetings for tomorrow ({tomorrow}): {len(tomorrow_meetings)}")
        
    finally:
        session.close()

if __name__ == "__main__":
    check_meetings()
