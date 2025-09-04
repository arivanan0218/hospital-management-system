#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend-python'))

from datetime import datetime, timedelta
from database import get_db_session, Patient, Bed
import uuid

def assign_p1025_to_bed():
    """Assign patient P1025 to a bed for testing."""
    
    print("=== Assigning P1025 to a Bed ===")
    
    with get_db_session() as db:
        # Get patient P1025
        patient = db.query(Patient).filter(Patient.patient_number == "P1025").first()
        if not patient:
            print("❌ Patient P1025 not found")
            return
            
        print(f"✅ Found patient: {patient.first_name} {patient.last_name} (ID: {patient.id})")
        
        # Check if patient is already assigned to a bed
        current_bed = db.query(Bed).filter(Bed.patient_id == patient.id).first()
        if current_bed:
            print(f"✅ Patient already assigned to bed: {current_bed.bed_number} (status: {current_bed.status})")
            if current_bed.status != "occupied":
                current_bed.status = "occupied"
                current_bed.admission_date = datetime.now() - timedelta(days=1)
                db.commit()
                print("✅ Updated bed status to occupied")
            return
        
        # Find an available bed
        available_bed = db.query(Bed).filter(Bed.status == "available").first()
        if not available_bed:
            print("❌ No available beds found")
            return
            
        # Assign patient to bed
        available_bed.patient_id = patient.id
        available_bed.status = "occupied"
        available_bed.admission_date = datetime.now() - timedelta(days=1)
        available_bed.discharge_date = None
        
        db.commit()
        
        print(f"✅ Assigned patient P1025 to bed {available_bed.bed_number}")
        print(f"   Bed ID: {available_bed.id}")
        print(f"   Status: {available_bed.status}")
        print(f"   Admission Date: {available_bed.admission_date}")

if __name__ == "__main__":
    assign_p1025_to_bed()
