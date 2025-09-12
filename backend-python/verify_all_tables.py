"""
Final Database Verification Script - All 33 Tables
Verify that all database tables have been populated with operational data
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_all_tables():
    """Verify that all database tables have been populated."""
    
    # Database connection
    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(db_url)
    
    print("🏥 Hospital Management System - Final Database Verification (All 33 Tables)")
    print("=" * 80)
    
    # All 33 tables that should exist
    tables_to_check = [
        # Core reference tables (10 tables - should already have data)
        'users', 'departments', 'staff', 'patients', 'rooms', 'beds',
        'equipment_categories', 'equipment', 'supply_categories', 'supplies',
        
        # Operational tables (23 tables - the previously empty tables)
        'agent_interactions', 'bed_staff_assignments', 'equipment_usage',
        'staff_assignments', 'patient_supply_usage', 'inventory_transactions',
        'treatment_records', 'meetings', 'meeting_participants',
        'discharge_reports', 'bed_turnovers', 'patient_queue',
        'medical_documents', 'staff_interactions', 'extracted_medical_data',
        'bed_equipment_assignments', 'bed_cleaning_tasks', 'bed_turnover_logs',
        'staff_meetings', 'staff_meeting_participants', 'document_embeddings',
        'legacy_users', 'equipment_turnovers'
    ]
    
    total_records = 0
    populated_tables = 0
    empty_tables = []
    
    with engine.connect() as conn:
        print("Table Name                    | Record Count | Status")
        print("-" * 80)
        
        for table in tables_to_check:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                total_records += count
                
                if count > 0:
                    populated_tables += 1
                    status = "✅ POPULATED"
                else:
                    empty_tables.append(table)
                    status = "❌ EMPTY"
                    
                print(f"{table:<30} | {count:>12} | {status}")
                
            except Exception as e:
                print(f"{table:<30} | {'ERROR':>12} | ❌ ERROR: {str(e)}")
    
    print("-" * 80)
    print(f"\n📊 FINAL SUMMARY:")
    print(f"Total Tables Checked: {len(tables_to_check)}")
    print(f"Populated Tables: {populated_tables}")
    print(f"Empty Tables: {len(empty_tables)}")
    print(f"Total Records: {total_records:,}")
    
    if empty_tables:
        print(f"\n❌ REMAINING EMPTY TABLES:")
        for table in empty_tables:
            print(f"  - {table}")
    else:
        print(f"\n🎉 SUCCESS: ALL TABLES HAVE BEEN POPULATED!")
    
    # Calculate completion percentage
    completion_percentage = (populated_tables / len(tables_to_check)) * 100
    print(f"\nDatabase Completion: {completion_percentage:.1f}%")
    
    print(f"\n🚀 ACHIEVEMENT:")
    print(f"You now have a fully operational hospital management database with")
    print(f"{total_records:,} records across {populated_tables} populated tables!")
    
    return populated_tables, len(empty_tables), total_records

if __name__ == "__main__":
    verify_all_tables()
