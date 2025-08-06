"""
Enhanced Meeting Management with Google Meet Integration
======================================================

This module provides comprehensive meeting storage and retrieval functionality.
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
import uuid

from database import Base, SessionLocal, Staff, User, Department

class Meeting(Base):
    """Enhanced Meeting model with Google Meet integration."""
    __tablename__ = 'meetings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)
    meeting_datetime = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=15)
    location = Column(String, default="Conference Room A")
    
    # Google Meet Integration Fields
    google_meet_link = Column(String)
    google_event_id = Column(String)  # Google Calendar Event ID
    google_meet_room_code = Column(String)  # Extract room code from meet link
    
    # Meeting Details
    organizer_id = Column(UUID(as_uuid=True), ForeignKey('staff.id'), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'))
    meeting_type = Column(String, default='staff')  # staff, department, emergency, training
    status = Column(String, default='scheduled')  # scheduled, in_progress, completed, cancelled
    priority = Column(String, default='normal')  # low, normal, high, urgent
    
    # Notification Settings
    email_sent = Column(Boolean, default=False)
    calendar_invites_sent = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)
    
    # Meeting Notes
    agenda = Column(Text)
    meeting_notes = Column(Text)  # Post-meeting notes
    action_items = Column(Text)   # Action items from the meeting
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    cancelled_at = Column(DateTime)

    # Relationships
    organizer = relationship("Staff", foreign_keys=[organizer_id])
    department = relationship("Department")

class MeetingParticipant(Base):
    """Meeting participants table."""
    __tablename__ = 'meeting_participants'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey('meetings.id'), nullable=False)
    staff_id = Column(UUID(as_uuid=True), ForeignKey('staff.id'), nullable=False)
    attendance_status = Column(String, default='invited')  # invited, accepted, declined, attended, absent
    response_datetime = Column(DateTime)
    join_datetime = Column(DateTime)  # When they joined the Google Meet
    leave_datetime = Column(DateTime)  # When they left the Google Meet

    # Relationships
    meeting = relationship("Meeting")
    staff = relationship("Staff")

class MeetingManager:
    """Manager class for meeting operations."""
    
    def __init__(self):
        self.session = SessionLocal()
    
    def create_meeting(self, 
                      title: str,
                      description: str,
                      meeting_datetime: datetime,
                      duration_minutes: int = 15,
                      google_meet_link: str = None,
                      google_event_id: str = None,
                      organizer_staff_id: str = None,
                      department_id: str = None,
                      meeting_type: str = 'staff',
                      priority: str = 'normal',
                      agenda: str = None) -> Meeting:
        """Create a new meeting record."""
        
        try:
            # Extract Google Meet room code if link provided
            google_meet_room_code = None
            if google_meet_link and 'meet.google.com/' in google_meet_link:
                google_meet_room_code = google_meet_link.split('meet.google.com/')[-1]
            
            # Create meeting
            meeting = Meeting(
                title=title,
                description=description,
                meeting_datetime=meeting_datetime,
                duration_minutes=duration_minutes,
                google_meet_link=google_meet_link,
                google_event_id=google_event_id,
                google_meet_room_code=google_meet_room_code,
                organizer_id=uuid.UUID(organizer_staff_id) if organizer_staff_id else None,
                department_id=uuid.UUID(department_id) if department_id else None,
                meeting_type=meeting_type,
                priority=priority,
                agenda=agenda,
                email_sent=True,  # Assuming emails are sent when meeting is created
                calendar_invites_sent=True  # Assuming calendar invites are sent
            )
            
            self.session.add(meeting)
            self.session.commit()
            
            return meeting
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def add_participants(self, meeting_id: str, staff_ids: List[str]):
        """Add participants to a meeting."""
        try:
            for staff_id in staff_ids:
                participant = MeetingParticipant(
                    meeting_id=uuid.UUID(meeting_id),
                    staff_id=uuid.UUID(staff_id),
                    attendance_status='invited'
                )
                self.session.add(participant)
            
            self.session.commit()
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_meetings_by_date(self, target_date: date) -> List[Meeting]:
        """Get all meetings for a specific date."""
        try:
            start_of_day = datetime.combine(target_date, datetime.min.time())
            end_of_day = datetime.combine(target_date, datetime.max.time())
            
            meetings = self.session.query(Meeting).filter(
                Meeting.meeting_datetime >= start_of_day,
                Meeting.meeting_datetime <= end_of_day,
                Meeting.status != 'cancelled'
            ).order_by(Meeting.meeting_datetime).all()
            
            return meetings
            
        except Exception as e:
            print(f"Error retrieving meetings by date: {e}")
            return []
    
    def get_meetings_by_time_range(self, start_datetime: datetime, end_datetime: datetime) -> List[Meeting]:
        """Get all meetings within a specific time range."""
        try:
            meetings = self.session.query(Meeting).filter(
                Meeting.meeting_datetime >= start_datetime,
                Meeting.meeting_datetime <= end_datetime,
                Meeting.status != 'cancelled'
            ).order_by(Meeting.meeting_datetime).all()
            
            return meetings
            
        except Exception as e:
            print(f"Error retrieving meetings by time range: {e}")
            return []
    
    def get_meeting_by_id(self, meeting_id: str) -> Optional[Meeting]:
        """Get a specific meeting by ID."""
        try:
            meeting = self.session.query(Meeting).filter(
                Meeting.id == uuid.UUID(meeting_id)
            ).first()
            
            return meeting
            
        except Exception as e:
            print(f"Error retrieving meeting by ID: {e}")
            return None
    
    def get_meetings_by_google_meet_link(self, google_meet_link: str) -> List[Meeting]:
        """Get meetings by Google Meet link."""
        try:
            meetings = self.session.query(Meeting).filter(
                Meeting.google_meet_link == google_meet_link
            ).all()
            
            return meetings
            
        except Exception as e:
            print(f"Error retrieving meetings by Google Meet link: {e}")
            return []
    
    def get_upcoming_meetings(self, days_ahead: int = 7) -> List[Meeting]:
        """Get all upcoming meetings within specified days."""
        try:
            now = datetime.now()
            future_date = now + timedelta(days=days_ahead)
            
            meetings = self.session.query(Meeting).filter(
                Meeting.meeting_datetime >= now,
                Meeting.meeting_datetime <= future_date,
                Meeting.status == 'scheduled'
            ).order_by(Meeting.meeting_datetime).all()
            
            return meetings
            
        except Exception as e:
            print(f"Error retrieving upcoming meetings: {e}")
            return []
    
    def get_meeting_participants(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get all participants for a meeting."""
        try:
            participants = self.session.query(MeetingParticipant).join(Staff).join(User).filter(
                MeetingParticipant.meeting_id == uuid.UUID(meeting_id)
            ).all()
            
            participant_data = []
            for participant in participants:
                participant_data.append({
                    'staff_id': str(participant.staff_id),
                    'name': f"{participant.staff.user.first_name} {participant.staff.user.last_name}",
                    'email': participant.staff.user.email,
                    'role': participant.staff.user.role,
                    'attendance_status': participant.attendance_status,
                    'join_time': participant.join_datetime.isoformat() if participant.join_datetime else None,
                    'leave_time': participant.leave_datetime.isoformat() if participant.leave_datetime else None
                })
            
            return participant_data
            
        except Exception as e:
            print(f"Error retrieving meeting participants: {e}")
            return []
    
    def update_meeting_status(self, meeting_id: str, status: str):
        """Update meeting status."""
        try:
            meeting = self.session.query(Meeting).filter(
                Meeting.id == uuid.UUID(meeting_id)
            ).first()
            
            if meeting:
                meeting.status = status
                meeting.updated_at = datetime.now()
                
                if status == 'cancelled':
                    meeting.cancelled_at = datetime.now()
                
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

    def search_meetings_by_title(self, title_query: str) -> List[Meeting]:
        """Search meetings by title (case-insensitive partial match)."""
        try:
            meetings = self.session.query(Meeting).filter(
                Meeting.title.ilike(f"%{title_query}%")
            ).order_by(Meeting.meeting_datetime.desc()).all()
            
            return meetings
            
        except Exception as e:
            print(f"Error searching meetings by title: {e}")
            return []

    def search_meetings_by_description(self, description_query: str) -> List[Meeting]:
        """Search meetings by description (case-insensitive partial match)."""
        try:
            meetings = self.session.query(Meeting).filter(
                Meeting.description.ilike(f"%{description_query}%")
            ).order_by(Meeting.meeting_datetime.desc()).all()
            
            return meetings
            
        except Exception as e:
            print(f"Error searching meetings by description: {e}")
            return []

    def search_meetings(self, search_query: str) -> List[Meeting]:
        """Search meetings by title OR description (case-insensitive partial match)."""
        try:
            from sqlalchemy import or_
            meetings = self.session.query(Meeting).filter(
                or_(
                    Meeting.title.ilike(f"%{search_query}%"),
                    Meeting.description.ilike(f"%{search_query}%")
                )
            ).order_by(Meeting.meeting_datetime.desc()).all()
            
            return meetings
            
        except Exception as e:
            print(f"Error searching meetings: {e}")
            return []
    
    def close(self):
        """Close the database session."""
        self.session.close()

# Convenience functions
def create_meeting_tables():
    """Create meeting tables in the database."""
    from database import engine
    Base.metadata.create_all(bind=engine, tables=[Meeting.__table__, MeetingParticipant.__table__])
    print("✅ Meeting tables created successfully!")

if __name__ == "__main__":
    # Create the tables
    create_meeting_tables()
    print("Meeting management system initialized!")
