#!/usr/bin/env python3
"""
Initialize database schema for hospital management system
"""
import os
import sys
import time

def initialize_database():
    """Initialize database with required tables"""
    try:
        print("🔧 Initializing database schema...")
        
        # Import our database module
        from database import engine, Base
        from database import (
            User, Department, Patient, Room, Bed, Staff, Equipment, 
            EquipmentCategory, Supply, SupplyCategory, InventoryTransaction, 
            AgentInteraction, Appointment, LegacyUser
        )
        
        # Create all tables
        print("📋 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Test connection
        from database import SessionLocal
        session = SessionLocal()
        
        # Check if we have any users
        from sqlalchemy import text
        result = session.execute(text("SELECT COUNT(*) FROM users")).fetchone()
        user_count = result[0] if result else 0
        print(f"📊 Current user count: {user_count}")
        
        # If no users, create a default admin user
        if user_count == 0:
            print("👤 Creating default admin user...")
            admin_user = User(
                username="admin",
                email="admin@hospital.com",
                password_hash="hashed_password_here",  # In real app, use proper hashing
                role="admin",
                first_name="System",
                last_name="Administrator"
            )
            session.add(admin_user)
            session.commit()
            print("✅ Default admin user created")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🗄️ Database Initialization")
    print("=" * 50)
    
    if initialize_database():
        print("🎉 Database initialized successfully!")
        sys.exit(0)
    else:
        print("❌ Database initialization failed")
        sys.exit(1)
