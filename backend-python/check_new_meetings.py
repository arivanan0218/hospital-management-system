#!/usr/bin/env python3
"""Check meetings in the NEW Meeting table (with Google Meet support)."""

from database import SessionLocal
from meeting_management import Meeting

def check_new_meetings():
    session = SessionLocal()
    try:
        all_meetings = session.query(Meeting).all()
        print(f"📊 Total meetings in NEW Meeting table: {len(all_meetings)}")
        
        if all_meetings:
            print("\n🕐 Recent meetings (with Google Meet):")
            for i, meeting in enumerate(all_meetings[-10:]):  # Last 10 meetings
                print(f"{i+1}. {meeting.title}")
                print(f"   Date/Time: {meeting.meeting_datetime}")
                print(f"   Google Meet: {meeting.google_meet_link}")
                print(f"   Status: {meeting.status}")
                print(f"   Meeting ID: {meeting.id}")
                print()
        else:
            print("No meetings found in the NEW Meeting table")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_new_meetings()
