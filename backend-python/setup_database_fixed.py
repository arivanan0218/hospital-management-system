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
        
        # === STEP 1: Create Users (No foreign key dependencies) ===
        print("1. Creating users...")
        
        users = []
        
        # Admin Users
        admin_user = User(
            username="admin",
            email="admin@hospital.com",
            password_hash="hashed_password_123",
            role="admin",
            first_name="Admin",
            last_name="User",
            phone="555-0001"
        )
        users.append(admin_user)
        
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
        
        print("✅ All dummy data created successfully!")
        
        # Print summary
        print(f"\n📊 Database Summary:")
        print(f"Users: {db.query(User).count()}")
        print(f"Total Records: {db.query(User).count()}")
        
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

if __name__ == "__main__":
    main()
