"""Database configuration and connection management for PostgreSQL."""

import os
from typing import List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Sequence
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hospital_management")

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    """User table model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)

def create_tables():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def migrate_json_to_db():
    """Migrate existing users.json data to PostgreSQL database."""
    from pathlib import Path
    
    # Read existing JSON data
    json_file = Path(__file__).parent / "data" / "users.json"
    if not json_file.exists():
        print("No users.json file found to migrate")
        return
    
    with open(json_file, 'r') as f:
        users_data = json.load(f)
    
    # Create database session
    db = SessionLocal()
    try:
        # Check if users already exist
        existing_count = db.query(User).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} users. Skipping migration.")
            return
        
        # Insert users into database
        for user_data in users_data:
            # Don't set the ID, let PostgreSQL auto-generate it
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                address=user_data["address"],
                phone=user_data["phone"]
            )
            db.add(user)
        
        db.commit()
        print(f"Successfully migrated {len(users_data)} users to PostgreSQL database")
        
    except Exception as e:
        db.rollback()
        print(f"Error migrating data: {e}")
    finally:
        db.close()

def test_connection():
    """Test database connection."""
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1"))
        db.close()
        print("✅ PostgreSQL connection successful!")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

if __name__ == "__main__":
    # Test connection and create tables
    print("Testing PostgreSQL connection...")
    if test_connection():
        print("Creating tables...")
        create_tables()
        print("Migrating data from JSON...")
        migrate_json_to_db()
        print("Database setup complete!")
