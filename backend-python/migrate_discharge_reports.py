"""
Database Migration for Discharge Report System
==============================================

This script adds the new tables required for comprehensive discharge reports.
"""

from sqlalchemy import text
from database import engine, SessionLocal, Base
import sys
import os

def create_discharge_report_tables():
    """Create the new tables for discharge report system."""
    try:
        print("🏥 Creating discharge report tables...")
        
        # Import all models to ensure they're registered
        from database import (
            Patient, Staff, Equipment, User, Bed, Appointment,
            TreatmentRecord, EquipmentUsage, StaffAssignment, DischargeReport
        )
        
        # Create all new tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Successfully created discharge report tables:")
        print("   - treatment_records")
        print("   - equipment_usage") 
        print("   - staff_assignments")
        print("   - discharge_reports")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def verify_tables_exist():
    """Verify that the new tables were created successfully."""
    try:
        print("� Verifying table creation...")
        
        with engine.connect() as conn:
            # Check if tables exist
            tables_to_check = [
                'treatment_records',
                'equipment_usage', 
                'staff_assignments',
                'discharge_reports'
            ]
            
            for table in tables_to_check:
                result = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table}'
                    );
                """))
                exists = result.scalar()
                
                if exists:
                    print(f"   ✅ {table} - EXISTS")
                else:
                    print(f"   ❌ {table} - NOT FOUND")
                    return False
        
        print("✅ All tables verified successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to verify tables: {e}")
        return False

def create_sample_data():
    """Create some sample data for testing."""
    try:
        print("📊 Creating sample discharge report data...")
        
        from database import Patient, Staff, User, TreatmentRecord
        import uuid
        from datetime import datetime
        
        db = SessionLocal()
        
        # Get first patient and doctor for sample data
        patient = db.query(Patient).first()
        doctor_staff = db.query(Staff).join(User).filter(User.role == 'doctor').first()
        
        if patient and doctor_staff:
            # Create a sample treatment record
            sample_treatment = TreatmentRecord(
                patient_id=patient.id,
                doctor_id=doctor_staff.user_id,
                treatment_type="medication",
                treatment_name="Sample Medication",
                description="Sample treatment for testing",
                dosage="500mg",
                frequency="twice daily",
                duration="7 days",
                start_date=datetime.now(),
                status="active"
            )
            
            db.add(sample_treatment)
            db.commit()
            
            print("✅ Sample treatment record created")
        else:
            print("⚠️  No patients or doctors found - skipping sample data")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

if __name__ == "__main__":
    print("🏥 HOSPITAL DISCHARGE REPORT SYSTEM - Database Migration")
    print("=" * 60)
    
    success = create_discharge_report_tables()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Add the new MCP tools to comprehensive_server.py")
        print("2. Test the discharge report generation")
        print("3. Integrate with your existing workflow")
        
        # Optionally create sample data
        create_sample = input("\nCreate sample data for testing? (y/n): ").lower()
        if create_sample == 'y':
            create_sample_data()
    else:
        print("\n❌ Migration failed!")
        print("Please check your database connection and try again.")
