"""Test script to verify database setup and create sample data."""

import sys
import os
import uuid
from datetime import datetime, date
from decimal import Decimal

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import (
    test_connection, create_tables, SessionLocal,
    User, Department, Patient, Room, Bed, Staff, Equipment, EquipmentCategory,
    Supply, SupplyCategory, InventoryTransaction, AgentInteraction, Appointment
)

def create_sample_data():
    """Create sample data for testing."""
    db = SessionLocal()
    
    try:
        print("Creating sample data...")
        
        # Create sample users
        admin_user = User(
            username="admin",
            email="admin@hospital.com",
            password_hash="hashed_password_123",
            role="admin",
            first_name="Admin",
            last_name="User",
            phone="555-0001"
        )
        
        doctor_user = User(
            username="dr.smith",
            email="dr.smith@hospital.com",
            password_hash="hashed_password_456",
            role="doctor",
            first_name="John",
            last_name="Smith",
            phone="555-0002"
        )
        
        nurse_user = User(
            username="nurse.johnson",
            email="nurse.johnson@hospital.com",
            password_hash="hashed_password_789",
            role="nurse",
            first_name="Mary",
            last_name="Johnson",
            phone="555-0003"
        )
        
        db.add_all([admin_user, doctor_user, nurse_user])
        db.commit()
        db.refresh(admin_user)
        db.refresh(doctor_user)
        db.refresh(nurse_user)
        
        # Create sample departments
        cardiology_dept = Department(
            name="Cardiology",
            description="Heart and cardiovascular care",
            head_doctor_id=doctor_user.id,
            floor_number=3,
            phone="555-1001",
            email="cardiology@hospital.com"
        )
        
        emergency_dept = Department(
            name="Emergency",
            description="Emergency medical care",
            floor_number=1,
            phone="555-1002",
            email="emergency@hospital.com"
        )
        
        db.add_all([cardiology_dept, emergency_dept])
        db.commit()
        db.refresh(cardiology_dept)
        db.refresh(emergency_dept)
        
        # Create sample patients
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
        
        db.add_all([patient1, patient2])
        db.commit()
        db.refresh(patient1)
        db.refresh(patient2)
        
        # Create sample rooms
        room301 = Room(
            room_number="301",
            department_id=cardiology_dept.id,
            room_type="private",
            floor_number=3,
            capacity=1
        )
        
        room101 = Room(
            room_number="101",
            department_id=emergency_dept.id,
            room_type="emergency",
            floor_number=1,
            capacity=2
        )
        
        db.add_all([room301, room101])
        db.commit()
        db.refresh(room301)
        db.refresh(room101)
        
        # Create sample beds
        bed301a = Bed(
            bed_number="301A",
            room_id=room301.id,
            bed_type="standard",
            status="available"
        )
        
        bed101a = Bed(
            bed_number="101A",
            room_id=room101.id,
            bed_type="icu",
            status="occupied",
            patient_id=patient1.id,
            admission_date=datetime.now()
        )
        
        bed101b = Bed(
            bed_number="101B",
            room_id=room101.id,
            bed_type="icu",
            status="available"
        )
        
        db.add_all([bed301a, bed101a, bed101b])
        db.commit()
        
        # Create sample staff
        staff_doctor = Staff(
            user_id=doctor_user.id,
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
        
        staff_nurse = Staff(
            user_id=nurse_user.id,
            employee_id="EMP002",
            department_id=emergency_dept.id,
            position="Registered Nurse",
            specialization="Emergency Care",
            license_number="RN789012",
            hire_date=date(2021, 3, 1),
            salary=Decimal("75000.00"),
            shift_pattern="rotating",
            status="active"
        )
        
        db.add_all([staff_doctor, staff_nurse])
        db.commit()
        
        # Create sample equipment categories
        medical_devices = EquipmentCategory(
            name="Medical Devices",
            description="Various medical equipment and devices"
        )
        
        monitoring_equipment = EquipmentCategory(
            name="Monitoring Equipment",
            description="Patient monitoring systems"
        )
        
        db.add_all([medical_devices, monitoring_equipment])
        db.commit()
        db.refresh(medical_devices)
        db.refresh(monitoring_equipment)
        
        # Create sample equipment
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
            status="available",
            cost=Decimal("25000.00")
        )
        
        ventilator = Equipment(
            equipment_id="EQ002",
            name="Ventilator",
            category_id=medical_devices.id,
            model="BreathEasy Pro",
            manufacturer="LifeSupport Inc",
            serial_number="BEP-002",
            purchase_date=date(2023, 1, 10),
            warranty_expiry=date(2026, 1, 10),
            location="Room 101",
            department_id=emergency_dept.id,
            status="in_use",
            cost=Decimal("45000.00")
        )
        
        db.add_all([ecg_machine, ventilator])
        db.commit()
        
        # Create sample supply categories
        medications = SupplyCategory(
            name="Medications",
            description="Pharmaceutical supplies"
        )
        
        medical_supplies = SupplyCategory(
            name="Medical Supplies",
            description="General medical supplies and consumables"
        )
        
        db.add_all([medications, medical_supplies])
        db.commit()
        db.refresh(medications)
        db.refresh(medical_supplies)
        
        # Create sample supplies
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
        
        db.add_all([aspirin, syringes])
        db.commit()
        db.refresh(aspirin)
        db.refresh(syringes)
        
        # Create sample inventory transaction
        transaction = InventoryTransaction(
            supply_id=aspirin.id,
            transaction_type="in",
            quantity=200,
            unit_cost=Decimal("0.05"),
            total_cost=Decimal("10.00"),
            reference_number="PO2024001",
            notes="Monthly restock",
            performed_by=admin_user.id
        )
        
        db.add(transaction)
        db.commit()
        
        # Create sample appointment
        appointment = Appointment(
            patient_id=patient1.id,
            doctor_id=doctor_user.id,
            department_id=cardiology_dept.id,
            appointment_date=datetime(2024, 8, 15, 10, 30),
            duration_minutes=45,
            reason="Cardiac consultation",
            notes="Follow-up for hypertension management"
        )
        
        db.add(appointment)
        db.commit()
        
        # Create sample agent interaction
        agent_log = AgentInteraction(
            agent_type="bed_management",
            user_id=nurse_user.id,
            query="Find available beds in emergency department",
            response="Found 1 available bed: 101B in Room 101",
            action_taken="bed_search",
            confidence_score=Decimal("0.95"),
            execution_time_ms=150
        )
        
        db.add(agent_log)
        db.commit()
        
        print("✅ Sample data created successfully!")
        
        # Print summary
        print("\n📊 Database Summary:")
        print(f"Users: {db.query(User).count()}")
        print(f"Departments: {db.query(Department).count()}")
        print(f"Patients: {db.query(Patient).count()}")
        print(f"Rooms: {db.query(Room).count()}")
        print(f"Beds: {db.query(Bed).count()}")
        print(f"Staff: {db.query(Staff).count()}")
        print(f"Equipment Categories: {db.query(EquipmentCategory).count()}")
        print(f"Equipment: {db.query(Equipment).count()}")
        print(f"Supply Categories: {db.query(SupplyCategory).count()}")
        print(f"Supplies: {db.query(Supply).count()}")
        print(f"Inventory Transactions: {db.query(InventoryTransaction).count()}")
        print(f"Appointments: {db.query(Appointment).count()}")
        print(f"Agent Interactions: {db.query(AgentInteraction).count()}")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
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
    print("3. Sample data creation is disabled. Only tables are created.")
    
    print("\n🎉 Database setup completed successfully!")
    print("\nYou can now:")
    print("- Run the comprehensive_server.py for full CRUD operations")
    print("- Use the MCP tools to interact with all database tables")
    print("- Test the AI agents with the sample data")

if __name__ == "__main__":
    main()
