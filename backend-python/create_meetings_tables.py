"""Create both meeting tables - legacy and new enhanced Meeting table."""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import Base
from staff_meetings import StaffMeeting, staff_meeting_participants
from meeting_management import Meeting, MeetingParticipant
import os
from dotenv import load_dotenv

def create_tables():
    """Create both the legacy staff meetings tables and the new enhanced Meeting tables."""
    load_dotenv()
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    # Create database engine
    engine = create_engine(database_url)
    
    # Create legacy tables
    Base.metadata.create_all(engine, tables=[StaffMeeting.__table__, staff_meeting_participants])
    print("✅ Legacy staff meetings tables created successfully!")
    
    # Create new enhanced meeting tables (with Google Meet support)
    Base.metadata.create_all(engine, tables=[Meeting.__table__, MeetingParticipant.__table__])
    print("✅ Enhanced Meeting tables (with Google Meet support) created successfully!")
    
    print("\n📊 Database now has both legacy and enhanced meeting systems:")
    print("  - StaffMeeting (legacy) - for backward compatibility")
    print("  - Meeting (enhanced) - with Google Meet integration, used by new scheduler")

if __name__ == "__main__":
    create_tables()
