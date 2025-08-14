"""
Patient Discharge Report System - Demo Script
============================================

This script demonstrates the complete patient discharge workflow
with treatment tracking, equipment usage, and report generation.
"""

import uuid
from datetime import datetime, timedelta
from database import SessionLocal, Patient, Staff, User, Bed, Equipment, Department
from discharge_service import PatientDischargeReportGenerator
from comprehensive_server import (
    add_treatment_record, add_equipment_usage, assign_staff_to_patient,
    generate_discharge_report
)

def demo_discharge_workflow():
    """Demonstrate the complete discharge workflow."""
    
    print("🏥 PATIENT DISCHARGE REPORT SYSTEM - DEMO")
    print("=" * 50)
    
    try:
        # Get sample data from database
        db = SessionLocal()
        
        # Find a patient
        patient = db.query(Patient).first()
        if not patient:
            print("❌ No patients found in database. Please add a patient first.")
            return False
        
        # Find a doctor
        doctor = db.query(User).filter(User.role == 'doctor').first()
        if not doctor:
            print("❌ No doctors found in database. Please add a doctor first.")
            return False
        
        # Find a nurse
        nurse_staff = db.query(Staff).join(User).filter(User.role == 'nurse').first()
        if not nurse_staff:
            print("❌ No nurses found in database. Please add a nurse first.")
            return False
        
        # Get nurse user info while session is still active
        nurse_user = nurse_staff.user
        
        # Find a bed
        bed = db.query(Bed).filter(Bed.status == 'available').first()
        if not bed:
            print("❌ No available beds found. Please add a bed first.")
            return False
        
        # Find equipment
        equipment = db.query(Equipment).filter(Equipment.status == 'available').first()
        if not equipment:
            print("❌ No equipment found. Please add equipment first.")
            return False
        
        db.close()
        
        print(f"👤 Patient: {patient.first_name} {patient.last_name} (ID: {patient.patient_number})")
        print(f"👨‍⚕️ Doctor: {doctor.first_name} {doctor.last_name}")
        print(f"👩‍⚕️ Nurse: {nurse_user.first_name} {nurse_user.last_name}")
        print(f"🛏️ Bed: {bed.bed_number}")
        print(f"🏥 Equipment: {equipment.name}")
        
        print("\n📋 SIMULATING PATIENT STAY...")
        print("-" * 30)
        
        # Step 1: Assign bed to patient (simulate admission)
        print("1. Assigning bed to patient...")
        bed_db = SessionLocal()
        bed_record = bed_db.query(Bed).filter(Bed.id == bed.id).first()
        bed_record.patient_id = patient.id
        bed_record.status = "occupied"
        bed_record.admission_date = datetime.now() - timedelta(days=2)  # Admitted 2 days ago
        bed_db.commit()
        bed_db.close()
        print("   ✅ Patient admitted to bed")
        
        # Step 2: Assign staff to patient
        print("2. Assigning staff to patient...")
        staff_result = assign_staff_to_patient(
            patient_id=str(patient.id),
            staff_id=str(nurse_staff.id),
            assignment_type="primary_nurse",
            shift="day",
            responsibilities="Primary care, medication administration",
            bed_id=str(bed.id)
        )
        print(f"   ✅ Staff assigned: {staff_result['message']}")
        
        # Step 3: Add treatments
        print("3. Adding treatments...")
        
        # Add medication
        treatment1 = add_treatment_record(
            patient_id=str(patient.id),
            doctor_id=str(doctor.id),
            treatment_type="medication",
            treatment_name="Amoxicillin",
            description="Antibiotic treatment for infection",
            dosage="500mg",
            frequency="3 times daily",
            duration="7 days",
            bed_id=str(bed.id)
        )
        print(f"   ✅ Medication added: {treatment1['message']}")
        
        # Add procedure
        treatment2 = add_treatment_record(
            patient_id=str(patient.id),
            doctor_id=str(doctor.id),
            treatment_type="procedure",
            treatment_name="Blood Pressure Monitoring",
            description="Regular vital signs monitoring",
            bed_id=str(bed.id)
        )
        print(f"   ✅ Procedure added: {treatment2['message']}")
        
        # Step 4: Add equipment usage
        print("4. Recording equipment usage...")
        equipment_result = add_equipment_usage(
            patient_id=str(patient.id),
            equipment_id=str(equipment.id),
            staff_id=str(nurse_staff.id),
            purpose="Continuous vital signs monitoring",
            duration_minutes=2880,  # 2 days
            settings='{"heart_rate_alarm": 120, "bp_alarm": "180/100"}',
            readings='{"avg_hr": 78, "avg_bp": "128/82", "temp": "98.6F"}',
            bed_id=str(bed.id)
        )
        print(f"   ✅ Equipment usage recorded: {equipment_result['message']}")
        
        # Step 5: Generate discharge report
        print("5. Generating discharge report...")
        discharge_result = generate_discharge_report(
            bed_id=str(bed.id),
            discharge_condition="improved",
            discharge_destination="home",
            discharge_instructions="Continue taking Amoxicillin as prescribed. Rest for 3 days. Follow up with primary care physician in 1 week.",
            follow_up_required="Primary care follow-up in 1 week. Blood work in 2 weeks.",
            generated_by_user_id=str(doctor.id)
        )
        
        if discharge_result["success"]:
            print(f"   ✅ Discharge report generated: {discharge_result['report_number']}")
            print(f"   📄 Report ID: {discharge_result['report_id']}")
            
            # Display formatted report
            print("\n📋 DISCHARGE REPORT PREVIEW:")
            print("=" * 50)
            report_preview = discharge_result['formatted_report'][:1000] + "..." if len(discharge_result['formatted_report']) > 1000 else discharge_result['formatted_report']
            print(report_preview)
            
            # Save full report to file
            report_filename = f"discharge_report_{discharge_result['report_number']}.md"
            with open(report_filename, 'w') as f:
                f.write(discharge_result['formatted_report'])
            print(f"\n💾 Full report saved to: {report_filename}")
            
        else:
            print(f"   ❌ Failed to generate report: {discharge_result['message']}")
            return False
        
        # Step 6: Discharge the bed
        print("6. Discharging patient from bed...")
        bed_db = SessionLocal()
        bed_record = bed_db.query(Bed).filter(Bed.id == bed.id).first()
        bed_record.patient_id = None
        bed_record.status = "available"
        bed_record.discharge_date = datetime.now()
        bed_db.commit()
        bed_db.close()
        print("   ✅ Patient discharged, bed available")
        
        print("\n🎉 DISCHARGE WORKFLOW COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"📊 Patient: {patient.first_name} {patient.last_name}")
        print(f"📅 Length of Stay: 2 days")
        print(f"📋 Report Number: {discharge_result['report_number']}")
        print(f"💾 Report File: {report_filename}")
        print(f"🏥 Discharge Condition: Improved")
        print(f"🏠 Discharge Destination: Home")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = demo_discharge_workflow()
    if success:
        print("\n✅ Demo completed successfully!")
        print("📚 The discharge report system is ready for production use.")
    else:
        print("\n❌ Demo failed. Please check the error messages above.")
