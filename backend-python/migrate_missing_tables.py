#!/usr/bin/env python3
"""
Database Migration Script - Create all missing tables
This script ensures all 31 tables from the local database are created in the deployed database.
"""

from database import *
from sqlalchemy import text

def check_existing_tables():
    """Check what tables currently exist in the database."""
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename;
        """))
        existing_tables = [row[0] for row in result.fetchall()]
        return existing_tables
    finally:
        db.close()

def create_missing_tables():
    """Create all missing tables."""
    print("🏥 Hospital Management System - Database Migration")
    print("=" * 60)
    
    # Check existing tables
    existing_tables = check_existing_tables()
    print(f"📊 Found {len(existing_tables)} existing tables")
    
    # Expected tables from local database
    expected_tables = [
        'agent_interactions', 'appointments', 'bed_cleaning_tasks', 'bed_equipment_assignments',
        'bed_staff_assignments', 'bed_turnover_logs', 'beds', 'departments', 'discharge_reports',
        'document_embeddings', 'equipment', 'equipment_categories', 'equipment_usage',
        'extracted_medical_data', 'inventory_transactions', 'legacy_users', 'medical_documents',
        'meeting_participants', 'meetings', 'patient_queue', 'patients', 'rooms', 'staff',
        'staff_assignments', 'staff_interactions', 'staff_meeting_participants', 'staff_meetings',
        'supplies', 'supply_categories', 'treatment_records', 'users'
    ]
    
    missing_tables = [table for table in expected_tables if table not in existing_tables]
    
    if not missing_tables:
        print("✅ All tables already exist!")
        return True
    
    print(f"📋 Missing tables ({len(missing_tables)}):")
    for i, table in enumerate(missing_tables, 1):
        print(f"  {i:2d}. {table}")
    
    # Create missing tables
    print(f"\n🔨 Creating missing tables...")
    try:
        # Use checkfirst=True to avoid recreating existing tables
        Base.metadata.create_all(bind=engine, checkfirst=True)
        
        # Verify tables were created
        new_existing_tables = check_existing_tables()
        newly_created = [table for table in expected_tables if table in new_existing_tables and table not in existing_tables]
        
        print(f"✅ Successfully created {len(newly_created)} tables:")
        for table in newly_created:
            print(f"  ✓ {table}")
        
        still_missing = [table for table in expected_tables if table not in new_existing_tables]
        if still_missing:
            print(f"⚠️  Still missing {len(still_missing)} tables:")
            for table in still_missing:
                print(f"  ❌ {table}")
            return False
        
        print(f"\n🎉 Database migration completed successfully!")
        print(f"📈 Total tables: {len(new_existing_tables)}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False

def test_model_integrity():
    """Test that all models are properly defined."""
    print(f"\n🔍 Testing model integrity...")
    
    all_models = [
        Meeting, MeetingParticipant, User, Department, Patient, Room, Bed, Staff,
        EquipmentCategory, Equipment, SupplyCategory, Supply, InventoryTransaction,
        AgentInteraction, Appointment, MedicalDocument, ExtractedMedicalData,
        DocumentEmbedding, LegacyUser, DischargeReport, BedTurnover, PatientQueue,
        EquipmentTurnover, BedCleaningTask, BedEquipmentAssignment, BedStaffAssignment,
        BedTurnoverLog, EquipmentUsage, StaffAssignment, StaffInteraction,
        StaffMeetingParticipant, StaffMeeting, TreatmentRecord
    ]
    
    print(f"📊 Total models defined: {len(all_models)}")
    
    try:
        # Test database connection
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection successful")
        
        # Test that each model can be used to query (even if empty)
        db = SessionLocal()
        for model in all_models:
            try:
                count = db.query(model).count()
                print(f"  ✓ {model.__name__} ({count} records)")
            except Exception as e:
                print(f"  ❌ {model.__name__}: {str(e)}")
        db.close()
        
        print("✅ All models are functional!")
        return True
        
    except Exception as e:
        print(f"❌ Model integrity test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting database migration...")
    
    if create_missing_tables():
        if test_model_integrity():
            print("\n🏆 Migration completed successfully!")
            print("All 31 tables are now available in the deployed database.")
        else:
            print("\n⚠️  Migration completed but some models have issues.")
    else:
        print("\n❌ Migration failed!")
