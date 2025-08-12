#!/usr/bin/env python3
"""
Create sample data for a bed to ensure discharge reports work in UI
"""

from database import SessionLocal, Bed, Patient, User, Staff, TreatmentRecord, EquipmentUsage, StaffAssignment
import uuid
from datetime import datetime, timedelta

def setup_bed_for_ui_testing():
    """Setup a bed with sample data that can be used for UI testing"""
    db = SessionLocal()
    
    try:
        print("Setting up bed with sample data for UI testing...")
        print("=" * 50)
        
        # Get the first occupied bed
        bed = db.query(Bed).filter(Bed.status == 'occupied').first()
        if not bed:
            # If no occupied beds, use an available one and assign a patient
            bed = db.query(Bed).filter(Bed.status == 'available').first()
            patient = db.query(Patient).first()
            if bed and patient:
                bed.patient_id = patient.id
                bed.status = 'occupied'
                bed.admission_date = datetime.now() - timedelta(days=2)
                db.commit()
        
        if not bed or not bed.patient_id:
            print("❌ No suitable bed found")
            return None
            
        patient = bed.patient
        print(f"✅ Using bed: {bed.bed_number} (ID: {bed.id})")
        print(f"✅ Patient: {patient.first_name} {patient.last_name}")
        
        # Ensure admission date is set
        if not bed.admission_date:
            bed.admission_date = datetime.now() - timedelta(days=2)
            db.commit()
            
        admission_date = bed.admission_date
        
        # Get a doctor
        doctor = db.query(User).filter(User.role == 'doctor').first()
        if not doctor:
            doctor = User(
                username="dr.johnson",
                email="dr.johnson@hospital.com", 
                password_hash="hashed_password",
                role="doctor",
                first_name="Dr. Sarah",
                last_name="Johnson"
            )
            db.add(doctor)
            db.commit()
        
        # Clear existing treatment records for this bed to avoid duplicates
        existing_treatments = db.query(TreatmentRecord).filter(
            TreatmentRecord.bed_id == bed.id
        ).all()
        for treatment in existing_treatments:
            db.delete(treatment)
            
        # Add treatment records
        print("Adding treatment records...")
        treatments = [
            TreatmentRecord(
                patient_id=patient.id,
                doctor_id=doctor.id,
                bed_id=bed.id,
                treatment_type="medication",
                treatment_name="Pain Relief",
                description="Prescribed for post-surgery pain management",
                dosage="400mg", 
                frequency="Every 6 hours",
                duration="5 days",
                start_date=admission_date,
                status="active"
            ),
            TreatmentRecord(
                patient_id=patient.id,
                doctor_id=doctor.id,
                bed_id=bed.id,
                treatment_type="procedure",
                treatment_name="Vital Signs Monitoring",
                description="Regular monitoring of blood pressure, heart rate, and temperature",
                start_date=admission_date + timedelta(hours=2),
                status="ongoing"
            ),
            TreatmentRecord(
                patient_id=patient.id,
                doctor_id=doctor.id,
                bed_id=bed.id,
                treatment_type="medication",
                treatment_name="Antibiotics",
                description="Preventive antibiotic treatment",
                dosage="250mg",
                frequency="Twice daily",
                duration="7 days",
                start_date=admission_date + timedelta(hours=6),
                status="active"
            )
        ]
        
        for treatment in treatments:
            db.add(treatment)
            
        # Add staff assignment
        staff = db.query(Staff).first()
        if staff:
            # Clear existing assignments
            existing_assignments = db.query(StaffAssignment).filter(
                StaffAssignment.bed_id == bed.id
            ).all()
            for assignment in existing_assignments:
                db.delete(assignment)
                
            assignment = StaffAssignment(
                patient_id=patient.id,
                staff_id=staff.id,
                bed_id=bed.id,
                assignment_type="primary_nurse",
                start_date=admission_date,
                shift="day",
                responsibilities="Primary nursing care, medication administration, patient monitoring"
            )
            db.add(assignment)
            
        db.commit()
        
        print(f"✅ Sample data created successfully!")
        print(f"✅ Bed ID for UI testing: {bed.id}")
        print(f"✅ This bed now has treatment records and can generate discharge reports")
        
        return str(bed.id)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    bed_id = setup_bed_for_ui_testing()
    if bed_id:
        print(f"\n🎯 Use this bed ID in your UI tests: {bed_id}")
        print("This bed now has sample data and will generate successful discharge reports!")
