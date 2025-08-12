"""
Database extensions for Patient Discharge Report System
=====================================================

Additional tables needed to track comprehensive patient care data.
"""

from sqlalchemy import Column, String, DateTime, Text, DECIMAL, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
import uuid

class TreatmentRecord(Base):
    """Treatment record table - tracks all treatments given to patients."""
    __tablename__ = "treatment_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"))
    bed_id = Column(UUID(as_uuid=True), ForeignKey("beds.id"))
    
    treatment_type = Column(String(100), nullable=False)  # medication, procedure, surgery, therapy, etc.
    treatment_name = Column(String(200), nullable=False)
    description = Column(Text)
    dosage = Column(String(100))  # for medications
    frequency = Column(String(50))  # daily, twice daily, etc.
    duration = Column(String(50))  # 7 days, 2 weeks, etc.
    
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    status = Column(String(20), default="active")  # active, completed, discontinued, suspended
    
    notes = Column(Text)
    side_effects = Column(Text)
    effectiveness = Column(String(20))  # excellent, good, fair, poor
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="treatments")
    doctor = relationship("User", foreign_keys=[doctor_id])
    appointment = relationship("Appointment")
    bed = relationship("Bed")

class EquipmentUsage(Base):
    """Equipment usage tracking for patients."""
    __tablename__ = "equipment_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=False)
    staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False)
    bed_id = Column(UUID(as_uuid=True), ForeignKey("beds.id"))
    
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_minutes = Column(Integer)
    
    purpose = Column(String(200))  # monitoring, treatment, diagnostic, etc.
    settings = Column(Text)  # JSON storing equipment settings
    readings = Column(Text)  # JSON storing readings/measurements
    
    status = Column(String(20), default="in_use")  # in_use, completed, interrupted
    notes = Column(Text)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="equipment_usage")
    equipment = relationship("Equipment")
    staff = relationship("Staff")
    bed = relationship("Bed")

class StaffAssignment(Base):
    """Track staff assignments to patients during their stay."""
    __tablename__ = "staff_assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False)
    bed_id = Column(UUID(as_uuid=True), ForeignKey("beds.id"))
    
    assignment_type = Column(String(50), nullable=False)  # primary_nurse, attending_doctor, specialist, therapist
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    
    shift = Column(String(20))  # morning, afternoon, night, all_day
    responsibilities = Column(Text)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="staff_assignments")
    staff = relationship("Staff")
    bed = relationship("Bed")

class DischargeReport(Base):
    """Store generated discharge reports."""
    __tablename__ = "discharge_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    bed_id = Column(UUID(as_uuid=True), ForeignKey("beds.id"), nullable=False)
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    report_number = Column(String(50), unique=True, nullable=False)
    admission_date = Column(DateTime, nullable=False)
    discharge_date = Column(DateTime, nullable=False)
    length_of_stay_days = Column(Integer)
    
    # Report sections as JSON
    patient_summary = Column(Text)  # JSON
    treatment_summary = Column(Text)  # JSON
    equipment_summary = Column(Text)  # JSON
    staff_summary = Column(Text)  # JSON
    medications = Column(Text)  # JSON
    procedures = Column(Text)  # JSON
    discharge_instructions = Column(Text)
    follow_up_required = Column(Text)
    
    # Discharge conditions
    discharge_condition = Column(String(50))  # improved, stable, critical, deceased
    discharge_destination = Column(String(100))  # home, transfer, rehabilitation, nursing_home
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    patient = relationship("Patient")
    bed = relationship("Bed")
    generated_by_user = relationship("User", foreign_keys=[generated_by])
