#!/usr/bin/env python3
"""
Create sample data and test complete discharge workflow
"""

from database import SessionLocal, Patient, Bed, User, Staff, TreatmentRecord, EquipmentUsage, StaffAssignment
from discharge_service import PatientDischargeReportGenerator
import uuid
from datetime import datetime, timedelta

def create_sample_discharge_scenario():
    """Create a complete discharge scenario with sample data"""
    db = SessionLocal()
    
    try:
        print("Setting up sample discharge scenario...")
        print("=" * 50)
        
        # Get the bed
        bed_id = 'efc306b2-e3a8-4bab-aa4e-176410338e95'
        bed = db.query(Bed).filter(Bed.id == uuid.UUID(bed_id)).first()
        
        if not bed:
            print("Bed not found!")
            return
            
        # Get a sample patient
        patient = db.query(Patient).first()
        if not patient:
            print("No patients available!")
            return
            
        print(f"Patient: {patient.first_name} {patient.last_name}")
        print(f"Bed: {bed.bed_number}")
        
        # Get a doctor (user with role doctor)
        doctor = db.query(User).filter(User.role == 'doctor').first()
        if not doctor:
            # Create a sample doctor
            doctor = User(
                username="dr.smith",
                email="dr.smith@hospital.com",
                password_hash="hashed_password",
                role="doctor",
                first_name="Dr. John",
                last_name="Smith"
            )
            db.add(doctor)
            db.commit()
            
        # Temporarily assign patient to bed for historical context
        admission_date = datetime.now() - timedelta(days=3)
        
        # Add some treatment records
        print("Adding treatment records...")
        
        treatment1 = TreatmentRecord(
            patient_id=patient.id,
            doctor_id=doctor.id,
            bed_id=uuid.UUID(bed_id),
            treatment_type="medication",
            treatment_name="Antibiotics",
            description="Prescribed for infection",
            dosage="500mg",
            frequency="Twice daily",
            duration="7 days",
            start_date=admission_date,
            status="completed"
        )
        db.add(treatment1)
        
        treatment2 = TreatmentRecord(
            patient_id=patient.id,
            doctor_id=doctor.id,
            bed_id=uuid.UUID(bed_id),
            treatment_type="procedure",
            treatment_name="Blood Test",
            description="Routine blood work",
            start_date=admission_date + timedelta(days=1),
            status="completed"
        )
        db.add(treatment2)
        
        # Add staff assignment
        print("Adding staff assignment...")
        staff = db.query(Staff).first()
        if staff:
            assignment = StaffAssignment(
                patient_id=patient.id,
                staff_id=staff.id,
                bed_id=uuid.UUID(bed_id),
                assignment_type="primary_nurse",
                start_date=admission_date,
                shift="day",
                responsibilities="Patient care and monitoring"
            )
            db.add(assignment)
        
        db.commit()
        print("Sample data created successfully!")
        
        # Now generate the discharge report
        print("\nGenerating discharge report...")
        print("=" * 40)
        
        generator = PatientDischargeReportGenerator()
        result = generator.generate_discharge_report(
            bed_id=bed_id,
            discharge_condition='stable',
            discharge_destination='home',
            discharge_instructions='Continue medication as prescribed. Follow up in 1 week.',
            follow_up_required='Primary care physician appointment in 1 week',
            generated_by_user_id=str(doctor.id)
        )
        
        print(f"Success: {result.get('success')}")
        
        if result.get('success'):
            print(f"Report Number: {result.get('report_number')}")
            print(f"Patient: {result.get('patient_name')}")
            print(f"Report ID: {result.get('report_id')}")
            
            # Save the report to file
            report_content = result.get('formatted_report', '')
            if report_content:
                filename = f"discharge_report_{result.get('report_number')}.md"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                print(f"Report saved to: {filename}")
                
                # Show preview
                print("\n--- Report Preview (first 800 characters) ---")
                print(report_content[:800])
                if len(report_content) > 800:
                    print("...")
        else:
            print(f"Error: {result.get('message')}")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_discharge_scenario()
