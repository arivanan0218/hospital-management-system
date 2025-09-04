#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend-python'))

from datetime import datetime, timedelta
from database import get_db_session, Patient, PatientSupplyUsage, EquipmentUsage, Supply, Equipment, User, Staff, SupplyCategory, EquipmentCategory
import uuid

def create_sample_usage_records():
    """Create sample supply and equipment usage records for P1025."""
    
    print("=== Creating Sample Usage Records for P1025 ===")
    
    with get_db_session() as db:
        # Get patient P1025
        patient = db.query(Patient).filter(Patient.patient_number == "P1025").first()
        if not patient:
            print("❌ Patient P1025 not found")
            return
            
        print(f"✅ Found patient: {patient.first_name} {patient.last_name} (ID: {patient.id})")
        
        # Check if we already have records
        existing_supply = db.query(PatientSupplyUsage).filter(PatientSupplyUsage.patient_id == patient.id).count()
        existing_equipment = db.query(EquipmentUsage).filter(EquipmentUsage.patient_id == patient.id).count()
        
        print(f"📊 Existing records: {existing_supply} supply usage, {existing_equipment} equipment usage")
        
        # Create or find a supply item (Aspirin)
        aspirin = db.query(Supply).filter(Supply.name.ilike('%aspirin%')).first()
        if not aspirin:
            # First create a supply category if needed
            medication_category = db.query(SupplyCategory).filter(SupplyCategory.name.ilike('%medication%')).first()
            if not medication_category:
                medication_category = SupplyCategory(
                    id=uuid.uuid4(),
                    name="Medications",
                    description="Pharmaceutical supplies"
                )
                db.add(medication_category)
                db.commit()
                print("✅ Created Medications category")
            
            # Create aspirin supply item
            aspirin = Supply(
                id=uuid.uuid4(),
                name="Aspirin 81mg",
                item_code="SUP001", 
                description="Low-dose aspirin for cardiac care",
                unit_of_measure="tablets",
                current_stock=100,
                unit_cost=0.50,
                category_id=medication_category.id
            )
            db.add(aspirin)
            db.commit()
            print("✅ Created Aspirin supply item")
        else:
            print(f"✅ Found existing supply: {aspirin.name}")
        
        # Create or find ECG equipment
        ecg = db.query(Equipment).filter(Equipment.name.ilike('%ecg%')).first()
        if not ecg:
            # First create an equipment category if needed
            monitoring_category = db.query(EquipmentCategory).filter(EquipmentCategory.name.ilike('%monitor%')).first()
            if not monitoring_category:
                monitoring_category = EquipmentCategory(
                    id=uuid.uuid4(),
                    name="Monitoring Equipment",
                    description="Patient monitoring devices"
                )
                db.add(monitoring_category)
                db.commit()
                print("✅ Created Monitoring Equipment category")
            
            # Create ECG equipment
            ecg = Equipment(
                id=uuid.uuid4(),
                name="ECG Monitor",
                equipment_id="EQ001",
                description="12-lead ECG monitoring device",
                status="operational",
                category_id=monitoring_category.id
            )
            db.add(ecg)
            db.commit()
            print("✅ Created ECG equipment")
        else:
            print(f"✅ Found existing equipment: {ecg.name}")
        
        # Get a staff member for administered_by
        staff_member = db.query(Staff).first()
        if not staff_member:
            print("❌ No staff members found - creating records without administered_by")
            
        # Create supply usage record
        if existing_supply == 0:
            supply_usage = PatientSupplyUsage(
                id=uuid.uuid4(),
                patient_id=patient.id,
                supply_id=aspirin.id,
                quantity_used=2,
                prescribed_date=datetime.now() - timedelta(hours=2),
                administration_date=datetime.now() - timedelta(hours=1),
                administered_by_id=staff_member.user_id if staff_member else None,
                notes="Administered Aspirin 81mg for cardiac protection"
            )
            db.add(supply_usage)
            print("✅ Created supply usage record")
        else:
            print("✅ Supply usage records already exist")
        
        # Create equipment usage record
        if existing_equipment == 0:
            equipment_usage = EquipmentUsage(
                id=uuid.uuid4(),
                patient_id=patient.id,
                equipment_id=ecg.id,
                staff_id=staff_member.id if staff_member else None,
                start_time=datetime.now() - timedelta(hours=3),
                end_time=datetime.now() - timedelta(hours=2),
                duration_minutes=60,
                purpose="ECG monitoring during cardiac evaluation",
                notes="Normal sinus rhythm observed"
            )
            db.add(equipment_usage)
            print("✅ Created equipment usage record")
        else:
            print("✅ Equipment usage records already exist")
        
        # Commit all changes
        db.commit()
        
        # Verify records were created
        final_supply = db.query(PatientSupplyUsage).filter(PatientSupplyUsage.patient_id == patient.id).count()
        final_equipment = db.query(EquipmentUsage).filter(EquipmentUsage.patient_id == patient.id).count()
        
        print(f"\n📊 Final record counts: {final_supply} supply usage, {final_equipment} equipment usage")
        
        return True

if __name__ == "__main__":
    create_sample_usage_records()
