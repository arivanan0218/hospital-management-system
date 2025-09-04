"""Script to re-admit patient P1025 for discharge testing."""

import sys
import os
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def readmit_p1025():
    """Re-admit patient P1025 to a bed for discharge testing."""
    try:
        from database import SessionLocal, Patient, Bed
        
        db = SessionLocal()
        
        # Find patient P1025
        patient = db.query(Patient).filter(Patient.patient_number == 'P1025').first()
        if not patient:
            print("❌ Patient P1025 not found")
            return
            
        print(f"📋 Found patient: {patient.first_name} {patient.last_name}")
        print(f"   Current status: {patient.status}")
        
        # Find an available bed
        available_bed = db.query(Bed).filter(Bed.patient_id.is_(None), Bed.status == 'available').first()
        if not available_bed:
            print("❌ No available beds found")
            return
            
        print(f"🛏️  Found available bed: {available_bed.bed_number}")
        
        # Re-admit the patient
        patient.status = 'active'
        available_bed.patient_id = patient.id
        available_bed.status = 'occupied'
        available_bed.admission_date = datetime.now()
        available_bed.discharge_date = None
        
        db.commit()
        
        print("✅ Patient P1025 re-admitted successfully!")
        print(f"   Patient Status: {patient.status}")
        print(f"   Bed: {available_bed.bed_number}")
        print(f"   You can now test: 'Discharge Patient P1025'")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error re-admitting patient: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🏥 Re-admitting Patient P1025 for Discharge Testing")
    print("=" * 55)
    readmit_p1025()
