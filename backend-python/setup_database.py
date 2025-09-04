"""Test script to verify database setup and create sample data."""

import sys
import os
import uuid
import random
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
    StaffMeeting, TreatmentRecord, PatientSupplyUsage
)

def create_sample_data():
    """Create comprehensive sample data for testing with proper foreign key relationships."""
    db = SessionLocal()
    
    try:
        print("Creating comprehensive sample data...")
        
        print("1. Creating users...")
        users = []
        
        # Create 30 diverse users with different roles
        roles = ["doctor", "nurse", "admin", "manager", "receptionist", "support_staff"]
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa", 
                      "William", "Jessica", "James", "Ashley", "Christopher", "Amanda", "Daniel",
                      "Stephanie", "Matthew", "Jennifer", "Anthony", "Elizabeth", "Mark", "Deborah",
                      "Donald", "Rachel", "Steven", "Carolyn", "Paul", "Janet", "Andrew", "Maria"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                     "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
                     "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
                     "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"]
        
        for i in range(30):
            role = random.choice(roles)
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            user = User(
                username=f"{first_name.lower()}.{last_name.lower()}{i}",
                email=f"{first_name.lower()}.{last_name.lower()}{i}@hospital.com",
                password_hash=f"hashed_password_{100+i}",
                role=role,
                first_name=first_name,
                last_name=last_name,
                phone=f"555-{1000+i:04d}"
            )
            users.append(user)
        
        db.add_all(users)
        db.commit()
        
        print("2. Creating departments...")
        departments = []
        
        dept_data = [
            ("Emergency Medicine", "Emergency and trauma care"),
            ("Internal Medicine", "General internal medicine and primary care"),
            ("Cardiology", "Heart and cardiovascular care"),
            ("Neurology", "Brain and nervous system care"),
            ("Orthopedics", "Bone and joint care"),
            ("Pediatrics", "Children's healthcare"),
            ("Oncology", "Cancer treatment and care"),
            ("Radiology", "Imaging and diagnostic services"),
            ("Surgery", "Surgical procedures and care"),
            ("ICU", "Intensive care unit"),
            ("Pharmacy", "Medication management"),
            ("Administration", "Hospital administration")
        ]
        
        for i, (name, description) in enumerate(dept_data):
            dept = Department(
                name=name,
                description=description,
                head_doctor_id=random.choice(users).id,
                floor_number=random.randint(1, 5),
                phone=f"555-{2000+i:04d}",
                email=f"{name.lower().replace(' ', '.')}@hospital.com"
            )
            departments.append(dept)
        
        db.add_all(departments)
        db.commit()
        
        print("3. Creating staff...")
        staff = []
        
        specializations = [
            "Emergency Medicine", "Internal Medicine", "Cardiology", "Neurology",
            "Orthopedics", "Pediatrics", "Oncology", "Radiology", "Surgery",
            "Nursing", "Administration", "Pharmacy"
        ]
        
        positions = ["Doctor", "Nurse", "Manager", "Technician", "Administrator"]
        
        for i, user in enumerate(users):
            if user.role in ["doctor", "nurse", "manager"]:
                staff_member = Staff(
                    user_id=user.id,
                    employee_id=f"EMP{1000+i:04d}",
                    department_id=random.choice(departments).id,
                    position=random.choice(positions),
                    specialization=random.choice(specializations),
                    license_number=f"LIC{random.randint(10000, 99999)}",
                    hire_date=date.today() - timedelta(days=random.randint(30, 3650)),
                    status="active",
                    shift_pattern=random.choice(["day", "night", "rotating"]),
                    salary=Decimal(f"{random.randint(50000, 200000)}.00")
                )
                staff.append(staff_member)
        
        db.add_all(staff)
        db.commit()
        
        print("4. Creating patients...")
        patients = []
        
        blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        
        for i in range(25):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            patient = Patient(
                patient_number=f"P{1000+i:04d}",
                first_name=first_name,
                last_name=last_name,
                date_of_birth=date.today() - timedelta(days=random.randint(365, 30000)),
                gender=random.choice(["M", "F"]),
                phone=f"555-2{i:03d}",
                email=f"{first_name.lower()}.{last_name.lower()}.patient{i}@email.com",
                address=f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'First', 'Second'])} St",
                emergency_contact_name=f"Emergency Contact {i}",
                emergency_contact_phone=f"555-3{i:03d}",
                blood_type=random.choice(blood_types),
                allergies=random.choice(["None", "Penicillin", "Shellfish", "Latex", "Peanuts"]),
                medical_history=f"Patient {i} medical history: {random.choice(['diabetes', 'hypertension', 'asthma', 'none significant'])}",
                status="active"
            )
            patients.append(patient)
        
        db.add_all(patients)
        db.commit()
        
        print("5. Creating rooms...")
        rooms = []
        
        # Create diverse room types across multiple floors
        room_types = ["ICU", "General", "Private", "Emergency", "Surgery", "Recovery"]
        
        for floor in range(1, 6):  # 5 floors
            for room_num in range(1, 21):  # 20 rooms per floor
                room_number = f"{floor}{room_num:02d}"
                
                room = Room(
                    room_number=room_number,
                    room_type=random.choice(room_types),
                    department_id=random.choice(departments).id,
                    capacity=random.randint(1, 4),
                    floor_number=floor,
                    status=random.choice(["available", "occupied", "maintenance", "cleaning"])
                )
                rooms.append(room)
        
        db.add_all(rooms)
        db.commit()
        
        print("6. Creating beds...")
        beds = []
        
        # Create 1-3 beds per room based on capacity
        for room in rooms:
            for bed_num in range(room.capacity):
                bed_letter = chr(65 + bed_num)  # A, B, C, D
                bed_number = f"{room.room_number}{bed_letter}"
                
                # Assign some beds to patients
                patient_id = None
                bed_status = "available"
                if random.random() < 0.7 and patients:  # 70% occupancy rate
                    patient_id = random.choice(patients).id
                    bed_status = "occupied"
                
                bed = Bed(
                    bed_number=bed_number,
                    room_id=room.id,
                    patient_id=patient_id,
                    bed_type=random.choice(["standard", "ICU", "pediatric", "bariatric"]),
                    status=bed_status
                )
                beds.append(bed)
        
        db.add_all(beds)
        db.commit()
        
        print("7. Creating equipment categories...")
        equipment_categories = [
            ("Monitoring Equipment", "Patient monitoring and vital signs equipment"),
            ("Life Support", "Life support and respiratory equipment"),
            ("Surgical Equipment", "Surgical tools and operating room equipment"),
            ("Diagnostic Equipment", "Imaging and diagnostic tools"),
            ("Transport Equipment", "Patient transport and mobility aids"),
            ("Laboratory Equipment", "Lab testing and analysis equipment"),
            ("Emergency Equipment", "Emergency response and trauma equipment"),
            ("Rehabilitation Equipment", "Physical therapy and rehabilitation tools"),
            ("Sterilization Equipment", "Cleaning and sterilization equipment"),
            ("Communication Equipment", "Communication and information systems")
        ]
        
        eq_categories = []
        for name, description in equipment_categories:
            category = EquipmentCategory(
                name=name,
                description=description
            )
            eq_categories.append(category)
        
        db.add_all(eq_categories)
        db.commit()
        
        print("8. Creating equipment...")
        equipment = []
        
        # Equipment by category
        equipment_data = {
            "Monitoring Equipment": [
                ("ECG Monitor", "Electrocardiogram monitoring device"),
                ("Pulse Oximeter", "Blood oxygen saturation monitor"),
                ("Blood Pressure Monitor", "Automated blood pressure measurement"),
                ("Heart Rate Monitor", "Continuous heart rate monitoring"),
                ("Temperature Monitor", "Digital temperature measurement"),
                ("Multi-Parameter Monitor", "Comprehensive vital signs monitoring"),
                ("Cardiac Monitor", "Advanced cardiac rhythm monitoring"),
                ("Fetal Monitor", "Fetal heart rate and contraction monitoring"),
                ("Sleep Monitor", "Sleep study monitoring equipment"),
                ("Telemetry Monitor", "Wireless patient monitoring")
            ],
            "Life Support": [
                ("Ventilator", "Mechanical breathing assistance"),
                ("CPAP Machine", "Continuous positive airway pressure"),
                ("BiPAP Machine", "Bilevel positive airway pressure"),
                ("Oxygen Concentrator", "Oxygen therapy equipment"),
                ("Nebulizer", "Medication delivery via inhalation"),
                ("Suction Machine", "Airway clearance equipment"),
                ("Defibrillator", "Emergency cardiac resuscitation"),
                ("Infusion Pump", "Intravenous medication delivery"),
                ("Feeding Pump", "Enteral nutrition delivery"),
                ("Dialysis Machine", "Kidney function replacement")
            ]
        }
        
        # Create equipment for each category with sequential IDs
        equipment_counter = 1
        for category_name, items in equipment_data.items():
            category = next(c for c in eq_categories if c.name == category_name)
            
            for item_name, description in items:
                for i in range(random.randint(8, 15)):  # 8-15 of each type
                    equipment_item = Equipment(
                        equipment_id=f"EQ{equipment_counter:05d}",
                        name=f"{item_name} {i+1:03d}",
                        serial_number=f"SN{random.randint(100000, 999999)}",
                        model=f"Model-{random.randint(1000, 9999)}",
                        manufacturer=random.choice(["Philips", "GE Healthcare", "Siemens", "Medtronic", "Abbott"]),
                        category_id=category.id,
                        location=f"Room {random.choice(rooms).room_number}",
                        department_id=random.choice(departments).id,
                        status=random.choice(["available", "in_use", "maintenance", "out_of_order"]),
                        purchase_date=date.today() - timedelta(days=random.randint(1, 3650)),
                        cost=Decimal(f"{random.randint(5000, 100000)}.00"),
                        warranty_expiry=date.today() + timedelta(days=random.randint(30, 3650)),
                        last_maintenance=date.today() - timedelta(days=random.randint(1, 365))
                    )
                    equipment.append(equipment_item)
                    equipment_counter += 1
        
        db.add_all(equipment)
        db.commit()
        
        print("9. Creating supply categories...")
        supply_categories_data = [
            ("Medications", "Pharmaceuticals and medical drugs"),
            ("Surgical Supplies", "Items used in surgical procedures"),
            ("Wound Care", "Supplies for wound treatment and dressing"),
            ("IV and Injection", "Intravenous and injection related supplies"),
            ("Diagnostic Supplies", "Items for patient diagnosis and testing"),
            ("Personal Protective Equipment", "Safety equipment for staff and patients"),
            ("Patient Care", "General patient care and comfort items"),
            ("Laboratory Supplies", "Lab testing and analysis materials"),
            ("Emergency Supplies", "Emergency response and trauma care items"),
            ("Rehabilitation", "Physical therapy and recovery supplies"),
            ("Nutrition", "Dietary and nutritional supplements"),
            ("Sterilization", "Cleaning and sterilization materials"),
            ("Respiratory Care", "Breathing and oxygen therapy supplies"),
            ("Cardiac Care", "Heart and cardiovascular care supplies"),
            ("Pediatric Care", "Children's healthcare specific supplies")
        ]
        
        supply_categories = []
        for name, description in supply_categories_data:
            category = SupplyCategory(
                name=name,
                description=description
            )
            supply_categories.append(category)
        
        db.add_all(supply_categories)
        db.commit()
        
        print("10. Creating supplies...")
        supplies_by_category = {
            "Medications": [
                ("Acetaminophen 500mg", "Pain reliever and fever reducer", "tablet"),
                ("Ibuprofen 200mg", "Anti-inflammatory pain reliever", "tablet"),
                ("Morphine 10mg/ml", "Strong pain medication", "ml"),
                ("Insulin (Regular)", "Diabetes medication", "unit"),
                ("Epinephrine 1mg/ml", "Emergency allergy/cardiac medication", "ml"),
                ("Amoxicillin 500mg", "Antibiotic medication", "tablet"),
                ("Lisinopril 10mg", "Blood pressure medication", "tablet"),
                ("Albuterol Inhaler", "Respiratory bronchodilator", "inhaler"),
                ("Normal Saline 0.9%", "IV fluid solution", "ml"),
                ("Heparin 5000u/ml", "Blood thinner injection", "ml")
            ],
            "Surgical Supplies": [
                ("Surgical Gloves (Size 7)", "Sterile latex surgical gloves", "pair"),
                ("Surgical Mask", "Disposable surgical face mask", "piece"),
                ("Surgical Gown", "Sterile surgical protection gown", "piece"),
                ("Scalpel Blade #15", "Disposable surgical blade", "piece"),
                ("Surgical Suture 3-0", "Non-absorbable suture material", "piece"),
                ("Surgical Staples", "Wound closure staples", "piece"),
                ("Surgical Sponges", "Absorbent surgical sponges", "piece"),
                ("Endotracheal Tube 7.0", "Airway intubation tube", "piece"),
                ("Trocar 5mm", "Laparoscopic port", "piece"),
                ("Hemostatic Agent", "Bleeding control powder", "g")
            ],
            "Wound Care": [
                ("Gauze Pads 4x4", "Sterile wound dressing pads", "piece"),
                ("Medical Tape 1 inch", "Adhesive medical tape", "roll"),
                ("Transparent Dressing", "Clear adhesive wound cover", "piece"),
                ("Antibiotic Ointment", "Topical infection prevention", "g"),
                ("Betadine Solution", "Antiseptic wound cleaner", "ml"),
                ("Alcohol Prep Pads", "Skin preparation wipes", "piece"),
                ("Elastic Bandage 4 inch", "Compression support bandage", "roll"),
                ("Pressure Bandage", "Emergency bleeding control", "piece"),
                ("Hydrocolloid Dressing", "Advanced wound healing dressing", "piece"),
                ("Silver Sulfadiazine Cream", "Antimicrobial wound cream", "g")
            ],
            "IV and Injection": [
                ("IV Catheter 18G", "Large bore IV catheter", "piece"),
                ("IV Catheter 20G", "Medium bore IV catheter", "piece"),
                ("Syringe 5ml", "Standard injection syringe", "piece"),
                ("Needle 23G 1 inch", "Standard injection needle", "piece"),
                ("IV Bag 500ml Normal Saline", "IV fluid bag", "bag"),
                ("Blood Collection Tube", "Vacuum blood draw tube", "piece"),
                ("Butterfly Needle 23G", "Winged blood collection needle", "piece"),
                ("IV Tubing Set", "Standard IV administration set", "piece"),
                ("Tourniquet", "Blood draw compression band", "piece"),
                ("IV Site Dressing", "Catheter site protection", "piece")
            ],
            "Personal Protective Equipment": [
                ("N95 Respirator Mask", "High filtration respiratory protection", "piece"),
                ("Nitrile Gloves Medium", "Powder-free examination gloves", "piece"),
                ("Face Shield", "Full face protection shield", "piece"),
                ("Isolation Gown", "Protective clothing garment", "piece"),
                ("Hand Sanitizer 500ml", "Alcohol-based hand disinfectant", "bottle"),
                ("Disinfectant Wipes", "Surface cleaning wipes", "piece"),
                ("Biohazard Bag", "Infectious waste disposal bag", "piece"),
                ("Sharps Container", "Needle disposal container", "piece"),
                ("Safety Goggles", "Eye protection glasses", "piece"),
                ("Shoe Covers", "Disposable foot protection", "pair")
            ]
        }
        
        supplies = []
        supply_counter = 1
        
        for category_name, supply_items in supplies_by_category.items():
            # Find the category
            category = next(c for c in supply_categories if c.name == category_name)
            
            for name, description, unit in supply_items:
                supply = Supply(
                    item_code=f"SUP{supply_counter:05d}",
                    name=name,
                    category_id=category.id,
                    description=description,
                    unit_of_measure=unit,
                    minimum_stock_level=random.randint(10, 50),
                    maximum_stock_level=random.randint(100, 500),
                    current_stock=random.randint(25, 200),
                    unit_cost=Decimal(f"{random.uniform(0.5, 50.0):.2f}"),
                    supplier=random.choice([
                        "MedSupply Corp", "Healthcare Solutions", "Medical Distributors Inc",
                        "Premier Medical", "Cardinal Health"
                    ]),
                    expiry_date=date.today() + timedelta(days=random.randint(180, 1095)),
                    location=random.choice([
                        "Pharmacy", "Supply Room A", "Central Storage", "Emergency Stock"
                    ])
                )
                supplies.append(supply)
                supply_counter += 1
        
        db.add_all(supplies)
        db.commit()
        
        print("✅ Sample data created successfully!")
        
        # Print summary
        print(f"\n📊 Database Summary:")
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
        
        print(f"\n📈 Data Statistics:")
        total_records = sum([
            db.query(User).count(), db.query(Department).count(), db.query(Staff).count(),
            db.query(Patient).count(), db.query(Room).count(), db.query(Bed).count(),
            db.query(Equipment).count(), db.query(Supply).count(), db.query(SupplyCategory).count()
        ])
        print(f"Total Records Created: {total_records}")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        import traceback
        traceback.print_exc()
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
        return
    
    # Create sample data
    print("3. Creating sample data...")
    try:
        create_sample_data()
        print("✅ Sample data created successfully!")
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
    
    print("\n🎉 Database setup completed successfully!")

if __name__ == "__main__":
    main()
