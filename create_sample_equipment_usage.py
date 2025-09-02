#!/usr/bin/env python3
"""
Create sample EquipmentUsage records for testing discharge reports
"""

import sys
import os
import uuid
from datetime import datetime, timedelta
import random

# Add the backend-python directory to the Python path
sys.path.append('./backend-python')

from database import SessionLocal, Patient, Equipment, Staff, EquipmentUsage

def create_sample_equipment_usage():
    """Create sample equipment usage records for testing"""
    
    print("🏥 Creating sample EquipmentUsage records...")
    
    db = SessionLocal()
    
    try:
        # Get existing patients
        patients = db.query(Patient).limit(5).all()
        if not patients:
            print("❌ No patients found. Please create patients first.")
            return False
        
        # Get available equipment
        available_equipment = db.query(Equipment).filter(Equipment.status == "available").limit(10).all()
        if not available_equipment:
            print("❌ No available equipment found.")
            return False
        
        # Get existing staff
        staff_members = db.query(Staff).limit(5).all()
        if not staff_members:
            print("❌ No staff found. Please create staff first.")
            return False
        
        print(f"✅ Found {len(patients)} patients, {len(available_equipment)} available equipment, {len(staff_members)} staff")
        
        # Create sample equipment usage records
        sample_records = []
        
        for i, patient in enumerate(patients):
            # Create 2-3 equipment usage records per patient
            num_records = min(3, len(available_equipment))
            
            for j in range(num_records):
                equipment = available_equipment[j % len(available_equipment)]
                staff = staff_members[j % len(staff_members)]
                
                # Generate realistic dates within the last 30 days
                start_time = datetime.now() - timedelta(days=random.randint(1, 30))
                duration_minutes = random.randint(15, 120)  # 15 minutes to 2 hours
                end_time = start_time + timedelta(minutes=duration_minutes)
                
                # Generate realistic purposes based on equipment type
                purposes = {
                    "Monitoring Equipment": ["Patient monitoring", "Vital signs check", "Continuous monitoring"],
                    "Life Support": ["Respiratory support", "Ventilation assistance", "Life support monitoring"],
                    "Diagnostic Equipment": ["Diagnostic imaging", "Medical examination", "Patient assessment"],
                    "Transport Equipment": ["Patient transport", "Mobility assistance", "Transfer support"],
                    "Laboratory Equipment": ["Lab testing", "Sample analysis", "Diagnostic testing"],
                    "Emergency Equipment": ["Emergency response", "Trauma care", "Critical care"],
                    "Rehabilitation Equipment": ["Physical therapy", "Rehabilitation session", "Therapeutic exercise"],
                    "Sterilization Equipment": ["Equipment cleaning", "Sterilization process", "Infection control"],
                    "Communication Equipment": ["Patient communication", "Information access", "Data recording"]
                }
                
                category_name = equipment.category.name if equipment.category else "Monitoring Equipment"
                purpose_options = purposes.get(category_name, ["Medical procedure", "Patient care", "Treatment"])
                purpose = random.choice(purpose_options)
                
                # Create the usage record
                usage_record = EquipmentUsage(
                    patient_id=patient.id,
                    equipment_id=equipment.id,
                    staff_id=staff.id,
                    bed_id=patient.bed_id if hasattr(patient, 'bed_id') else None,
                    start_time=start_time,
                    end_time=end_time,
                    duration_minutes=duration_minutes,
                    purpose=purpose,
                    settings=random.choice([None, '{"mode": "standard", "intensity": "medium"}', '{"frequency": "continuous"}']),
                    readings=random.choice([None, '{"heart_rate": "72 bpm", "blood_pressure": "120/80"}', '{"temperature": "98.6°F", "oxygen_sat": "98%"}']),
                    status=random.choice(["completed", "active", "interrupted"]),
                    notes=f"Sample equipment usage record {i+1}-{j+1} for testing discharge reports"
                )
                
                sample_records.append(usage_record)
                print(f"✅ Created usage record for {patient.first_name} - {equipment.name}")
        
        # Add all records to database
        db.add_all(sample_records)
        db.commit()
        
        print(f"\n✅ Successfully created {len(sample_records)} sample EquipmentUsage records!")
        print(f"📊 Total records in database: {db.query(EquipmentUsage).count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample equipment usage: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_equipment_usage()
