#!/usr/bin/env python3
"""
Database schema setup for meeting scheduling and discharge reports
"""

import sys
import os

# Add the backend-python directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Database configuration using user's credentials
DATABASE_URL = "postgresql://postgres:Smrm%405670@localhost:5433/hospital_management"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_meeting_tables():
    """Create indexes for existing meeting scheduling tables"""
    
    # The meetings and meeting_participants tables already exist, just add indexes
    meeting_indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_meetings_meeting_datetime ON meetings(meeting_datetime);",
        "CREATE INDEX IF NOT EXISTS idx_meetings_status ON meetings(status);",
        "CREATE INDEX IF NOT EXISTS idx_meetings_type ON meetings(meeting_type);",
        "CREATE INDEX IF NOT EXISTS idx_meeting_participants_meeting_id ON meeting_participants(meeting_id);",
        "CREATE INDEX IF NOT EXISTS idx_meeting_participants_staff_id ON meeting_participants(staff_id);"
    ]
    
    return meeting_indexes_sql

def create_discharge_tables():
    """Create tables for discharge reporting functionality (only missing tables/indexes)"""
    
    # discharge_reports, equipment_usage, treatment_records already exist, just add missing tables/indexes
    staff_interactions_sql = """
    CREATE TABLE IF NOT EXISTS staff_interactions (
        id SERIAL PRIMARY KEY,
        patient_id VARCHAR(50) NOT NULL,
        staff_name VARCHAR(100) NOT NULL,
        staff_role VARCHAR(50),
        interaction_type VARCHAR(50),
        description TEXT,
        interaction_date DATE,
        duration_minutes INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Create indexes for better performance
    discharge_indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_discharge_reports_patient_id ON discharge_reports(patient_id);",
        "CREATE INDEX IF NOT EXISTS idx_discharge_reports_discharge_date ON discharge_reports(discharge_date);",
        "CREATE INDEX IF NOT EXISTS idx_treatment_records_patient_id ON treatment_records(patient_id);",
        "CREATE INDEX IF NOT EXISTS idx_equipment_usage_patient_id ON equipment_usage(patient_id);",
        "CREATE INDEX IF NOT EXISTS idx_staff_interactions_patient_id ON staff_interactions(patient_id);",
        "CREATE INDEX IF NOT EXISTS idx_staff_interactions_date ON staff_interactions(interaction_date);"
    ]
    
    return [staff_interactions_sql] + discharge_indexes_sql

def setup_database():
    """Create all necessary tables for meeting and discharge functionality"""
    
    try:
        # Create database engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            logger.info(f"Connected to PostgreSQL: {version}")
        
        # Get all table creation SQL statements
        all_sql_statements = create_meeting_tables() + create_discharge_tables()
        
        # Execute all statements
        with engine.connect() as conn:
            for sql_statement in all_sql_statements:
                try:
                    conn.execute(text(sql_statement))
                    conn.commit()
                    logger.info(f"Executed: {sql_statement[:50]}...")
                except Exception as e:
                    logger.error(f"Failed to execute SQL: {str(e)}")
                    conn.rollback()
                    raise
        
        logger.info("✅ All database tables created successfully!")
        
        # Verify tables were created
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('meetings', 'meeting_participants', 'discharge_reports', 
                                  'treatment_records', 'equipment_usage', 'staff_interactions')
                ORDER BY table_name;
            """))
            
            tables = result.fetchall()
            logger.info(f"Created tables: {[table[0] for table in tables]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🏥 Setting up Hospital Management System database tables...")
    print(f"📊 Database URL: {DATABASE_URL.replace('Smrm%405670', '***')}")
    
    success = setup_database()
    
    if success:
        print("\n✅ Database setup completed successfully!")
        print("\n📋 Created tables:")
        print("   - meetings (meeting scheduling)")
        print("   - meeting_participants (meeting attendees)")
        print("   - discharge_reports (patient discharge summaries)")
        print("   - treatment_records (treatment history)")
        print("   - equipment_usage (equipment usage tracking)")
        print("   - staff_interactions (staff-patient interactions)")
    else:
        print("\n❌ Database setup failed. Check the logs above.")
        sys.exit(1)
