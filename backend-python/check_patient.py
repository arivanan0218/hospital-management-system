#!/usr/bin/env python3
"""Script to check if a patient exists in the database."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, Patient

def check_patient(patient_number):
    """Check if a patient exists with the given patient number."""
    session = SessionLocal()
    try:
        # Get all patients first
        all_patients = session.query(Patient).order_by(Patient.patient_number).all()
        print("All patients in database:")
        for patient in all_patients:
            print(f"  Number: {patient.patient_number}, Name: {patient.first_name} {patient.last_name}")
        
        print(f"\nSearching for patient number: {patient_number}")
        
        # Check for specific patient
        patient = session.query(Patient).filter(Patient.patient_number == patient_number).first()
        
        if patient:
            print(f"✅ Found patient: {patient.first_name} {patient.last_name}")
            print(f"   ID: {patient.id}")
            print(f"   Email: {patient.email}")
            print(f"   Phone: {patient.phone}")
            return True
        else:
            print(f"❌ Patient {patient_number} not found in database")
            return False
            
    except Exception as e:
        print(f"Error checking patient: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    patient_number = sys.argv[1] if len(sys.argv) > 1 else "P532865"
    check_patient(patient_number)
