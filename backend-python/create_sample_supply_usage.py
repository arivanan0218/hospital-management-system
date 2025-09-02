#!/usr/bin/env python3
"""
Create sample PatientSupplyUsage records for testing discharge reports
"""

import sys
import os
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, Patient, Supply, User, PatientSupplyUsage

def create_sample_supply_usage():
    """Create sample patient supply usage records for testing"""
    
    print("🏥 Creating sample PatientSupplyUsage records...")
    
    db = SessionLocal()
    
    try:
        # Get existing patients
        patients = db.query(Patient).limit(5).all()
        if not patients:
            print("❌ No patients found. Please create patients first.")
            return False
        
        # Get existing supplies
        supplies = db.query(Supply).all()
        if not supplies:
            print("❌ No supplies found. Please run migrate_supply_usage.py first.")
            return False
        
        # Get existing users (doctors/nurses)
        users = db.query(User).filter(User.role.in_(["doctor", "nurse"])).limit(5).all()
        if not users:
            print("❌ No medical staff found. Please create users first.")
            return False
        
        print(f"✅ Found {len(patients)} patients, {len(supplies)} supplies, {len(users)} medical staff")
        
        # Create sample supply usage records
        sample_records = []
        
        for i, patient in enumerate(patients):
            # Create 2-4 supply usage records per patient
            num_records = min(4, len(supplies))
            
            for j in range(num_records):
                supply = supplies[j % len(supplies)]
                doctor = users[j % len(users)]
                nurse = users[(j + 1) % len(users)]
                
                # Generate realistic dates within the last 30 days
                prescribed_date = datetime.now() - timedelta(days=random.randint(1, 30))
                administration_date = prescribed_date + timedelta(hours=random.randint(1, 24))
                start_date = prescribed_date.date()
                end_date = start_date + timedelta(days=random.randint(1, 7))
                
                # Generate realistic quantities and costs
                quantity = random.randint(1, 10)
                unit_cost = float(supply.unit_cost or 1.0)
                total_cost = quantity * unit_cost
                
                # Create the usage record
                usage_record = PatientSupplyUsage(
                    patient_id=patient.id,
                    supply_id=supply.id,
                    quantity_used=quantity,
                    unit_cost=Decimal(str(unit_cost)),
                    total_cost=Decimal(str(total_cost)),
                    prescribed_by_id=doctor.id,
                    administered_by_id=nurse.id,
                    dosage=f"{random.randint(1, 5)} {supply.unit_of_measure}",
                    frequency=random.choice(["once daily", "twice daily", "as needed", "every 4 hours"]),
                    administration_route=random.choice(["oral", "IV", "injection", "topical"]),
                    indication=f"Treatment for {random.choice(['pain management', 'infection', 'symptom relief', 'preventive care'])}",
                    prescribed_date=prescribed_date,
                    administration_date=administration_date,
                    start_date=start_date,
                    end_date=end_date,
                    status=random.choice(["prescribed", "administered", "completed"]),
                    effectiveness=random.choice(["effective", "partial", "unknown"]),
                    side_effects=random.choice([None, "Mild nausea", "Drowsiness", "No side effects reported"]),
                    notes=f"Sample record {i+1}-{j+1} for testing discharge reports"
                )
                
                sample_records.append(usage_record)
                print(f"✅ Created usage record for {patient.first_name} - {supply.name}")
        
        # Add all records to database
        db.add_all(sample_records)
        db.commit()
        
        print(f"\n✅ Successfully created {len(sample_records)} sample PatientSupplyUsage records!")
        print(f"📊 Total records in database: {db.query(PatientSupplyUsage).count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample supply usage: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    import random
    create_sample_supply_usage()
