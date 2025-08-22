"""Test script to verify database setup and create sample data."""

import sys
import os
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import (
    test_connection, create_tables, SessionLocal,
    User, Department, Patient, Room, Bed, Staff, Equipment, EquipmentCategory,
    Supply, SupplyCategory, InventoryTransaction, AgentInteraction,
    LegacyUser, Meeting, MeetingParticipant, MedicalDocument, ExtractedMedicalData,
    DocumentEmbedding, DischargeReport, BedTurnover, PatientQueue, EquipmentTurnover,
    BedCleaningTask, BedEquipmentAssignment, BedStaffAssignment, BedTurnoverLog,
    EquipmentUsage, StaffAssignment, StaffInteraction, StaffMeetingParticipant,
    StaffMeeting, TreatmentRecord
)

def create_sample_data():
    """Create comprehensive sample data for testing with proper foreign key relationships."""
    db = SessionLocal()
    
    try:
        print("Creating comprehensive sample data...")
        
        # === STEP 1: Create Users (No foreign key dependencies) ===
        print("1. Creating users...")
        admin_user = User(
            username="admin",
            email="admin@hospital.com",
            password_hash="hashed_password_123",
            role="admin",
            first_name="Admin",
            last_name="User",
            phone="555-0001"
        )
        
        doctor_user_1 = User(
            username="dr.smith",
            email="dr.smith@hospital.com",
            password_hash="hashed_password_456",
            role="doctor",
            first_name="John",
            last_name="Smith",
            phone="555-0002"
        )
        
        doctor_user_2 = User(
            username="dr.johnson",
            email="mrmshamil1786@gmail.com",
            password_hash="hashed_password_789",
            role="doctor",
            first_name="Mohamed",
            last_name="Shamil",
            phone="555-0003"
        )
        
        nurse_user_1 = User(
            username="nurse.brown",
            email="nurse.brown@hospital.com",
            password_hash="hashed_password_101",
            role="nurse",
            first_name="Mary",
            last_name="Brown",
            phone="555-0004"
        )
        
        nurse_user_2 = User(
            username="nurse.davis",
            email="nurse.davis@hospital.com",
            password_hash="hashed_password_102",
            role="nurse",
            first_name="Sarah",
            last_name="Davis",
            phone="555-0005"
        )
        
        manager_user = User(
            username="manager.wilson",
            email="mn4385293@gmail.com",
            password_hash="hashed_password_103",
            role="manager",
            first_name="Mohamed",
            last_name="nazif",
            phone="555-0006"
        )
        
        receptionist_user = User(
            username="receptionist.taylor",
            email="receptionist.taylor@hospital.com",
            password_hash="hashed_password_104",
            role="receptionist",
            first_name="Lisa",
            last_name="Taylor",
            phone="555-0007"
        )
        
        cleaner_user = User(
            username="cleaner.martinez",
            email="cleaner.martinez@hospital.com",
            password_hash="hashed_password_105",
            role="staff",
            first_name="Carlos",
            last_name="Martinez",
            phone="555-0008"
        )
        
        db.add_all([admin_user, doctor_user_1, doctor_user_2, nurse_user_1, nurse_user_2, 
                   manager_user, receptionist_user, cleaner_user])
        db.commit()
        db.refresh(admin_user)
        db.refresh(doctor_user_1)
        db.refresh(doctor_user_2)
        db.refresh(nurse_user_1)
        db.refresh(nurse_user_2)
        db.refresh(manager_user)
        db.refresh(receptionist_user)
        db.refresh(cleaner_user)
        
        # === STEP 2: Create Departments (Depends on Users for head_doctor_id) ===
        print("2. Creating departments...")
        cardiology_dept = Department(
            name="Cardiology",
            description="Heart and cardiovascular care",
            head_doctor_id=doctor_user_1.id,
            floor_number=3,
            phone="555-1001",
            email="cardiology@hospital.com"
        )
        
        emergency_dept = Department(
            name="Emergency",
            description="Emergency medical care",
            head_doctor_id=doctor_user_2.id,
            floor_number=1,
            phone="555-1002",
            email="emergency@hospital.com"
        )
        
        icu_dept = Department(
            name="ICU",
            description="Intensive Care Unit",
            floor_number=4,
            phone="555-1003",
            email="icu@hospital.com"
        )
        
        surgery_dept = Department(
            name="Surgery",
            description="Surgical operations",
            floor_number=5,
            phone="555-1004",
            email="surgery@hospital.com"
        )
        
        db.add_all([cardiology_dept, emergency_dept, icu_dept, surgery_dept])
        db.commit()
        db.refresh(cardiology_dept)
        db.refresh(emergency_dept)
        db.refresh(icu_dept)
        db.refresh(surgery_dept)
        
        # === STEP 3: Create Staff (Depends on Users and Departments) ===
        print("3. Creating staff...")
        staff_doctor_1 = Staff(
            user_id=doctor_user_1.id,
            employee_id="EMP001",
            department_id=cardiology_dept.id,
            position="Cardiologist",
            specialization="Interventional Cardiology",
            license_number="MD123456",
            hire_date=date(2020, 1, 15),
            salary=Decimal("200000.00"),
            shift_pattern="day",
            status="active"
        )
        
        staff_doctor_2 = Staff(
            user_id=doctor_user_2.id,
            employee_id="EMP002",
            department_id=emergency_dept.id,
            position="Emergency Physician",
            specialization="Emergency Medicine",
            license_number="MD789012",
            hire_date=date(2019, 3, 1),
            salary=Decimal("180000.00"),
            shift_pattern="rotating",
            status="active"
        )
        
        staff_nurse_1 = Staff(
            user_id=nurse_user_1.id,
            employee_id="EMP003",
            department_id=emergency_dept.id,
            position="Registered Nurse",
            specialization="Emergency Care",
            license_number="RN789012",
            hire_date=date(2021, 3, 1),
            salary=Decimal("75000.00"),
            shift_pattern="rotating",
            status="active"
        )
        
        staff_nurse_2 = Staff(
            user_id=nurse_user_2.id,
            employee_id="EMP004",
            department_id=icu_dept.id,
            position="ICU Nurse",
            specialization="Critical Care",
            license_number="RN345678",
            hire_date=date(2020, 6, 15),
            salary=Decimal("80000.00"),
            shift_pattern="night",
            status="active"
        )
        
        staff_manager = Staff(
            user_id=manager_user.id,
            employee_id="EMP005",
            department_id=cardiology_dept.id,
            position="Department Manager",
            hire_date=date(2018, 1, 1),
            salary=Decimal("95000.00"),
            shift_pattern="day",
            status="active"
        )
        
        staff_cleaner = Staff(
            user_id=cleaner_user.id,
            employee_id="EMP006",
            department_id=emergency_dept.id,
            position="Cleaning Staff",
            hire_date=date(2022, 1, 1),
            salary=Decimal("35000.00"),
            shift_pattern="day",
            status="active"
        )
        
        db.add_all([staff_doctor_1, staff_doctor_2, staff_nurse_1, staff_nurse_2, 
                   staff_manager, staff_cleaner])
        db.commit()
        db.refresh(staff_doctor_1)
        db.refresh(staff_doctor_2)
        db.refresh(staff_nurse_1)
        db.refresh(staff_nurse_2)
        
        # === STEP 4: Create Patients (No foreign key dependencies) ===
        print("4. Creating patients...")
        patient1 = Patient(
            patient_number="P001",
            first_name="Alice",
            last_name="Williams",
            date_of_birth=date(1985, 5, 15),
            gender="female",
            phone="555-2001",
            email="alice.williams@email.com",
            address="123 Main St, City, State",
            emergency_contact_name="Bob Williams",
            emergency_contact_phone="555-2002",
            blood_type="A+",
            allergies="Penicillin",
            medical_history="Hypertension"
        )
        
        patient2 = Patient(
            patient_number="P002",
            first_name="Robert",
            last_name="Brown",
            date_of_birth=date(1970, 8, 22),
            gender="male",
            phone="555-2003",
            email="robert.brown@email.com",
            address="456 Oak Ave, City, State",
            emergency_contact_name="Lisa Brown",
            emergency_contact_phone="555-2004",
            blood_type="O-",
            medical_history="Diabetes Type 2"
        )
        
        patient3 = Patient(
            patient_number="P003",
            first_name="Maria",
            last_name="Garcia",
            date_of_birth=date(1992, 12, 3),
            gender="female",
            phone="555-2005",
            email="maria.garcia@email.com",
            address="789 Pine St, City, State",
            emergency_contact_name="Jose Garcia",
            emergency_contact_phone="555-2006",
            blood_type="B+",
            allergies="Shellfish",
            medical_history="Asthma"
        )
        
        patient4 = Patient(
            patient_number="P004",
            first_name="David",
            last_name="Jones",
            date_of_birth=date(1965, 7, 10),
            gender="male",
            phone="555-2007",
            email="david.jones@email.com",
            address="321 Elm Ave, City, State",
            emergency_contact_name="Susan Jones",
            emergency_contact_phone="555-2008",
            blood_type="AB+",
            medical_history="Heart disease, Hypertension"
        )
        
        db.add_all([patient1, patient2, patient3, patient4])
        db.commit()
        db.refresh(patient1)
        db.refresh(patient2)
        db.refresh(patient3)
        db.refresh(patient4)
        
        # === STEP 5: Create Rooms (Depends on Departments) ===
        print("5. Creating rooms...")
        room301 = Room(
            room_number="301",
            department_id=cardiology_dept.id,
            room_type="private",
            floor_number=3,
            capacity=1
        )
        
        room302 = Room(
            room_number="302",
            department_id=cardiology_dept.id,
            room_type="semi-private",
            floor_number=3,
            capacity=2
        )
        
        room101 = Room(
            room_number="101",
            department_id=emergency_dept.id,
            room_type="emergency",
            floor_number=1,
            capacity=4
        )
        
        room401 = Room(
            room_number="401",
            department_id=icu_dept.id,
            room_type="icu",
            floor_number=4,
            capacity=1
        )
        
        room402 = Room(
            room_number="402",
            department_id=icu_dept.id,
            room_type="icu",
            floor_number=4,
            capacity=1
        )
        
        db.add_all([room301, room302, room101, room401, room402])
        db.commit()
        db.refresh(room301)
        db.refresh(room302)
        db.refresh(room101)
        db.refresh(room401)
        db.refresh(room402)
        
        # === STEP 6: Create Beds (Depends on Rooms and optionally Patients) ===
        print("6. Creating beds...")
        bed301a = Bed(
            bed_number="301A",
            room_id=room301.id,
            bed_type="standard",
            status="occupied",
            patient_id=patient1.id,
            admission_date=datetime.now() - timedelta(days=2)
        )
        
        bed302a = Bed(
            bed_number="302A",
            room_id=room302.id,
            bed_type="standard",
            status="available"
        )
        
        bed302b = Bed(
            bed_number="302B",
            room_id=room302.id,
            bed_type="standard",
            status="occupied",
            patient_id=patient2.id,
            admission_date=datetime.now() - timedelta(days=1)
        )
        
        bed101a = Bed(
            bed_number="101A",
            room_id=room101.id,
            bed_type="emergency",
            status="occupied",
            patient_id=patient3.id,
            admission_date=datetime.now() - timedelta(hours=6)
        )
        
        bed101b = Bed(
            bed_number="101B",
            room_id=room101.id,
            bed_type="emergency",
            status="available"
        )
        
        bed101c = Bed(
            bed_number="101C",
            room_id=room101.id,
            bed_type="emergency",
            status="maintenance"
        )
        
        bed101d = Bed(
            bed_number="101D",
            room_id=room101.id,
            bed_type="emergency",
            status="available"
        )
        
        bed401a = Bed(
            bed_number="401A",
            room_id=room401.id,
            bed_type="icu",
            status="occupied",
            patient_id=patient4.id,
            admission_date=datetime.now() - timedelta(days=5)
        )
        
        bed402a = Bed(
            bed_number="402A",
            room_id=room402.id,
            bed_type="icu",
            status="available"
        )
        
        db.add_all([bed301a, bed302a, bed302b, bed101a, bed101b, bed101c, bed101d, bed401a, bed402a])
        db.commit()
        db.refresh(bed301a)
        db.refresh(bed302a)
        db.refresh(bed302b)
        db.refresh(bed101a)
        db.refresh(bed401a)
        
        # === STEP 7: Create Equipment Categories (No dependencies) ===
        print("7. Creating equipment categories...")
        medical_devices = EquipmentCategory(
            name="Medical Devices",
            description="Various medical equipment and devices"
        )
        
        monitoring_equipment = EquipmentCategory(
            name="Monitoring Equipment",
            description="Patient monitoring systems"
        )
        
        surgical_equipment = EquipmentCategory(
            name="Surgical Equipment",
            description="Equipment for surgical procedures"
        )
        
        life_support = EquipmentCategory(
            name="Life Support",
            description="Life support and ventilation equipment"
        )
        
        db.add_all([medical_devices, monitoring_equipment, surgical_equipment, life_support])
        db.commit()
        db.refresh(medical_devices)
        db.refresh(monitoring_equipment)
        db.refresh(surgical_equipment)
        db.refresh(life_support)
        
        # === STEP 8: Create Equipment (Depends on Categories and Departments) ===
        print("8. Creating equipment...")
        ecg_machine = Equipment(
            equipment_id="EQ001",
            name="ECG Machine",
            category_id=monitoring_equipment.id,
            model="CardioMax 3000",
            manufacturer="MedTech Corp",
            serial_number="CM3000-001",
            purchase_date=date(2022, 6, 15),
            warranty_expiry=date(2025, 6, 15),
            location="Room 301",
            department_id=cardiology_dept.id,
            status="in_use",
            cost=Decimal("25000.00")
        )
        
        ventilator1 = Equipment(
            equipment_id="EQ002",
            name="Ventilator",
            category_id=life_support.id,
            model="BreathEasy Pro",
            manufacturer="LifeSupport Inc",
            serial_number="BEP-002",
            purchase_date=date(2023, 1, 10),
            warranty_expiry=date(2026, 1, 10),
            location="Room 401",
            department_id=icu_dept.id,
            status="in_use",
            cost=Decimal("45000.00")
        )
        
        ventilator2 = Equipment(
            equipment_id="EQ003",
            name="Ventilator",
            category_id=life_support.id,
            model="BreathEasy Pro",
            manufacturer="LifeSupport Inc",
            serial_number="BEP-003",
            purchase_date=date(2023, 1, 10),
            warranty_expiry=date(2026, 1, 10),
            location="Room 101",
            department_id=emergency_dept.id,
            status="available",
            cost=Decimal("45000.00")
        )
        
        defibrillator = Equipment(
            equipment_id="EQ004",
            name="Defibrillator",
            category_id=medical_devices.id,
            model="LifeSaver 2000",
            manufacturer="Emergency Corp",
            serial_number="LS2000-001",
            purchase_date=date(2021, 8, 20),
            warranty_expiry=date(2024, 8, 20),
            location="Emergency Department",
            department_id=emergency_dept.id,
            status="available",
            cost=Decimal("15000.00")
        )
        
        db.add_all([ecg_machine, ventilator1, ventilator2, defibrillator])
        db.commit()
        db.refresh(ecg_machine)
        db.refresh(ventilator1)
        db.refresh(ventilator2)
        db.refresh(defibrillator)
        
        # === STEP 9: Create Supply Categories (No dependencies) ===
        print("9. Creating supply categories...")
        medications = SupplyCategory(
            name="Medications",
            description="Pharmaceutical supplies"
        )
        
        medical_supplies = SupplyCategory(
            name="Medical Supplies",
            description="General medical supplies and consumables"
        )
        
        surgical_supplies = SupplyCategory(
            name="Surgical Supplies",
            description="Supplies for surgical procedures"
        )
        
        db.add_all([medications, medical_supplies, surgical_supplies])
        db.commit()
        db.refresh(medications)
        db.refresh(medical_supplies)
        db.refresh(surgical_supplies)
        
        # === STEP 10: Create Supplies (Depends on Categories) ===
        print("10. Creating supplies...")
        aspirin = Supply(
            item_code="MED001",
            name="Aspirin 81mg",
            category_id=medications.id,
            description="Low-dose aspirin tablets",
            unit_of_measure="tablets",
            minimum_stock_level=100,
            maximum_stock_level=1000,
            current_stock=500,
            unit_cost=Decimal("0.05"),
            supplier="PharmaCorp",
            expiry_date=date(2025, 12, 31),
            location="Pharmacy Storage"
        )
        
        syringes = Supply(
            item_code="SUP001",
            name="Disposable Syringes 10ml",
            category_id=medical_supplies.id,
            description="Sterile disposable syringes",
            unit_of_measure="pieces",
            minimum_stock_level=50,
            maximum_stock_level=500,
            current_stock=25,  # Low stock to test alerts
            unit_cost=Decimal("0.75"),
            supplier="MedSupply Co",
            location="Supply Room A"
        )
        
        gauze = Supply(
            item_code="SUP002",
            name="Sterile Gauze Pads",
            category_id=medical_supplies.id,
            description="4x4 inch sterile gauze pads",
            unit_of_measure="pieces",
            minimum_stock_level=200,
            maximum_stock_level=2000,
            current_stock=1500,
            unit_cost=Decimal("0.25"),
            supplier="MedSupply Co",
            location="Supply Room A"
        )
        
        morphine = Supply(
            item_code="MED002",
            name="Morphine 10mg/ml",
            category_id=medications.id,
            description="Morphine injection for pain management",
            unit_of_measure="vials",
            minimum_stock_level=10,
            maximum_stock_level=100,
            current_stock=45,
            unit_cost=Decimal("15.50"),
            supplier="PharmaCorp",
            expiry_date=date(2024, 12, 31),
            location="Controlled Substances Cabinet"
        )
        
        db.add_all([aspirin, syringes, gauze, morphine])
        db.commit()
        db.refresh(aspirin)
        db.refresh(syringes)
        db.refresh(gauze)
        db.refresh(morphine)
        
        # === STEP 11: Create Inventory Transactions (Depends on Supplies and Users) ===
        print("11. Creating inventory transactions...")
        transaction1 = InventoryTransaction(
            supply_id=aspirin.id,
            transaction_type="in",
            quantity=200,
            unit_cost=Decimal("0.05"),
            total_cost=Decimal("10.00"),
            reference_number="PO2024001",
            notes="Monthly restock",
            performed_by=admin_user.id
        )
        
        transaction2 = InventoryTransaction(
            supply_id=syringes.id,
            transaction_type="out",
            quantity=25,
            unit_cost=Decimal("0.75"),
            total_cost=Decimal("18.75"),
            reference_number="REQ2024001",
            notes="Emergency department usage",
            performed_by=nurse_user_1.id
        )
        
        transaction3 = InventoryTransaction(
            supply_id=morphine.id,
            transaction_type="in",
            quantity=20,
            unit_cost=Decimal("15.50"),
            total_cost=Decimal("310.00"),
            reference_number="PO2024002",
            notes="Controlled substance delivery",
            performed_by=admin_user.id
        )
        
        db.add_all([transaction1, transaction2, transaction3])
        db.commit()
        
        # === STEP 12: Create Meetings (Depends on Users and Departments) ===
        print("12. Creating meetings...")
        meeting1 = Meeting(
            title="Weekly Department Meeting",
            description="Weekly cardiology department meeting",
            meeting_datetime=datetime(2024, 8, 20, 15, 0),
            duration_minutes=60,
            location="Conference Room A",
            google_meet_link="https://meet.google.com/abc-defg-hij",
            organizer_id=manager_user.id,
            department_id=cardiology_dept.id,
            meeting_type="department",
            status="scheduled",
            priority="normal",
            agenda="Discuss patient cases and department updates"
        )
        
        meeting2 = Meeting(
            title="Emergency Protocol Review",
            description="Review of emergency protocols and procedures",
            meeting_datetime=datetime(2024, 8, 21, 11, 0),
            duration_minutes=90,
            location="Emergency Conference Room",
            google_meet_link="https://meet.google.com/xyz-uvwx-yzab",
            organizer_id=doctor_user_2.id,
            department_id=emergency_dept.id,
            meeting_type="training",
            status="scheduled",
            priority="high",
            agenda="Update on new emergency protocols"
        )
        
        db.add_all([meeting1, meeting2])
        db.commit()
        db.refresh(meeting1)
        db.refresh(meeting2)
        
        # === STEP 14: Create Meeting Participants (Depends on Meetings and Staff) ===
        print("14. Creating meeting participants...")
        participant1 = MeetingParticipant(
            meeting_id=meeting1.id,
            staff_id=staff_doctor_1.id,
            attendance_status="confirmed"
        )
        
        participant2 = MeetingParticipant(
            meeting_id=meeting1.id,
            staff_id=staff_manager.id,
            attendance_status="confirmed"
        )
        
        participant3 = MeetingParticipant(
            meeting_id=meeting2.id,
            staff_id=staff_doctor_2.id,
            attendance_status="confirmed"
        )
        
        participant4 = MeetingParticipant(
            meeting_id=meeting2.id,
            staff_id=staff_nurse_1.id,
            attendance_status="pending"
        )
        
        db.add_all([participant1, participant2, participant3, participant4])
        db.commit()
        
        # === STEP 15: Create Medical Documents (Depends on Patients) ===
        print("15. Creating medical documents...")
        doc1 = MedicalDocument(
            patient_id=patient1.id,
            document_type="prescription",
            file_name="prescription_001.pdf",
            file_path="/medical_docs/prescriptions/prescription_001.pdf",
            file_size=156789,
            mime_type="application/pdf",
            extracted_text="Patient: Alice Williams. Prescribed: Lisinopril 10mg daily for hypertension.",
            processing_status="completed",
            confidence_score=Decimal("0.95")
        )
        
        doc2 = MedicalDocument(
            patient_id=patient2.id,
            document_type="lab_result",
            file_name="glucose_test_002.pdf",
            file_path="/medical_docs/lab_results/glucose_test_002.pdf",
            file_size=89456,
            mime_type="application/pdf",
            extracted_text="Patient: Robert Brown. Glucose level: 145 mg/dL. Hemoglobin A1c: 7.2%",
            processing_status="completed",
            confidence_score=Decimal("0.92")
        )
        
        db.add_all([doc1, doc2])
        db.commit()
        db.refresh(doc1)
        db.refresh(doc2)
        
        # === STEP 16: Create Extracted Medical Data (Depends on Documents and Patients) ===
        print("16. Creating extracted medical data...")
        extracted_data1 = ExtractedMedicalData(
            document_id=doc1.id,
            patient_id=patient1.id,
            data_type="medication",
            entity_name="Lisinopril",
            entity_value="10",
            entity_unit="mg",
            date_prescribed=date.today(),
            doctor_name="Dr. Smith",
            hospital_name="General Hospital",
            department_name="Cardiology",
            extraction_confidence=Decimal("0.95"),
            extraction_method="AI_PARSING",
            verified=True
        )
        
        extracted_data2 = ExtractedMedicalData(
            document_id=doc2.id,
            patient_id=patient2.id,
            data_type="vital_sign",
            entity_name="Blood Glucose",
            entity_value="145",
            entity_unit="mg/dL",
            date_recorded=date.today(),
            doctor_name="Dr. Johnson",
            hospital_name="General Hospital",
            department_name="Emergency",
            extraction_confidence=Decimal("0.92"),
            extraction_method="AI_PARSING",
            verified=True
        )
        
        db.add_all([extracted_data1, extracted_data2])
        db.commit()
        
        # === STEP 17: Create Discharge Reports (Depends on Patients, Beds, Users) ===
        print("17. Creating discharge reports...")
        discharge_report1 = DischargeReport(
            patient_id=patient1.id,
            bed_id=bed301a.id,
            generated_by=doctor_user_1.id,
            report_number="DR-20240818-ABC12345",
            admission_date=datetime.now() - timedelta(days=3),
            discharge_date=datetime.now(),
            length_of_stay_days=3,
            patient_summary='{"age": 39, "gender": "female", "condition": "stable"}',
            treatment_summary='{"treatments": ["medication", "monitoring"]}',
            equipment_summary='{"equipment_used": ["ECG Machine"]}',
            staff_summary='{"primary_doctor": "Dr. Smith", "nurses": ["Nurse Brown"]}',
            medications='{"discharge_meds": ["Lisinopril 10mg daily"]}',
            procedures='{"procedures": ["ECG monitoring"]}',
            discharge_instructions="Continue medication as prescribed. Follow up in 2 weeks.",
            follow_up_required="Cardiology follow-up in 2 weeks",
            discharge_condition="stable",
            discharge_destination="home"
        )
        
        db.add(discharge_report1)
        db.commit()
        
        # === STEP 18: Create Patient Queue (Depends on Patients, Departments, Beds, Users) ===
        print("18. Creating patient queue...")
        queue_entry1 = PatientQueue(
            patient_id=patient3.id,
            department_id=icu_dept.id,
            queue_position=1,
            bed_type_required="icu",
            priority_level="high",
            admission_type="emergency",
            estimated_wait_time=30,
            target_bed_id=bed402a.id,
            medical_condition="Respiratory distress",
            special_requirements='{"ventilator": true, "isolation": false}',
            doctor_id=doctor_user_2.id,
            status="waiting"
        )
        
        db.add(queue_entry1)
        db.commit()
        
        # === STEP 19: Create Bed Turnover Records (Depends on Beds, Patients, Users) ===
        print("19. Creating bed turnover records...")
        bed_turnover1 = BedTurnover(
            bed_id=bed301a.id,
            previous_patient_id=patient1.id,
            status="cleaning",
            turnover_type="standard",
            discharge_time=datetime.now() - timedelta(hours=2),
            cleaning_start_time=datetime.now() - timedelta(hours=1),
            estimated_cleaning_duration=45,
            assigned_cleaner_id=cleaner_user.id,
            equipment_requiring_cleaning='["EQ001"]',
            cleaning_checklist='{"bed_sheets": false, "surfaces": false, "equipment": false}',
            priority_level="normal",
            notes="Standard cleaning after discharge"
        )
        
        db.add(bed_turnover1)
        db.commit()
        db.refresh(bed_turnover1)
        
        # === STEP 20: Create Equipment Turnover (Depends on Bed Turnover and Equipment) ===
        print("20. Creating equipment turnover...")
        equipment_turnover1 = EquipmentTurnover(
            bed_turnover_id=bed_turnover1.id,
            equipment_id=ecg_machine.id,
            status="needs_cleaning",
            cleaning_required=True,
            cleaning_type="surface",
            release_time=datetime.now() - timedelta(hours=2),
            released_by_staff_id=nurse_user_1.id,
            cleaning_checklist='{"surface_cleaning": false, "calibration": false}',
            notes="ECG machine needs cleaning after patient use"
        )
        
        db.add(equipment_turnover1)
        db.commit()
        
        # === STEP 21: Create Agent Interactions (Depends on Users) ===
        print("21. Creating agent interactions...")
        agent_log1 = AgentInteraction(
            agent_type="bed_management",
            user_id=nurse_user_1.id,
            query="Find available beds in emergency department",
            response="Found 2 available beds: 101B and 101D in Room 101",
            action_taken="bed_search",
            confidence_score=Decimal("0.95"),
            execution_time_ms=150
        )
        
        agent_log2 = AgentInteraction(
            agent_type="equipment_tracker",
            user_id=doctor_user_1.id,
            query="Check status of ECG machine EQ001",
            response="ECG Machine EQ001 is currently in use in Room 301",
            action_taken="equipment_status_check",
            confidence_score=Decimal("0.98"),
            execution_time_ms=75
        )
        
        agent_log3 = AgentInteraction(
            agent_type="supply_inventory",
            user_id=nurse_user_2.id,
            query="Check morphine stock levels",
            response="Morphine 10mg/ml: 45 vials available (Normal stock level)",
            action_taken="inventory_check",
            confidence_score=Decimal("0.99"),
            execution_time_ms=120
        )
        
        db.add_all([agent_log1, agent_log2, agent_log3])
        db.commit()
        
        # === STEP 22: Create Legacy Users (For backward compatibility) ===
        print("22. Creating legacy users...")
        legacy_user1 = LegacyUser(
            name="John Legacy",
            email="john.legacy@hospital.com",
            address="123 Legacy Street",
            phone="555-9001"
        )
        
        legacy_user2 = LegacyUser(
            name="Jane Legacy",
            email="jane.legacy@hospital.com",
            address="456 Legacy Avenue",
            phone="555-9002"
        )
        
        db.add_all([legacy_user1, legacy_user2])
        db.commit()
        
        print("✅ Comprehensive sample data created successfully!")
        
        # Print detailed summary
        print("\n📊 Database Summary:")
        print(f"Users: {db.query(User).count()}")
        print(f"Departments: {db.query(Department).count()}")
        print(f"Staff: {db.query(Staff).count()}")
        print(f"Patients: {db.query(Patient).count()}")
        print(f"Rooms: {db.query(Room).count()}")
        print(f"Beds: {db.query(Bed).count()}")
        print(f"Equipment Categories: {db.query(EquipmentCategory).count()}")
        print(f"Equipment: {db.query(Equipment).count()}")
        print(f"Supply Categories: {db.query(SupplyCategory).count()}")
        print(f"Supplies: {db.query(Supply).count()}")
        print(f"Inventory Transactions: {db.query(InventoryTransaction).count()}")
        print(f"Meetings: {db.query(Meeting).count()}")
        print(f"Meeting Participants: {db.query(MeetingParticipant).count()}")
        print(f"Medical Documents: {db.query(MedicalDocument).count()}")
        print(f"Extracted Medical Data: {db.query(ExtractedMedicalData).count()}")
        print(f"Discharge Reports: {db.query(DischargeReport).count()}")
        print(f"Patient Queue: {db.query(PatientQueue).count()}")
        print(f"Bed Turnovers: {db.query(BedTurnover).count()}")
        print(f"Equipment Turnovers: {db.query(EquipmentTurnover).count()}")
        print(f"Agent Interactions: {db.query(AgentInteraction).count()}")
        print(f"Legacy Users: {db.query(LegacyUser).count()}")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function to test database setup."""
    print("🏥 Hospital Management System Database Setup")
    print("=" * 50)
    
    # Test connection
    print("1. Testing database connection...")
    if not test_connection():
        print("❌ Database connection failed. Please check your PostgreSQL setup.")
        return
    
    # Create tables
    print("2. Creating database tables...")
    print("⚠️  This will drop and recreate all tables!")
    
    try:
        create_tables()
        print("✅ Tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        print("\n💡 Troubleshooting tips:")
        print("- Make sure PostgreSQL is running")
        print("- Check your DATABASE_URL in .env file")
        print("- Ensure the database 'hospital_management' exists")
        print("- Try creating the database: createdb hospital_management")
        return
    
    # Create sample data
    print("3. Creating sample data...")
    try:
        create_sample_data()
        print("✅ Sample data created successfully!")
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        print("⚠️  Continuing without sample data...")
    
    print("\n🎉 Database setup completed successfully!")
    print("\nYou can now:")
    print("- Run the comprehensive_server.py for full CRUD operations")
    print("- Use the MCP tools to interact with all database tables")
    print("- Test the AI agents with the sample data")

if __name__ == "__main__":
    main()
