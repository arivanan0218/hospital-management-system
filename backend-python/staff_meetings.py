"""Staff Meeting table and related functionality."""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from database import Base

# Association table for staff meetings and participants
staff_meeting_participants = Table(
    'staff_meeting_participants',
    Base.metadata,
    Column('meeting_id', UUID(as_uuid=True), ForeignKey('staff_meetings.id')),
    Column('staff_id', UUID(as_uuid=True), ForeignKey('staff.id'))
)

class StaffMeeting(Base):
    """Staff Meeting model."""
    __tablename__ = 'staff_meetings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String)
    meeting_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    location = Column(String)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey('staff.id'), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'))
    status = Column(String, default='scheduled')  # scheduled, completed, cancelled
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    organizer = relationship("Staff", foreign_keys=[organizer_id])
    department = relationship("Department")
    participants = relationship("Staff", secondary=staff_meeting_participants, backref="meetings")
