"""Database configuration and connection management for PostgreSQL."""

import os
import uuid
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, Date, Boolean, Text, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.sql import func
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

# --- New imports for meeting & legacy models registration ---
# Note: Meeting models will be imported when needed to avoid circular imports

# Database Models

class User(Base):
    """User table model for authentication and basic user info."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # admin, doctor, nurse, manager, receptionist
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    staff = relationship("Staff", back_populates="user", uselist=False)
    appointments_as_doctor = relationship("Appointment", foreign_keys="Appointment.doctor_id", back_populates="doctor")
    inventory_transactions = relationship("InventoryTransaction", back_populates="performed_by_user")
    agent_interactions = relationship("AgentInteraction", back_populates="user")
    discharge_reports = relationship("DischargeReport", foreign_keys="DischargeReport.doctor_id", back_populates="doctor")

class Department(Base):
    """Department table model."""
    __tablename__ = "departments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    head_doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    floor_number = Column(Integer)
    phone = Column(String(20))
    email = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    head_doctor = relationship("User", foreign_keys=[head_doctor_id])
    staff = relationship("Staff", back_populates="department")
    rooms = relationship("Room", back_populates="department")
    equipment = relationship("Equipment", back_populates="department")
    appointments = relationship("Appointment", back_populates="department")
    discharge_reports = relationship("DischargeReport", back_populates="department")

class Patient(Base):
    """Patient table model."""
    __tablename__ = "patients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_number = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10))  # male, female, other
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    emergency_contact_name = Column(String(100))
    emergency_contact_phone = Column(String(20))
    blood_type = Column(String(5))
    allergies = Column(Text)
    medical_history = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    beds = relationship("Bed", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")
    medical_documents = relationship("MedicalDocument", back_populates="patient")
    extracted_medical_data = relationship("ExtractedMedicalData", back_populates="patient")
    discharge_reports = relationship("DischargeReport", back_populates="patient")

class Room(Base):
    """Room table model."""
    __tablename__ = "rooms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_number = Column(String(10), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    room_type = Column(String(20))  # general, private, icu, emergency, operation
    floor_number = Column(Integer)
    capacity = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    department = relationship("Department", back_populates="rooms")
    beds = relationship("Bed", back_populates="room")

class Bed(Base):
    """Bed table model."""
    __tablename__ = "beds"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bed_number = Column(String(10), nullable=False)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"), nullable=False)
    bed_type = Column(String(20))  # standard, icu, pediatric, maternity
    status = Column(String(20), default="available")  # available, occupied, maintenance, reserved
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"))
    admission_date = Column(DateTime)
    discharge_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    room = relationship("Room", back_populates="beds")
    patient = relationship("Patient", back_populates="beds")

class Staff(Base):
    """Staff table model."""
    __tablename__ = "staff"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    employee_id = Column(String(20), unique=True, nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    position = Column(String(50), nullable=False)
    specialization = Column(String(100))
    license_number = Column(String(50))
    hire_date = Column(Date, nullable=False)
    salary = Column(DECIMAL(10, 2))
    shift_pattern = Column(String(20))  # day, night, rotating
    status = Column(String(20), default="active")  # active, inactive, on_leave
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="staff")
    department = relationship("Department", back_populates="staff")

class EquipmentCategory(Base):
    """Equipment category table model."""
    __tablename__ = "equipment_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    equipment = relationship("Equipment", back_populates="category")

class Equipment(Base):
    """Equipment table model."""
    __tablename__ = "equipment"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("equipment_categories.id"), nullable=False)
    model = Column(String(100))
    manufacturer = Column(String(100))
    serial_number = Column(String(100))
    purchase_date = Column(Date)
    warranty_expiry = Column(Date)
    location = Column(String(100))
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
    status = Column(String(20), default="available")  # available, in_use, maintenance, out_of_order
    last_maintenance = Column(Date)
    next_maintenance = Column(Date)
    cost = Column(DECIMAL(10, 2))
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    category = relationship("EquipmentCategory", back_populates="equipment")
    department = relationship("Department", back_populates="equipment")

class SupplyCategory(Base):
    """Supply category table model."""
    __tablename__ = "supply_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    supplies = relationship("Supply", back_populates="category")

class Supply(Base):
    """Supply table model."""
    __tablename__ = "supplies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("supply_categories.id"), nullable=False)
    description = Column(Text)
    unit_of_measure = Column(String(20), nullable=False)
    minimum_stock_level = Column(Integer, default=0)
    maximum_stock_level = Column(Integer)
    current_stock = Column(Integer, default=0)
    unit_cost = Column(DECIMAL(8, 2))
    supplier = Column(String(100))
    expiry_date = Column(Date)
    location = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    category = relationship("SupplyCategory", back_populates="supplies")
    transactions = relationship("InventoryTransaction", back_populates="supply")

class InventoryTransaction(Base):
    """Inventory transaction table model."""
    __tablename__ = "inventory_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supply_id = Column(UUID(as_uuid=True), ForeignKey("supplies.id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # in, out, adjustment
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(DECIMAL(8, 2))
    total_cost = Column(DECIMAL(10, 2))
    reference_number = Column(String(50))
    notes = Column(Text)
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    transaction_date = Column(DateTime, default=func.now())

    # Relationships
    supply = relationship("Supply", back_populates="transactions")
    performed_by_user = relationship("User", back_populates="inventory_transactions")

class AgentInteraction(Base):
    """Agent interaction table model."""
    __tablename__ = "agent_interactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_type = Column(String(50), nullable=False)  # bed_management, equipment_tracker, staff_allocation, supply_inventory
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    action_taken = Column(String(100))
    confidence_score = Column(DECIMAL(3, 2))
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="agent_interactions")

class Appointment(Base):
    """Appointment table model."""
    __tablename__ = "appointments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    status = Column(String(20), default="scheduled")  # scheduled, completed, cancelled, no_show
    reason = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="appointments_as_doctor")
    department = relationship("Department", back_populates="appointments")

class MedicalDocument(Base):
    """Medical documents table model for storing uploaded medical files."""
    __tablename__ = "medical_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    document_type = Column(String(50), nullable=False)  # prescription, lab_result, imaging, discharge_summary, etc.
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Local path or S3 URL
    file_size = Column(Integer)  # File size in bytes
    mime_type = Column(String(100))  # File MIME type
    upload_date = Column(DateTime, default=func.now())
    extracted_text = Column(Text)  # OCR extracted text
    processing_status = Column(String(20), default='pending')  # pending, processing, completed, failed
    extracted_metadata = Column(Text)  # JSON string of extracted medical data
    confidence_score = Column(DECIMAL(3, 2))  # AI extraction confidence (0.00-1.00)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="medical_documents")
    extracted_medical_data = relationship("ExtractedMedicalData", back_populates="document")

class ExtractedMedicalData(Base):
    """Structured medical data extracted from documents."""
    __tablename__ = "extracted_medical_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("medical_documents.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    data_type = Column(String(50), nullable=False)  # medication, condition, procedure, allergy, vital_sign
    
    # Medical entity fields
    entity_name = Column(String(200), nullable=False)  # Name of medication, condition, etc.
    entity_value = Column(String(200))  # Dosage, measurement value, etc.
    entity_unit = Column(String(50))  # mg, ml, mmHg, etc.
    
    # Temporal information
    date_prescribed = Column(Date)
    date_recorded = Column(Date)
    date_effective = Column(Date)
    
    # Context information
    doctor_name = Column(String(100))
    hospital_name = Column(String(100))
    department_name = Column(String(100))
    
    # AI extraction metadata
    extraction_confidence = Column(DECIMAL(3, 2))  # Confidence score for this extraction
    extraction_method = Column(String(50))  # OCR, AI_PARSING, MANUAL
    verified = Column(Boolean, default=False)  # Human verified
    
    # Additional context
    notes = Column(Text)  # Additional notes or context
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    document = relationship("MedicalDocument", back_populates="extracted_medical_data")
    patient = relationship("Patient", back_populates="extracted_medical_data")

class DocumentEmbedding(Base):
    """Vector embeddings for RAG system."""
    __tablename__ = "document_embeddings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("medical_documents.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)  # Text chunk for embedding
    chunk_index = Column(Integer, nullable=False)  # Order of chunk in document
    embedding_vector = Column(Text)  # JSON serialized embedding vector
    created_at = Column(DateTime, default=func.now())

    # Relationships
    document = relationship("MedicalDocument")
    patient = relationship("Patient")

# Legacy User model for backward compatibility
class LegacyUser(Base):
    """Legacy User table model for backward compatibility."""
    __tablename__ = "legacy_users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)

class DischargeReport(Base):
    """Discharge report table model."""
    __tablename__ = "discharge_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    discharge_date = Column(DateTime, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="discharge_reports")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="discharge_reports")
    department = relationship("Department", back_populates="discharge_reports")

def create_tables():
    """Create all tables in the database."""
    try:
        # Drop all tables first to avoid conflicts
        Base.metadata.drop_all(bind=engine)
        print("Dropped existing tables")
        
        # Create all tables fresh
        Base.metadata.create_all(bind=engine)
        print("Created all tables successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Helper for session retrieval expected by some tooling files ---
def get_db_session():
    """Return a new database session (convenience wrapper)."""
    return SessionLocal()

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
        existing_count = db.query(LegacyUser).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} legacy users. Skipping migration.")
            return
        
        # Insert users into database
        for user_data in users_data:
            # Don't set the ID, let PostgreSQL auto-generate it
            user = LegacyUser(
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
