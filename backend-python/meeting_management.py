"""
Enhanced Meeting Management with Google Meet Integration
======================================================

Import models from database.py to avoid duplicate table definitions.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
import uuid

# Import models from database.py instead of redefining them
from database import SessionLocal, Staff, User, Department, Meeting, MeetingParticipant

class MeetingManager:
    """Enhanced Meeting Manager using models from database.py."""
    
    def __init__(self):
        self.session = SessionLocal()
    
    def create_meeting(self, 
                      title: str,
                      description: str,
                      meeting_datetime: datetime,
                      duration_minutes: int = 15,
                      location: str = "Conference Room A",
                      google_meet_link: str = None,
                      google_event_id: str = None,
                      organizer_id: str = None,
                      department_id: str = None,
                      agenda: str = None) -> Meeting:
        """Create a new meeting record."""
        try:
            meeting = Meeting(
                title=title,
                description=description,
                meeting_datetime=meeting_datetime,
                duration_minutes=duration_minutes,
                location=location,
                google_meet_link=google_meet_link,
                google_event_id=google_event_id,
                organizer_id=uuid.UUID(organizer_id) if organizer_id else None,
                department_id=uuid.UUID(department_id) if department_id else None,
                agenda=agenda,
                status="scheduled"
            )
            
            self.session.add(meeting)
            self.session.commit()
            return meeting
        except Exception as e:
            self.session.rollback()
            print(f"Error creating meeting: {e}")
            raise
    
    def add_participants(self, meeting_id: str, participant_ids: List[str]):
        """Add participants to a meeting."""
        try:
            for participant_id in participant_ids:
                participant = MeetingParticipant(
                    meeting_id=uuid.UUID(meeting_id),
                    participant_id=uuid.UUID(participant_id),
                    participant_type="staff",
                    response_status="pending"
                )
                self.session.add(participant)
            
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error adding participants: {e}")
            return False
    
    def get_meeting_by_id(self, meeting_id: str) -> Optional[Meeting]:
        """Get meeting by ID."""
        try:
            return self.session.query(Meeting).filter(
                Meeting.id == uuid.UUID(meeting_id)
            ).first()
        except Exception as e:
            print(f"Error getting meeting: {e}")
            return None
    
    def update_meeting_status(self, meeting_id: str, status: str) -> bool:
        """Update meeting status."""
        try:
            meeting = self.session.query(Meeting).filter(
                Meeting.id == uuid.UUID(meeting_id)
            ).first()
            if meeting:
                meeting.status = status
                meeting.updated_at = datetime.now()
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            print(f"Error updating meeting status: {e}")
            return False
    
    def add_meeting_notes(self, meeting_id: str, notes: str, action_items: str = None):
        """Add post-meeting notes and action items."""
        try:
            meeting = self.session.query(Meeting).filter(
                Meeting.id == uuid.UUID(meeting_id)
            ).first()
            if meeting:
                meeting.meeting_notes = notes
                if action_items:
                    meeting.action_items = action_items
                meeting.updated_at = datetime.now()
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            print(f"Error adding meeting notes: {e}")
            return False
