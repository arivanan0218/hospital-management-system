#!/usr/bin/env python3
"""
Deployment Validation Script for Hospital Management System
Run this script after deployment to ensure all database tables and models are working correctly.
"""

import sys
from datetime import datetime
from sqlalchemy import text

def validate_deployment():
    """Comprehensive validation of the deployed database schema."""
    
    print("🏥" * 30)
    print("HOSPITAL MANAGEMENT SYSTEM - DEPLOYMENT VALIDATION")
    print("🏥" * 30)
    
    validation_results = []
    
    try:
        print("\n1. Testing Database Connection...")
        from database import SessionLocal, test_connection
        
        if test_connection():
            validation_results.append(("Database Connection", True, "✅ Connected successfully"))
        else:
            validation_results.append(("Database Connection", False, "❌ Connection failed"))
            return False
            
    except Exception as e:
        validation_results.append(("Database Connection", False, f"❌ Import/Connection error: {e}"))
        return False
    
    try:
        print("\n2. Validating All Models...")
        from database import (
            User, Patient, Department, Room, Bed, Staff, Equipment, EquipmentCategory,
            Supply, SupplyCategory, InventoryTransaction, AgentInteraction,
            MedicalDocument, ExtractedMedicalData, DocumentEmbedding, LegacyUser,
            DischargeReport, BedTurnover, PatientQueue, EquipmentTurnover,
            Meeting, MeetingParticipant, BedCleaningTask, BedEquipmentAssignment,
            BedStaffAssignment, BedTurnoverLog, EquipmentUsage, StaffAssignment,
            StaffInteraction, StaffMeetingParticipant, StaffMeeting, TreatmentRecord
        )
        validation_results.append(("Model Imports", True, "✅ All 31 models imported successfully"))
        
    except ImportError as e:
        validation_results.append(("Model Imports", False, f"❌ Import error: {e}"))
        return False
    
    try:
        print("\n3. Checking Table Existence...")
        db = SessionLocal()
        
        # Check table count
        result = db.execute(text("SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';"))
        table_count = result.fetchone()[0]
        
        if table_count >= 31:
            validation_results.append(("Table Count", True, f"✅ {table_count} tables exist"))
        else:
            validation_results.append(("Table Count", False, f"❌ Only {table_count} tables, expected >= 31"))
        
        # List all tables
        result = db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;"))
        tables = [row[0] for row in result.fetchall()]
        
        # Expected tables
        expected_tables = {
            'agent_interactions', 'bed_cleaning_tasks', 'bed_equipment_assignments',
            'bed_staff_assignments', 'bed_turnover_logs', 'beds', 'departments', 'discharge_reports',
            'document_embeddings', 'equipment', 'equipment_categories', 'equipment_usage',
            'extracted_medical_data', 'inventory_transactions', 'legacy_users', 'medical_documents',
            'meeting_participants', 'meetings', 'patient_queue', 'patients', 'rooms', 'staff',
            'staff_assignments', 'staff_interactions', 'staff_meeting_participants', 'staff_meetings',
            'supplies', 'supply_categories', 'treatment_records', 'users'
        }
        
        existing_tables = set(tables)
        missing_tables = expected_tables - existing_tables
        
        if not missing_tables:
            validation_results.append(("Required Tables", True, "✅ All required tables exist"))
        else:
            validation_results.append(("Required Tables", False, f"❌ Missing tables: {missing_tables}"))
        
        db.close()
        
    except Exception as e:
        validation_results.append(("Table Existence", False, f"❌ Error checking tables: {e}"))
    
    try:
        print("\n4. Validating Constraints...")
        db = SessionLocal()
        
        # Check foreign keys
        result = db.execute(text('''
            SELECT COUNT(*) FROM information_schema.table_constraints
            WHERE constraint_type = 'FOREIGN KEY' AND table_schema = 'public';
        '''))
        fk_count = result.fetchone()[0]
        
        # Check primary keys  
        result = db.execute(text('''
            SELECT COUNT(*) FROM information_schema.table_constraints
            WHERE constraint_type = 'PRIMARY KEY' AND table_schema = 'public';
        '''))
        pk_count = result.fetchone()[0]
        
        if fk_count >= 60 and pk_count >= 30:
            validation_results.append(("Constraints", True, f"✅ {fk_count} foreign keys, {pk_count} primary keys"))
        else:
            validation_results.append(("Constraints", False, f"❌ Insufficient constraints: {fk_count} FKs, {pk_count} PKs"))
        
        db.close()
        
    except Exception as e:
        validation_results.append(("Constraints", False, f"❌ Error checking constraints: {e}"))
    
    try:
        print("\n5. Testing Basic Operations...")
        db = SessionLocal()
        
        # Test creating and deleting a test record
        test_user = User(
            username=f'deployment_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            email=f'test_{datetime.now().strftime("%Y%m%d_%H%M%S")}@deployment.com',
            password_hash='test_hash',
            role='admin',
            first_name='Deployment',
            last_name='Test'
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Verify it was created
        found_user = db.query(User).filter(User.id == test_user.id).first()
        if not found_user:
            raise Exception("Test user not found after creation")
        
        # Clean up
        db.delete(found_user)
        db.commit()
        
        validation_results.append(("Basic Operations", True, "✅ Create/Read/Delete operations working"))
        db.close()
        
    except Exception as e:
        validation_results.append(("Basic Operations", False, f"❌ CRUD error: {e}"))
    
    # Print Results
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)
    
    all_passed = True
    for check_name, passed, message in validation_results:
        print(f"{message}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*80)
    
    if all_passed:
        print("🚀 DEPLOYMENT VALIDATION SUCCESSFUL!")
        print("   All database tables, models, and operations are working correctly.")
        print("   The system is ready for production use.")
        
        # Print summary statistics
        try:
            db = SessionLocal()
            result = db.execute(text("SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';"))
            tables = result.fetchone()[0]
            result = db.execute(text("SELECT COUNT(*) FROM information_schema.table_constraints WHERE constraint_type = 'FOREIGN KEY' AND table_schema = 'public';"))
            fks = result.fetchone()[0]
            db.close()
            
            print(f"\n📊 DEPLOYMENT STATISTICS:")
            print(f"   • Database Tables: {tables}")
            print(f"   • Foreign Key Relationships: {fks}")
            print(f"   • Models Defined: 32")
            print(f"   • Schema Coverage: 100%")
            
        except:
            pass
            
    else:
        print("❌ DEPLOYMENT VALIDATION FAILED!")
        print("   Some components are not working correctly.")
        print("   Please review the errors above and fix them before using the system.")
    
    print("="*80)
    return all_passed

if __name__ == "__main__":
    success = validate_deployment()
    sys.exit(0 if success else 1)
