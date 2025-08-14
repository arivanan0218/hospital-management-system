"""
Sample Data Preparation for Patient Discharge Report System
===========================================================

This script prepares comprehensive sample data for testing the discharge report system.
Includes patients, staff, equipment, treatments, and discharge scenarios.
"""

from datetime import datetime, timedelta
from database import (
    engine, SessionLocal, User, Patient, Staff, Department, Room, Bed, Equipment, 
    TreatmentRecord, EquipmentUsage, StaffAssignment, DischargeReport, EquipmentCategory
)
from sqlalchemy.exc import IntegrityError
import uuid

def create_sample_data():
    """Create comprehensive sample data for discharge testing."""
    
    session = SessionLocal()
    
    try:
        print("🏥 PREPARING SAMPLE DATA FOR DISCHARGE REPORT SYSTEM")
        print("=" * 60)
        
        # Clear existing data (optional - uncomment if needed)
        # print("🗑️  Clearing existing data...")
        # session.query(DischargeReport).delete()
        # session.query(EquipmentUsage).delete()
        # session.query(TreatmentRecord).delete()
        # session.query(StaffAssignment).delete()
        
        # 1. Create Equipment Categories
        print("1. Creating equipment categories...")
        categories = [
            ("monitoring", "Patient Monitoring Equipment"),
            ("respiratory", "Respiratory Care Equipment"),
            ("diagnostic", "Diagnostic Equipment"),
            ("therapeutic", "Therapeutic Equipment")
        ]
        
        category_objects = {}
        for cat_name, cat_desc in categories:
            try:
                category = EquipmentCategory(name=cat_name, description=cat_desc)
                session.add(category)
                session.flush()
                category_objects[cat_name] = category.id
                print(f"   ✅ Created category: {cat_name}")
            except IntegrityError:
                session.rollback()
                existing = session.query(EquipmentCategory).filter_by(name=cat_name).first()
                if existing:
                    category_objects[cat_name] = existing.id
                    print(f"   ♻️  Using existing category: {cat_name}")
        
        # 2. Create Departments
        print("2. Creating departments...")
        departments = [
            ("Emergency", "Emergency Department", "emergency@hospital.com", "555-0101", 1),
            ("Cardiology", "Heart and Vascular Department", "cardio@hospital.com", "555-0102", 2),
            ("Orthopedics", "Bone and Joint Department", "ortho@hospital.com", "555-0103", 3),
            ("General Medicine", "Internal Medicine Department", "medicine@hospital.com", "555-0104", 2)
        ]
        
        dept_objects = {}
        for name, desc, email, phone, floor in departments:
            try:
                dept = Department(
                    name=name,
                    description=desc,
                    email=email,
                    phone=phone,
                    floor_number=floor
                )
                session.add(dept)
                session.flush()
                dept_objects[name] = dept.id
                print(f"   ✅ Created department: {name}")
            except IntegrityError:
                session.rollback()
                existing = session.query(Department).filter_by(name=name).first()
                if existing:
                    dept_objects[name] = existing.id
                    print(f"   ♻️  Using existing department: {name}")
        
        # 3. Create Users
        print("3. Creating users...")
        users_data = [
            ("dr_smith", "john.smith@hospital.com", "doctor", "John", "Smith", "555-1001"),
            ("nurse_johnson", "mary.johnson@hospital.com", "nurse", "Mary", "Johnson", "555-1002"),
            ("admin_wilson", "admin.wilson@hospital.com", "admin", "David", "Wilson", "555-1003"),
            ("dr_brown", "sarah.brown@hospital.com", "doctor", "Sarah", "Brown", "555-1004"),
            ("nurse_davis", "jane.davis@hospital.com", "nurse", "Jane", "Davis", "555-1005")
        ]
        
        user_objects = {}
        for username, email, role, first, last, phone in users_data:
            try:
                user = User(
                    username=username,
                    email=email,
                    password_hash="hashed_password_123",
                    role=role,
                    first_name=first,
                    last_name=last,
                    phone=phone
                )
                session.add(user)
                session.flush()
                user_objects[username] = user.id
                print(f"   ✅ Created user: {username} ({first} {last})")
            except IntegrityError:
                session.rollback()
                existing = session.query(User).filter_by(username=username).first()
                if existing:
                    user_objects[username] = existing.id
                    print(f"   ♻️  Using existing user: {username}")
        
        # 4. Create Staff
        print("4. Creating staff members...")
        staff_data = [
            ("dr_smith", "EMP001", "Cardiology", "Senior Cardiologist", "MD12345", "day_shift", "Interventional Cardiology", 150000),
            ("nurse_johnson", "EMP002", "Cardiology", "Registered Nurse", "RN67890", "day_shift", "Cardiac Care", 75000),
            ("dr_brown", "EMP003", "Emergency", "Emergency Physician", "MD54321", "night_shift", "Emergency Medicine", 140000),
            ("nurse_davis", "EMP004", "General Medicine", "Registered Nurse", "RN98765", "day_shift", "General Care", 70000)
        ]
        
        staff_objects = {}
        for username, emp_id, dept_name, position, license, shift, spec, salary in staff_data:
            try:
                staff = Staff(
                    user_id=user_objects[username],
                    employee_id=emp_id,
                    department_id=dept_objects[dept_name],
                    position=position,
                    license_number=license,
                    shift_pattern=shift,
                    specialization=spec,
                    salary=salary,
                    hire_date=datetime.now() - timedelta(days=365),
                    status="active"
                )
                session.add(staff)
                session.flush()
                staff_objects[username] = staff.id
                print(f"   ✅ Created staff: {emp_id} ({position})")
            except IntegrityError:
                session.rollback()
                existing = session.query(Staff).filter_by(employee_id=emp_id).first()
                if existing:
                    staff_objects[username] = existing.id
                    print(f"   ♻️  Using existing staff: {emp_id}")
        
        # 5. Create Rooms and Beds
        print("5. Creating rooms and beds...")
        rooms_data = [
            ("101", "Cardiology", "ICU", 1, 2),
            ("102", "Cardiology", "Standard", 1, 2),
            ("201", "Emergency", "Emergency", 1, 3),
            ("301", "General Medicine", "Standard", 1, 4)
        ]
        
        bed_objects = {}
        for room_num, dept_name, room_type, floor, capacity in rooms_data:
            try:
                room = Room(
                    room_number=room_num,
                    department_id=dept_objects[dept_name],
                    room_type=room_type,
                    floor_number=floor,
                    capacity=capacity
                )
                session.add(room)
                session.flush()
                
                # Create beds for this room
                for bed_num in range(1, capacity + 1):
                    bed_number = f"{room_num}-{bed_num}"
                    bed = Bed(
                        bed_number=bed_number,
                        room_id=room.id,
                        bed_type="standard",
                        status="available"
                    )
                    session.add(bed)
                    session.flush()
                    bed_objects[bed_number] = bed.id
                    
                print(f"   ✅ Created room {room_num} with {capacity} beds")
            except IntegrityError:
                session.rollback()
                print(f"   ♻️  Room {room_num} already exists")
        
        # 6. Create Equipment
        print("6. Creating medical equipment...")
        equipment_data = [
            ("EQ001", "Cardiac Monitor", "monitoring", "Philips", "IntelliVue MX450", "SN001234", "Cardiology", "Room 101"),
            ("EQ002", "Ventilator", "respiratory", "Medtronic", "Puritan Bennett 980", "SN005678", "Emergency", "Room 201"),
            ("EQ003", "IV Pump", "therapeutic", "Baxter", "Sigma Spectrum", "SN009876", "Cardiology", "Mobile"),
            ("EQ004", "Blood Pressure Monitor", "monitoring", "Omron", "HBP-1320", "SN001122", "General Medicine", "Room 301"),
            ("EQ005", "Oxygen Concentrator", "respiratory", "Philips", "EverFlo", "SN003344", "General Medicine", "Mobile")
        ]
        
        equipment_objects = {}
        for eq_id, name, cat_name, mfg, model, serial, dept_name, location in equipment_data:
            try:
                equipment = Equipment(
                    equipment_id=eq_id,
                    name=name,
                    category_id=category_objects[cat_name],
                    manufacturer=mfg,
                    model=model,
                    serial_number=serial,
                    department_id=dept_objects[dept_name],
                    location=location,
                    purchase_date=datetime.now() - timedelta(days=730),
                    cost=25000.00,
                    warranty_expiry=datetime.now() + timedelta(days=365),
                    status="operational"
                )
                session.add(equipment)
                session.flush()
                equipment_objects[eq_id] = equipment.id
                print(f"   ✅ Created equipment: {eq_id} ({name})")
            except IntegrityError:
                session.rollback()
                existing = session.query(Equipment).filter_by(equipment_id=eq_id).first()
                if existing:
                    equipment_objects[eq_id] = existing.id
                    print(f"   ♻️  Using existing equipment: {eq_id}")
        
        # 7. Create Sample Patients
        print("7. Creating sample patients...")
        patients_data = [
            ("P001", "Alice", "Williams", "1985-05-15", "female", "alice.williams@email.com", "555-2001", 
             "123 Oak Street, Springfield", "O+", "Hypertension", "Penicillin", "John Williams", "555-2002"),
            ("P002", "Robert", "Johnson", "1970-12-08", "male", "robert.johnson@email.com", "555-2003",
             "456 Pine Avenue, Springfield", "A-", "Diabetes Type 2", "None", "Lisa Johnson", "555-2004"),
            ("P003", "Maria", "Garcia", "1992-03-22", "female", "maria.garcia@email.com", "555-2005",
             "789 Elm Drive, Springfield", "B+", "Asthma", "Aspirin", "Carlos Garcia", "555-2006"),
            ("P004", "James", "Wilson", "1965-09-30", "male", "james.wilson@email.com", "555-2007",
             "321 Maple Lane, Springfield", "AB+", "Heart Disease", "Shellfish", "Nancy Wilson", "555-2008")
        ]
        
        patient_objects = {}
        for (p_num, first, last, dob, gender, email, phone, address, blood, 
             history, allergies, ec_name, ec_phone) in patients_data:
            try:
                patient = Patient(
                    patient_number=p_num,
                    first_name=first,
                    last_name=last,
                    date_of_birth=datetime.strptime(dob, "%Y-%m-%d").date(),
                    gender=gender,
                    email=email,
                    phone=phone,
                    address=address,
                    blood_type=blood,
                    medical_history=history,
                    allergies=allergies,
                    emergency_contact_name=ec_name,
                    emergency_contact_phone=ec_phone
                )
                session.add(patient)
                session.flush()
                patient_objects[p_num] = patient.id
                print(f"   ✅ Created patient: {p_num} ({first} {last})")
            except IntegrityError:
                session.rollback()
                existing = session.query(Patient).filter_by(patient_number=p_num).first()
                if existing:
                    patient_objects[p_num] = existing.id
                    print(f"   ♻️  Using existing patient: {p_num}")
        
        # Commit all base data
        session.commit()
        print("\n📊 BASE DATA CREATED SUCCESSFULLY!")
        
        # 8. Create Sample Discharge Scenarios
        print("\n8. Creating sample discharge scenarios...")
        
        # Scenario 1: Cardiac Patient - Alice Williams
        print("   🏥 Scenario 1: Cardiac Patient Discharge (Alice Williams)")
        patient_id = patient_objects["P001"]
        doctor_id = staff_objects["dr_smith"] 
        nurse_id = staff_objects["nurse_johnson"]
        bed_id = bed_objects["101-1"]
        
        # Assign bed to patient
        from database import Patient as PatientModel, Bed as BedModel
        patient = session.query(PatientModel).filter_by(id=patient_id).first()
        bed = session.query(BedModel).filter_by(id=bed_id).first()
        bed.status = "occupied"
        bed.current_patient_id = patient_id
        bed.admission_date = datetime.now() - timedelta(days=3)
        
        # Add treatments
        treatments = [
            ("medication", "Lisinopril", "ACE Inhibitor for blood pressure", "10mg", "once daily"),
            ("medication", "Metoprolol", "Beta-blocker for heart rate", "50mg", "twice daily"),
            ("procedure", "ECG", "12-lead electrocardiogram", "", ""),
            ("procedure", "Echocardiogram", "Cardiac ultrasound", "", ""),
            ("therapy", "Cardiac Rehabilitation", "Exercise and education program", "", "3 sessions")
        ]
        
        for t_type, t_name, t_desc, dosage, frequency in treatments:
            treatment = TreatmentRecord(
                patient_id=patient_id,
                doctor_id=doctor_id,
                treatment_type=t_type,
                treatment_name=t_name,
                description=t_desc,
                dosage=dosage,
                frequency=frequency,
                start_date=datetime.now() - timedelta(days=2),
                status="completed",
                effectiveness="good response"
            )
            session.add(treatment)
        
        # Add equipment usage
        equipment_usage = [
            ("EQ001", "Continuous heart monitoring", "HR: 72-85 bpm, stable rhythm", 2880),  # 48 hours
            ("EQ003", "IV medication administration", "Fluids and medications delivered", 1440),  # 24 hours
            ("EQ004", "Blood pressure monitoring", "BP: 130/80 to 125/75 mmHg", 180)  # 3 hours total
        ]
        
        for eq_id, purpose, readings, duration in equipment_usage:
            usage = EquipmentUsage(
                patient_id=patient_id,
                equipment_id=equipment_objects[eq_id],
                staff_id=nurse_id,
                purpose=purpose,
                start_time=datetime.now() - timedelta(days=2),
                duration_minutes=duration,
                readings=readings,
                status="completed"
            )
            session.add(usage)
        
        # Add staff assignments
        assignments = [
            (doctor_id, "attending_physician", "Primary care physician", "day_shift"),
            (nurse_id, "primary_nurse", "Patient care coordination", "day_shift")
        ]
        
        for s_id, assignment_type, responsibilities, shift in assignments:
            assignment = StaffAssignment(
                patient_id=patient_id,
                staff_id=s_id,
                bed_id=bed_id,
                assignment_type=assignment_type,
                responsibilities=responsibilities,
                shift=shift,
                start_date=datetime.now() - timedelta(days=3),
                status="active"
            )
            session.add(assignment)
        
        print("      ✅ Added treatments, equipment usage, and staff assignments")
        
        # Scenario 2: Emergency Patient - Robert Johnson
        print("   🚨 Scenario 2: Emergency Patient Discharge (Robert Johnson)")
        patient_id_2 = patient_objects["P002"]
        doctor_id_2 = staff_objects["dr_brown"]
        nurse_id_2 = staff_objects["nurse_davis"]
        bed_id_2 = bed_objects["201-1"]
        
        # Assign bed
        bed_2 = session.query(BedModel).filter_by(id=bed_id_2).first()
        bed_2.status = "occupied"
        bed_2.current_patient_id = patient_id_2
        bed_2.admission_date = datetime.now() - timedelta(hours=8)
        
        # Add emergency treatments
        treatments_2 = [
            ("medication", "Insulin", "Blood sugar management", "10 units", "as needed"),
            ("procedure", "Blood Glucose Test", "Monitor blood sugar levels", "", "every 2 hours"),
            ("medication", "Normal Saline", "IV fluid replacement", "1000ml", "over 4 hours")
        ]
        
        for t_type, t_name, t_desc, dosage, frequency in treatments_2:
            treatment = TreatmentRecord(
                patient_id=patient_id_2,
                doctor_id=doctor_id_2,
                treatment_type=t_type,
                treatment_name=t_name,
                description=t_desc,
                dosage=dosage,
                frequency=frequency,
                start_date=datetime.now() - timedelta(hours=6),
                status="completed",
                effectiveness="blood sugar stabilized"
            )
            session.add(treatment)
        
        print("      ✅ Added emergency treatments and monitoring")
        
        # Commit all sample data
        session.commit()
        
        print("\n🎉 SAMPLE DATA PREPARATION COMPLETE!")
        print("=" * 60)
        print(f"✅ Created {len(departments)} departments")
        print(f"✅ Created {len(users_data)} users and staff members")
        print(f"✅ Created {len(patients_data)} patients")
        print(f"✅ Created {len(equipment_data)} medical equipment items")
        print(f"✅ Created 2 complete discharge scenarios with:")
        print("   - Treatment records")
        print("   - Equipment usage logs")
        print("   - Staff assignments")
        print("   - Bed assignments")
        
        print("\n📋 DISCHARGE TEST SCENARIOS READY:")
        print("1. Cardiac Patient (Alice Williams, P001) - 3-day stay")
        print("2. Emergency Patient (Robert Johnson, P002) - 8-hour stay")
        
        print("\n🚀 READY FOR DISCHARGE REPORT TESTING!")
        print("Use these bed IDs for generating discharge reports:")
        print(f"   - Bed 101-1 (Alice Williams - Cardiac)")
        print(f"   - Bed 201-1 (Robert Johnson - Emergency)")
        
        return {
            'patients': patient_objects,
            'staff': staff_objects,
            'beds': bed_objects,
            'equipment': equipment_objects,
            'departments': dept_objects
        }
        
    except Exception as e:
        print(f"❌ ERROR CREATING SAMPLE DATA: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        session.close()

def create_discharge_test_parameters():
    """Generate sample parameters for discharge report testing."""
    
    print("\n📝 SAMPLE DISCHARGE PARAMETERS FOR TESTING:")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "Cardiac Patient Discharge",
            "bed_id": "Use bed ID from scenario 1 (101-1)",
            "discharge_condition": "stable",
            "discharge_destination": "home",
            "discharge_instructions": """
1. Continue taking Lisinopril 10mg once daily for blood pressure
2. Take Metoprolol 50mg twice daily for heart rate control
3. Follow low-sodium, heart-healthy diet
4. Monitor blood pressure daily and record readings
5. Gradual increase in physical activity as tolerated
6. Call doctor if chest pain, shortness of breath, or swelling occurs
            """.strip(),
            "follow_up_required": "Cardiology follow-up in 1 week, Primary care in 2 weeks",
            "generated_by_user_id": "Use admin user ID"
        },
        {
            "name": "Emergency Patient Discharge", 
            "bed_id": "Use bed ID from scenario 2 (201-1)",
            "discharge_condition": "improved",
            "discharge_destination": "home",
            "discharge_instructions": """
1. Continue diabetes medication as prescribed
2. Monitor blood sugar levels 3 times daily
3. Follow diabetic diet plan provided
4. Stay hydrated and avoid excessive sugar intake
5. Take rest for next 24-48 hours
6. Return immediately if blood sugar >300 or <70 mg/dL
            """.strip(),
            "follow_up_required": "Endocrinology follow-up in 3-5 days, Emergency follow-up if symptoms return",
            "generated_by_user_id": "Use admin user ID"
        },
        {
            "name": "Orthopedic Patient Discharge",
            "bed_id": "Create new scenario or use available bed",
            "discharge_condition": "stable with restrictions",
            "discharge_destination": "home with home health services",
            "discharge_instructions": """
1. Keep surgical site clean and dry
2. No weight bearing on affected limb for 6 weeks
3. Use crutches or walker as instructed
4. Take pain medication as needed
5. Apply ice packs 15-20 minutes every 2-3 hours
6. Attend physical therapy as scheduled
7. Watch for signs of infection: fever, increased pain, redness, drainage
            """.strip(),
            "follow_up_required": "Orthopedic surgeon follow-up in 1 week, Physical therapy 3x weekly",
            "generated_by_user_id": "Use doctor user ID"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}:")
        print(f"   bed_id: '{scenario['bed_id']}'")
        print(f"   discharge_condition: '{scenario['discharge_condition']}'")
        print(f"   discharge_destination: '{scenario['discharge_destination']}'")
        print(f"   discharge_instructions: '''{scenario['discharge_instructions']}'''")
        print(f"   follow_up_required: '{scenario['follow_up_required']}'")
        print(f"   generated_by_user_id: '{scenario['generated_by_user_id']}'")
    
    return scenarios

if __name__ == "__main__":
    # Create comprehensive sample data
    result = create_sample_data()
    
    if result:
        # Show sample discharge parameters
        create_discharge_test_parameters()
        
        print(f"\n✅ SAMPLE DATA PREPARATION SUCCESSFUL!")
        print("🏥 Your hospital management system is now ready for discharge report testing!")
    else:
        print("❌ Sample data preparation failed. Check the error messages above.")
