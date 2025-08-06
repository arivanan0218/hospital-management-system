"""Hospital Management System MCP Server - Complete CRUD Operations for All Tables."""

import random
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import Date
from mcp.server.fastmcp import FastMCP

from meeting_scheduler import MeetingSchedulerAgent
from meeting_management import MeetingManager, Meeting, MeetingParticipant

# Import database modules
try:
    from database import (
        User, Department, Patient, Room, Bed, Staff, Equipment, EquipmentCategory,
        Supply, SupplyCategory, InventoryTransaction, AgentInteraction, Appointment,
        LegacyUser, SessionLocal
    )
    from staff_meetings import StaffMeeting, staff_meeting_participants
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("WARNING: Database modules not available. Install dependencies: pip install sqlalchemy psycopg2-binary")

# Initialize FastMCP server
mcp = FastMCP("hospital-management-system")

# Initialize Meeting Scheduler Agent
scheduler_agent = MeetingSchedulerAgent()

# Database helper functions
def get_db_session() -> Session:
    """Get database session."""
    return SessionLocal()

def serialize_model(obj):
    """Convert SQLAlchemy model to dictionary."""
    if obj is None:
        return None
    
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        if isinstance(value, uuid.UUID):
            result[column.name] = str(value)
        elif isinstance(value, (datetime, date)):
            result[column.name] = value.isoformat()
        elif isinstance(value, Decimal):
            result[column.name] = float(value)
        else:
            result[column.name] = value
    return result

# ================================
# USER CRUD OPERATIONS
# ================================

@mcp.tool()
def create_user(username: str, email: str, password_hash: str, role: str, 
                first_name: str, last_name: str, phone: str = None) -> Dict[str, Any]:
    """Create a new user in the database."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        result = serialize_model(user)
        db.close()
        
        return {"success": True, "message": "User created successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to create user: {str(e)}"}

@mcp.tool()
def get_user_by_id(user_id: str) -> Dict[str, Any]:
    """Get a user by ID."""
    if not DATABASE_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        db = get_db_session()
        user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
        result = serialize_model(user) if user else None
        db.close()
        
        if result:
            return {"data": result}
        else:
            return {"error": "User not found"}
    except Exception as e:
        return {"error": f"Failed to get user: {str(e)}"}

@mcp.tool()
def list_users() -> Dict[str, Any]:
    """List all users."""
    if not DATABASE_AVAILABLE:
        return {"error": "Database not available", "users": [], "count": 0}
    
    try:
        db = get_db_session()
        users = db.query(User).all()
        result = [serialize_model(user) for user in users]
        db.close()
        
        return {"users": result, "count": len(result)}
    except Exception as e:
        return {"error": f"Failed to list users: {str(e)}", "users": [], "count": 0}

@mcp.tool()
def update_user(user_id: str, username: str = None, email: str = None, role: str = None,
                first_name: str = None, last_name: str = None, phone: str = None,
                is_active: bool = None) -> Dict[str, Any]:
    """Update a user."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
        
        if not user:
            db.close()
            return {"success": False, "message": "User not found"}
        
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if role is not None:
            user.role = role
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if phone is not None:
            user.phone = phone
        if is_active is not None:
            user.is_active = is_active
        
        db.commit()
        db.refresh(user)
        result = serialize_model(user)
        db.close()
        
        return {"success": True, "message": "User updated successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to update user: {str(e)}"}

@mcp.tool()
def delete_user(user_id: str) -> Dict[str, Any]:
    """Delete a user."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
        
        if not user:
            db.close()
            return {"success": False, "message": "User not found"}
        
        db.delete(user)
        db.commit()
        db.close()
        
        return {"success": True, "message": "User deleted successfully"}
    except Exception as e:
        return {"success": False, "message": f"Failed to delete user: {str(e)}"}

# ================================
# DEPARTMENT CRUD OPERATIONS
# ================================

@mcp.tool()
def create_department(name: str, description: str = None, head_doctor_id: str = None,
                     floor_number: int = None, phone: str = None, email: str = None) -> Dict[str, Any]:
    """Create a new department."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        department = Department(
            name=name,
            description=description,
            head_doctor_id=uuid.UUID(head_doctor_id) if head_doctor_id else None,
            floor_number=floor_number,
            phone=phone,
            email=email
        )
        db.add(department)
        db.commit()
        db.refresh(department)
        result = serialize_model(department)
        db.close()
        
        return {"success": True, "message": "Department created successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to create department: {str(e)}"}

@mcp.tool()
def list_departments() -> Dict[str, Any]:
    """List all departments."""
    if not DATABASE_AVAILABLE:
        return {"error": "Database not available", "departments": [], "count": 0}
    
    try:
        db = get_db_session()
        departments = db.query(Department).all()
        result = [serialize_model(dept) for dept in departments]
        db.close()
        
        return {"departments": result, "count": len(result)}
    except Exception as e:
        return {"error": f"Failed to list departments: {str(e)}", "departments": [], "count": 0}

@mcp.tool()
def get_department_by_id(department_id: str) -> Dict[str, Any]:
    """Get a department by ID."""
    if not DATABASE_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        db = get_db_session()
        department = db.query(Department).filter(Department.id == uuid.UUID(department_id)).first()
        result = serialize_model(department) if department else None
        db.close()
        
        if result:
            return {"data": result}
        else:
            return {"error": "Department not found"}
    except Exception as e:
        return {"error": f"Failed to get department: {str(e)}"}

# ================================
# PATIENT CRUD OPERATIONS
# ================================

@mcp.tool()
def create_patient(patient_number: str, first_name: str, last_name: str, date_of_birth: str,
                  gender: str = None, phone: str = None, email: str = None, address: str = None,
                  emergency_contact_name: str = None, emergency_contact_phone: str = None,
                  blood_type: str = None, allergies: str = None, medical_history: str = None) -> Dict[str, Any]:
    """Create a new patient."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        patient = Patient(
            patient_number=patient_number,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=datetime.strptime(date_of_birth, "%Y-%m-%d").date(),
            gender=gender,
            phone=phone,
            email=email,
            address=address,
            emergency_contact_name=emergency_contact_name,
            emergency_contact_phone=emergency_contact_phone,
            blood_type=blood_type,
            allergies=allergies,
            medical_history=medical_history
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
        result = serialize_model(patient)
        db.close()
        
        return {"success": True, "message": "Patient created successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to create patient: {str(e)}"}

@mcp.tool()
def list_patients() -> Dict[str, Any]:
    """List all patients."""
    if not DATABASE_AVAILABLE:
        return {"error": "Database not available", "patients": [], "count": 0}
    
    try:
        db = get_db_session()
        patients = db.query(Patient).all()
        result = [serialize_model(patient) for patient in patients]
        db.close()
        
        return {"patients": result, "count": len(result)}
    except Exception as e:
        return {"error": f"Failed to list patients: {str(e)}", "patients": [], "count": 0}

@mcp.tool()
def get_patient_by_id(patient_id: str) -> Dict[str, Any]:
    """Get a patient by ID."""
    if not DATABASE_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        db = get_db_session()
        patient = db.query(Patient).filter(Patient.id == uuid.UUID(patient_id)).first()
        result = serialize_model(patient) if patient else None
        db.close()
        
        if result:
            return {"data": result}
        else:
            return {"error": "Patient not found"}
    except Exception as e:
        return {"error": f"Failed to get patient: {str(e)}"}

# ================================
# ROOM CRUD OPERATIONS
# ================================

@mcp.tool()
def create_room(room_number: str, department_id: str, room_type: str = None,
               floor_number: int = None, capacity: int = 1) -> Dict[str, Any]:
    """Create a new room."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        room = Room(
            room_number=room_number,
            department_id=uuid.UUID(department_id),
            room_type=room_type,
            floor_number=floor_number,
            capacity=capacity
        )
        db.add(room)
        db.commit()
        db.refresh(room)
        result = serialize_model(room)
        db.close()
        
        return {"success": True, "message": "Room created successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to create room: {str(e)}"}

@mcp.tool()
def list_rooms() -> Dict[str, Any]:
    """List all rooms."""
    if not DATABASE_AVAILABLE:
        return {"error": "Database not available", "rooms": [], "count": 0}
    
    try:
        db = get_db_session()
        rooms = db.query(Room).all()
        result = [serialize_model(room) for room in rooms]
        db.close()
        
        return {"rooms": result, "count": len(result)}
    except Exception as e:
        return {"error": f"Failed to list rooms: {str(e)}", "rooms": [], "count": 0}

# ================================
# BED CRUD OPERATIONS (for Bed Management Agent)
# ================================

@mcp.tool()
def create_bed(bed_number: str, room_id: str, bed_type: str = None, status: str = "available") -> Dict[str, Any]:
    """Create a new bed."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        bed = Bed(
            bed_number=bed_number,
            room_id=uuid.UUID(room_id),
            bed_type=bed_type,
            status=status
        )
        db.add(bed)
        db.commit()
        db.refresh(bed)
        result = serialize_model(bed)
        db.close()
        
        return {"success": True, "message": "Bed created successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to create bed: {str(e)}"}

@mcp.tool()
def list_beds(status: str = None) -> Dict[str, Any]:
    """List all beds, optionally filtered by status."""
    if not DATABASE_AVAILABLE:
        return {"error": "Database not available", "beds": [], "count": 0}
    
    try:
        db = get_db_session()
        query = db.query(Bed)
        if status:
            query = query.filter(Bed.status == status)
        beds = query.all()
        result = [serialize_model(bed) for bed in beds]
        db.close()
        
        return {"beds": result, "count": len(result)}
    except Exception as e:
        return {"error": f"Failed to list beds: {str(e)}", "beds": [], "count": 0}

@mcp.tool()
def assign_bed_to_patient(bed_id: str, patient_id: str, admission_date: str = None) -> Dict[str, Any]:
    """Assign a bed to a patient."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        bed = db.query(Bed).filter(Bed.id == uuid.UUID(bed_id)).first()
        
        if not bed:
            db.close()
            return {"success": False, "message": "Bed not found"}
        
        if bed.status != "available":
            db.close()
            return {"success": False, "message": "Bed is not available"}
        
        bed.patient_id = uuid.UUID(patient_id)
        bed.status = "occupied"
        bed.admission_date = datetime.fromisoformat(admission_date) if admission_date else datetime.now()
        
        db.commit()
        db.refresh(bed)
        result = serialize_model(bed)
        db.close()
        
        return {"success": True, "message": "Bed assigned successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to assign bed: {str(e)}"}

@mcp.tool()
def discharge_bed(bed_id: str, discharge_date: str = None) -> Dict[str, Any]:
    """Discharge a patient from a bed."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        bed = db.query(Bed).filter(Bed.id == uuid.UUID(bed_id)).first()
        
        if not bed:
            db.close()
            return {"success": False, "message": "Bed not found"}
        
        bed.patient_id = None
        bed.status = "available"
        bed.discharge_date = datetime.fromisoformat(discharge_date) if discharge_date else datetime.now()
        
        db.commit()
        db.refresh(bed)
        result = serialize_model(bed)
        db.close()
        
        return {"success": True, "message": "Bed discharged successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to discharge bed: {str(e)}"}

# ================================
# STAFF CRUD OPERATIONS (for Staff Allocation Agent)
# ================================

@mcp.tool()
def create_staff(user_id: str, employee_id: str, department_id: str, position: str,
                specialization: str = None, license_number: str = None, hire_date: str = None,
                salary: float = None, shift_pattern: str = None, status: str = "active") -> Dict[str, Any]:
    """Create a new staff member."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        staff = Staff(
            user_id=uuid.UUID(user_id),
            employee_id=employee_id,
            department_id=uuid.UUID(department_id),
            position=position,
            specialization=specialization,
            license_number=license_number,
            hire_date=datetime.strptime(hire_date, "%Y-%m-%d").date() if hire_date else date.today(),
            salary=Decimal(str(salary)) if salary else None,
            shift_pattern=shift_pattern,
            status=status
        )
        db.add(staff)
        db.commit()
        db.refresh(staff)
        result = serialize_model(staff)
        db.close()
        
        return {"success": True, "message": "Staff created successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to create staff: {str(e)}"}

@mcp.tool()
def list_staff(department_id: str = None, status: str = None) -> Dict[str, Any]:
    """List all staff members, optionally filtered by department or status."""
    if not DATABASE_AVAILABLE:
        return {"error": "Database not available", "staff": [], "count": 0}
    
    try:
        db = get_db_session()
        query = db.query(Staff)
        if department_id:
            query = query.filter(Staff.department_id == uuid.UUID(department_id))
        if status:
            query = query.filter(Staff.status == status)
        staff_members = query.all()
        result = [serialize_model(staff) for staff in staff_members]
        db.close()
        
        return {"staff": result, "count": len(result)}
    except Exception as e:
        return {"error": f"Failed to list staff: {str(e)}", "staff": [], "count": 0}

# ================================
# EQUIPMENT CRUD OPERATIONS (for Equipment Tracker Agent)
# ================================

@mcp.tool()
def create_equipment_category(name: str, description: str = None) -> Dict[str, Any]:
    """Create a new equipment category."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        category = EquipmentCategory(name=name, description=description)
        db.add(category)
        db.commit()
        db.refresh(category)
        result = serialize_model(category)
        db.close()
        
        return {"success": True, "message": "Equipment category created successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to create equipment category: {str(e)}"}

@mcp.tool()
def create_equipment(equipment_id: str, name: str, category_id: str, model: str = None,
                    manufacturer: str = None, serial_number: str = None, purchase_date: str = None,
                    warranty_expiry: str = None, location: str = None, department_id: str = None,
                    cost: float = None) -> Dict[str, Any]:
    """Create a new equipment item."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        equipment = Equipment(
            equipment_id=equipment_id,
            name=name,
            category_id=uuid.UUID(category_id),
            model=model,
            manufacturer=manufacturer,
            serial_number=serial_number,
            purchase_date=datetime.strptime(purchase_date, "%Y-%m-%d").date() if purchase_date else None,
            warranty_expiry=datetime.strptime(warranty_expiry, "%Y-%m-%d").date() if warranty_expiry else None,
            location=location,
            department_id=uuid.UUID(department_id) if department_id else None,
            cost=Decimal(str(cost)) if cost else None
        )
        db.add(equipment)
        db.commit()
        db.refresh(equipment)
        result = serialize_model(equipment)
        db.close()
        
        return {"success": True, "message": "Equipment created successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to create equipment: {str(e)}"}

@mcp.tool()
def list_equipment(status: str = None, department_id: str = None) -> Dict[str, Any]:
    """List all equipment, optionally filtered by status or department."""
    if not DATABASE_AVAILABLE:
        return {"error": "Database not available", "equipment": [], "count": 0}
    
    try:
        db = get_db_session()
        query = db.query(Equipment)
        if status:
            query = query.filter(Equipment.status == status)
        if department_id:
            query = query.filter(Equipment.department_id == uuid.UUID(department_id))
        equipment_items = query.all()
        result = [serialize_model(item) for item in equipment_items]
        db.close()
        
        return {"equipment": result, "count": len(result)}
    except Exception as e:
        return {"error": f"Failed to list equipment: {str(e)}", "equipment": [], "count": 0}

@mcp.tool()
def update_equipment_status(equipment_id: str, status: str, notes: str = None) -> Dict[str, Any]:
    """Update equipment status."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        equipment = db.query(Equipment).filter(Equipment.id == uuid.UUID(equipment_id)).first()
        
        if not equipment:
            db.close()
            return {"success": False, "message": "Equipment not found"}
        
        equipment.status = status
        if notes:
            equipment.notes = notes
        
        db.commit()
        db.refresh(equipment)
        result = serialize_model(equipment)
        db.close()
        
        return {"success": True, "message": "Equipment status updated successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to update equipment status: {str(e)}"}

# ================================
# SUPPLY CRUD OPERATIONS (for Supply Inventory Agent)
# ================================

@mcp.tool()
def create_supply_category(name: str, description: str = None) -> Dict[str, Any]:
    """Create a new supply category."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        category = SupplyCategory(name=name, description=description)
        db.add(category)
        db.commit()
        db.refresh(category)
        result = serialize_model(category)
        db.close()
        
        return {"success": True, "message": "Supply category created successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to create supply category: {str(e)}"}

@mcp.tool()
def create_supply(item_code: str, name: str, category_id: str, unit_of_measure: str,
                 description: str = None, minimum_stock_level: int = 0, maximum_stock_level: int = None,
                 current_stock: int = 0, unit_cost: float = None, supplier: str = None,
                 expiry_date: str = None, location: str = None) -> Dict[str, Any]:
    """Create a new supply item."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        supply = Supply(
            item_code=item_code,
            name=name,
            category_id=uuid.UUID(category_id),
            description=description,
            unit_of_measure=unit_of_measure,
            minimum_stock_level=minimum_stock_level,
            maximum_stock_level=maximum_stock_level,
            current_stock=current_stock,
            unit_cost=Decimal(str(unit_cost)) if unit_cost else None,
            supplier=supplier,
            expiry_date=datetime.strptime(expiry_date, "%Y-%m-%d").date() if expiry_date else None,
            location=location
        )
        db.add(supply)
        db.commit()
        db.refresh(supply)
        result = serialize_model(supply)
        db.close()
        
        return {"success": True, "message": "Supply created successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to create supply: {str(e)}"}

@mcp.tool()
def list_supplies(low_stock_only: bool = False) -> Dict[str, Any]:
    """List all supplies, optionally showing only low stock items."""
    if not DATABASE_AVAILABLE:
        return {"error": "Database not available", "supplies": [], "count": 0}
    
    try:
        db = get_db_session()
        query = db.query(Supply)
        if low_stock_only:
            query = query.filter(Supply.current_stock <= Supply.minimum_stock_level)
        supplies = query.all()
        result = [serialize_model(supply) for supply in supplies]
        db.close()
        
        return {"supplies": result, "count": len(result)}
    except Exception as e:
        return {"error": f"Failed to list supplies: {str(e)}", "supplies": [], "count": 0}

@mcp.tool()
def update_supply_stock(supply_id: str, quantity_change: int, transaction_type: str,
                       performed_by: str, unit_cost: float = None, reference_number: str = None,
                       notes: str = None) -> Dict[str, Any]:
    """Update supply stock and create inventory transaction."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        supply = db.query(Supply).filter(Supply.id == uuid.UUID(supply_id)).first()
        
        if not supply:
            db.close()
            return {"success": False, "message": "Supply not found"}
        
        # Update stock
        if transaction_type == "in":
            supply.current_stock += quantity_change
        elif transaction_type == "out":
            if supply.current_stock < quantity_change:
                db.close()
                return {"success": False, "message": "Insufficient stock"}
            supply.current_stock -= quantity_change
        elif transaction_type == "adjustment":
            supply.current_stock = quantity_change
        
        # Create transaction record
        transaction = InventoryTransaction(
            supply_id=uuid.UUID(supply_id),
            transaction_type=transaction_type,
            quantity=quantity_change,
            unit_cost=Decimal(str(unit_cost)) if unit_cost else None,
            total_cost=Decimal(str(unit_cost * quantity_change)) if unit_cost else None,
            reference_number=reference_number,
            notes=notes,
            performed_by=uuid.UUID(performed_by)
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(supply)
        result = serialize_model(supply)
        db.close()
        
        return {"success": True, "message": "Supply stock updated successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to update supply stock: {str(e)}"}

# ================================
# APPOINTMENT CRUD OPERATIONS
# ================================

@mcp.tool()
def create_appointment(patient_id: str, doctor_id: str, department_id: str, appointment_date: str,
                      duration_minutes: int = 30, reason: str = None, notes: str = None) -> Dict[str, Any]:
    """Create a new appointment."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        appointment = Appointment(
            patient_id=uuid.UUID(patient_id),
            doctor_id=uuid.UUID(doctor_id),
            department_id=uuid.UUID(department_id),
            appointment_date=datetime.fromisoformat(appointment_date),
            duration_minutes=duration_minutes,
            reason=reason,
            notes=notes
        )
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        result = serialize_model(appointment)
        db.close()
        
        return {"success": True, "message": "Appointment created successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to create appointment: {str(e)}"}

@mcp.tool()
def list_appointments(doctor_id: str = None, patient_id: str = None, date: str = None) -> Dict[str, Any]:
    """List appointments, optionally filtered by doctor, patient, or date."""
    if not DATABASE_AVAILABLE:
        return {"error": "Database not available", "appointments": [], "count": 0}
    
    try:
        db = get_db_session()
        query = db.query(Appointment)
        if doctor_id:
            query = query.filter(Appointment.doctor_id == uuid.UUID(doctor_id))
        if patient_id:
            query = query.filter(Appointment.patient_id == uuid.UUID(patient_id))
        if date:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(Appointment.appointment_date.cast(Date) == date_obj)
        
        appointments = query.all()
        result = [serialize_model(appointment) for appointment in appointments]
        db.close()
        
        return {"appointments": result, "count": len(result)}
    except Exception as e:
        return {"error": f"Failed to list appointments: {str(e)}", "appointments": [], "count": 0}

# ================================
# AGENT INTERACTION LOGGING
# ================================

@mcp.tool()
def log_agent_interaction(agent_type: str, query: str, response: str, user_id: str = None,
                         action_taken: str = None, confidence_score: float = None,
                         execution_time_ms: int = None) -> Dict[str, Any]:
    """Log an AI agent interaction."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        interaction = AgentInteraction(
            agent_type=agent_type,
            user_id=uuid.UUID(user_id) if user_id else None,
            query=query,
            response=response,
            action_taken=action_taken,
            confidence_score=Decimal(str(confidence_score)) if confidence_score else None,
            execution_time_ms=execution_time_ms
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        result = serialize_model(interaction)
        db.close()
        
        return {"success": True, "message": "Agent interaction logged successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to log agent interaction: {str(e)}"}

# ================================
# LEGACY USER OPERATIONS (for backward compatibility)
# ================================

@mcp.tool()
def create_legacy_user(name: str, email: str, address: str, phone: str) -> Dict[str, Any]:
    """Create a new legacy user (for backward compatibility)."""
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        user = LegacyUser(name=name, email=email, address=address, phone=phone)
        db.add(user)
        db.commit()
        db.refresh(user)
        result = serialize_model(user)
        db.close()
        
        return {"success": True, "message": "Legacy user created successfully", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Failed to create legacy user: {str(e)}"}

@mcp.tool()
def list_legacy_users() -> Dict[str, Any]:
    """List all legacy users."""
    if not DATABASE_AVAILABLE:
        return {"error": "Database not available", "users": [], "count": 0}
    
    try:
        db = get_db_session()
        users = db.query(LegacyUser).all()
        result = [serialize_model(user) for user in users]
        db.close()
        
        return {"users": result, "count": len(result)}
    except Exception as e:
        return {"error": f"Failed to list legacy users: {str(e)}", "users": [], "count": 0}

# ================================
# STAFF MEETINGS OPERATIONS
# ================================

@mcp.tool()
def list_staff_meetings(staff_id: str = None, from_date: str = None, to_date: str = None) -> Dict[str, Any]:
    """List staff meetings with optional filters."""
    if not DATABASE_AVAILABLE:
        return {"error": "Database not available", "meetings": [], "count": 0}
    
    try:
        db = get_db_session()
        query = db.query(StaffMeeting)
        
        if staff_id:
            query = query.join(staff_meeting_participants).filter(
                staff_meeting_participants.c.staff_id == uuid.UUID(staff_id)
            )
        
        if from_date:
            query = query.filter(StaffMeeting.meeting_time >= datetime.fromisoformat(from_date))
        if to_date:
            query = query.filter(StaffMeeting.meeting_time <= datetime.fromisoformat(to_date))
        
        meetings = query.order_by(StaffMeeting.meeting_time.desc()).all()
        result = [serialize_model(meeting) for meeting in meetings]
        db.close()
        
        return {"meetings": result, "count": len(result)}
    except Exception as e:
        return {"error": f"Failed to list meetings: {str(e)}", "meetings": [], "count": 0}

# ================================
# MEETING SCHEDULER AGENT
# ================================

@mcp.tool()
def schedule_meeting_with_staff(query: str) -> Dict[str, Any]:
    """Schedule a meeting with available staff members.
    
    This tool will:
    1. Parse the meeting request
    2. Find available staff members
    3. Schedule the meeting at the next available time slot
    4. Send email notifications to all participants
    """
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        # Use the scheduler agent to handle the request
        result = scheduler_agent.schedule_meeting(query)
        
        # Create a clean, encoding-safe response
        if result.get("success"):
            # Extract key information safely
            meeting_data = result.get("data", {})
            meeting_id = meeting_data.get("meeting_id", "N/A")
            google_meet_link = meeting_data.get("google_meet_link", "")
            participants = meeting_data.get("participants", 0)
            emails_sent = meeting_data.get("emails_sent", 0)
            
            # Create safe response without emojis or special characters
            safe_response = {
                "success": True,
                "message": "Meeting scheduled successfully with Google Meet link",
                "meeting_id": meeting_id,
                "google_meet_link": google_meet_link,
                "participants_invited": participants,
                "emails_sent": emails_sent,
                "status": "scheduled"
            }
            
            # Log the successful interaction
            log_agent_interaction(
                agent_type="meeting_scheduler",
                query=query,
                response="Meeting scheduled successfully",
                action_taken="schedule_meeting",
                confidence_score=0.95
            )
            
            return safe_response
        else:
            # Return clean error response
            error_message = result.get("message", "Unknown error occurred")
            return {
                "success": False,
                "message": error_message,
                "status": "failed"
            }
    except Exception as e:
        error_msg = f"Failed to schedule meeting: {str(e)}"
        log_agent_interaction(
            agent_type="meeting_scheduler",
            query=query,
            response=error_msg,
            action_taken="schedule_meeting_failed",
            confidence_score=0.0
        )
        return {"success": False, "message": error_msg}

# ================================
# MEETING RETRIEVAL FUNCTIONS
# ================================

@mcp.tool()
def get_meetings_by_date(meeting_date: str) -> Dict[str, Any]:
    """Get all meetings for a specific date.
    
    Args:
        meeting_date: Date in YYYY-MM-DD format (e.g., '2025-08-07')
    
    Returns:
        Dictionary with meeting details for the specified date
    """
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        from datetime import datetime, date
        
        # Parse the date
        target_date = datetime.strptime(meeting_date, '%Y-%m-%d').date()
        
        meeting_manager = MeetingManager()
        meetings = meeting_manager.get_meetings_by_date(target_date)
        
        meeting_list = []
        for meeting in meetings:
            # Get participants for this meeting
            participants = meeting_manager.get_meeting_participants(str(meeting.id))
            
            meeting_data = {
                'meeting_id': str(meeting.id),
                'title': meeting.title,
                'description': meeting.description,
                'meeting_datetime': meeting.meeting_datetime.isoformat(),
                'duration_minutes': meeting.duration_minutes,
                'location': meeting.location,
                'google_meet_link': meeting.google_meet_link,
                'google_event_id': meeting.google_event_id,
                'meeting_type': meeting.meeting_type,
                'status': meeting.status,
                'priority': meeting.priority,
                'agenda': meeting.agenda,
                'participants': participants,
                'participant_count': len(participants),
                'organizer_name': f"{meeting.organizer.user.first_name} {meeting.organizer.user.last_name}" if meeting.organizer else "Unknown",
                'department': meeting.department.name if meeting.department else "General",
                'created_at': meeting.created_at.isoformat()
            }
            meeting_list.append(meeting_data)
        
        meeting_manager.close()
        
        return {
            "success": True,
            "date": meeting_date,
            "total_meetings": len(meeting_list),
            "meetings": meeting_list
        }
        
    except ValueError as e:
        return {"success": False, "message": f"Invalid date format. Use YYYY-MM-DD: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"Error retrieving meetings: {str(e)}"}

@mcp.tool()
def get_meetings_by_time_range(start_datetime: str, end_datetime: str) -> Dict[str, Any]:
    """Get all meetings within a specific time range.
    
    Args:
        start_datetime: Start datetime in YYYY-MM-DD HH:MM format (e.g., '2025-08-07 09:00')
        end_datetime: End datetime in YYYY-MM-DD HH:MM format (e.g., '2025-08-07 17:00')
    
    Returns:
        Dictionary with meeting details for the specified time range
    """
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        from datetime import datetime
        
        # Parse the datetime strings
        start_dt = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M')
        end_dt = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M')
        
        meeting_manager = MeetingManager()
        meetings = meeting_manager.get_meetings_by_time_range(start_dt, end_dt)
        
        meeting_list = []
        for meeting in meetings:
            # Get participants for this meeting
            participants = meeting_manager.get_meeting_participants(str(meeting.id))
            
            meeting_data = {
                'meeting_id': str(meeting.id),
                'title': meeting.title,
                'description': meeting.description,
                'meeting_datetime': meeting.meeting_datetime.isoformat(),
                'duration_minutes': meeting.duration_minutes,
                'location': meeting.location,
                'google_meet_link': meeting.google_meet_link,
                'google_event_id': meeting.google_event_id,
                'meeting_type': meeting.meeting_type,
                'status': meeting.status,
                'priority': meeting.priority,
                'agenda': meeting.agenda,
                'participants': participants,
                'participant_count': len(participants),
                'organizer_name': f"{meeting.organizer.user.first_name} {meeting.organizer.user.last_name}" if meeting.organizer else "Unknown",
                'department': meeting.department.name if meeting.department else "General",
                'created_at': meeting.created_at.isoformat()
            }
            meeting_list.append(meeting_data)
        
        meeting_manager.close()
        
        return {
            "success": True,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "total_meetings": len(meeting_list),
            "meetings": meeting_list
        }
        
    except ValueError as e:
        return {"success": False, "message": f"Invalid datetime format. Use YYYY-MM-DD HH:MM: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"Error retrieving meetings: {str(e)}"}

@mcp.tool()
def get_meeting_details(meeting_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific meeting.
    
    Args:
        meeting_id: The UUID of the meeting
    
    Returns:
        Dictionary with complete meeting details
    """
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        meeting_manager = MeetingManager()
        meeting = meeting_manager.get_meeting_by_id(meeting_id)
        
        if not meeting:
            meeting_manager.close()
            return {"success": False, "message": "Meeting not found"}
        
        # Get participants for this meeting
        participants = meeting_manager.get_meeting_participants(meeting_id)
        
        meeting_data = {
            'meeting_id': str(meeting.id),
            'title': meeting.title,
            'description': meeting.description,
            'meeting_datetime': meeting.meeting_datetime.isoformat(),
            'duration_minutes': meeting.duration_minutes,
            'location': meeting.location,
            'google_meet_link': meeting.google_meet_link,
            'google_event_id': meeting.google_event_id,
            'google_meet_room_code': meeting.google_meet_room_code,
            'meeting_type': meeting.meeting_type,
            'status': meeting.status,
            'priority': meeting.priority,
            'agenda': meeting.agenda,
            'meeting_notes': meeting.meeting_notes,
            'action_items': meeting.action_items,
            'participants': participants,
            'participant_count': len(participants),
            'organizer_id': str(meeting.organizer_id) if meeting.organizer_id else None,
            'organizer_name': f"{meeting.organizer.user.first_name} {meeting.organizer.user.last_name}" if meeting.organizer else "Unknown",
            'department_id': str(meeting.department_id) if meeting.department_id else None,
            'department': meeting.department.name if meeting.department else "General",
            'email_sent': meeting.email_sent,
            'calendar_invites_sent': meeting.calendar_invites_sent,
            'reminder_sent': meeting.reminder_sent,
            'created_at': meeting.created_at.isoformat(),
            'updated_at': meeting.updated_at.isoformat(),
            'cancelled_at': meeting.cancelled_at.isoformat() if meeting.cancelled_at else None
        }
        
        meeting_manager.close()
        
        return {
            "success": True,
            "meeting": meeting_data
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error retrieving meeting details: {str(e)}"}

@mcp.tool()
def get_upcoming_meetings(days_ahead: int = 7) -> Dict[str, Any]:
    """Get all upcoming meetings within specified days.
    
    Args:
        days_ahead: Number of days to look ahead (default: 7)
    
    Returns:
        Dictionary with upcoming meeting details
    """
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        meeting_manager = MeetingManager()
        meetings = meeting_manager.get_upcoming_meetings(days_ahead)
        
        meeting_list = []
        for meeting in meetings:
            # Get participants for this meeting
            participants = meeting_manager.get_meeting_participants(str(meeting.id))
            
            meeting_data = {
                'meeting_id': str(meeting.id),
                'title': meeting.title,
                'description': meeting.description,
                'meeting_datetime': meeting.meeting_datetime.isoformat(),
                'duration_minutes': meeting.duration_minutes,
                'location': meeting.location,
                'google_meet_link': meeting.google_meet_link,
                'meeting_type': meeting.meeting_type,
                'status': meeting.status,
                'priority': meeting.priority,
                'participants': participants,
                'participant_count': len(participants),
                'organizer_name': f"{meeting.organizer.user.first_name} {meeting.organizer.user.last_name}" if meeting.organizer else "Unknown",
                'department': meeting.department.name if meeting.department else "General"
            }
            meeting_list.append(meeting_data)
        
        meeting_manager.close()
        
        return {
            "success": True,
            "days_ahead": days_ahead,
            "total_meetings": len(meeting_list),
            "meetings": meeting_list
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error retrieving upcoming meetings: {str(e)}"}

@mcp.tool()
def update_meeting_status(meeting_id: str, status: str) -> Dict[str, Any]:
    """Update the status of a meeting.
    
    Args:
        meeting_id: The UUID of the meeting
        status: New status (scheduled, in_progress, completed, cancelled)
    
    Returns:
        Dictionary with update result
    """
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        valid_statuses = ['scheduled', 'in_progress', 'completed', 'cancelled']
        if status not in valid_statuses:
            return {"success": False, "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}
        
        meeting_manager = MeetingManager()
        success = meeting_manager.update_meeting_status(meeting_id, status)
        meeting_manager.close()
        
        if success:
            return {
                "success": True,
                "message": f"Meeting status updated to '{status}'",
                "meeting_id": meeting_id,
                "new_status": status
            }
        else:
            return {"success": False, "message": "Meeting not found or update failed"}
            
    except Exception as e:
        return {"success": False, "message": f"Error updating meeting status: {str(e)}"}

@mcp.tool()
def add_meeting_notes(meeting_id: str, notes: str, action_items: str = None) -> Dict[str, Any]:
    """Add notes and action items to a completed meeting.
    
    Args:
        meeting_id: The UUID of the meeting
        notes: Meeting notes or summary
        action_items: Action items from the meeting (optional)
    
    Returns:
        Dictionary with update result
    """
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        meeting_manager = MeetingManager()
        success = meeting_manager.add_meeting_notes(meeting_id, notes, action_items)
        meeting_manager.close()
        
        if success:
            return {
                "success": True,
                "message": "Meeting notes added successfully",
                "meeting_id": meeting_id
            }
        else:
            return {"success": False, "message": "Meeting not found or update failed"}
            
    except Exception as e:
        return {"success": False, "message": f"Error adding meeting notes: {str(e)}"}

@mcp.tool()
def search_meetings_by_title(title_query: str) -> Dict[str, Any]:
    """Search meetings by title using partial text matching.
    
    Args:
        title_query: Text to search for in meeting titles (case-insensitive)
    
    Returns:
        Dictionary with matching meetings
    """
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        meeting_manager = MeetingManager()
        meetings = meeting_manager.search_meetings_by_title(title_query)
        
        meeting_list = []
        for meeting in meetings:
            participants = meeting_manager.get_meeting_participants(str(meeting.id))
            
            meeting_data = {
                'meeting_id': str(meeting.id),
                'title': meeting.title,
                'description': meeting.description,
                'meeting_datetime': meeting.meeting_datetime.isoformat(),
                'duration_minutes': meeting.duration_minutes,
                'location': meeting.location,
                'google_meet_link': meeting.google_meet_link,
                'google_event_id': meeting.google_event_id,
                'meeting_type': meeting.meeting_type,
                'status': meeting.status,
                'priority': meeting.priority,
                'agenda': meeting.agenda,
                'participants': participants,
                'participant_count': len(participants),
                'organizer_name': f"{meeting.organizer.user.first_name} {meeting.organizer.user.last_name}" if meeting.organizer else "Unknown",
                'department': meeting.department.name if meeting.department else "General",
                'created_at': meeting.created_at.isoformat() if meeting.created_at else None
            }
            meeting_list.append(meeting_data)
        
        meeting_manager.close()
        
        return {
            "success": True,
            "search_query": title_query,
            "total_matches": len(meeting_list),
            "meetings": meeting_list
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error searching meetings by title: {str(e)}"}

@mcp.tool()
def search_meetings_by_description(description_query: str) -> Dict[str, Any]:
    """Search meetings by description using partial text matching.
    
    Args:
        description_query: Text to search for in meeting descriptions (case-insensitive)
    
    Returns:
        Dictionary with matching meetings
    """
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        meeting_manager = MeetingManager()
        meetings = meeting_manager.search_meetings_by_description(description_query)
        
        meeting_list = []
        for meeting in meetings:
            participants = meeting_manager.get_meeting_participants(str(meeting.id))
            
            meeting_data = {
                'meeting_id': str(meeting.id),
                'title': meeting.title,
                'description': meeting.description,
                'meeting_datetime': meeting.meeting_datetime.isoformat(),
                'duration_minutes': meeting.duration_minutes,
                'location': meeting.location,
                'google_meet_link': meeting.google_meet_link,
                'google_event_id': meeting.google_event_id,
                'meeting_type': meeting.meeting_type,
                'status': meeting.status,
                'priority': meeting.priority,
                'agenda': meeting.agenda,
                'participants': participants,
                'participant_count': len(participants),
                'organizer_name': f"{meeting.organizer.user.first_name} {meeting.organizer.user.last_name}" if meeting.organizer else "Unknown",
                'department': meeting.department.name if meeting.department else "General",
                'created_at': meeting.created_at.isoformat() if meeting.created_at else None
            }
            meeting_list.append(meeting_data)
        
        meeting_manager.close()
        
        return {
            "success": True,
            "search_query": description_query,
            "total_matches": len(meeting_list),
            "meetings": meeting_list
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error searching meetings by description: {str(e)}"}

@mcp.tool()
def search_meetings(search_query: str) -> Dict[str, Any]:
    """Search meetings by title OR description using partial text matching.
    
    Args:
        search_query: Text to search for in meeting titles or descriptions (case-insensitive)
    
    Returns:
        Dictionary with matching meetings
    """
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        meeting_manager = MeetingManager()
        meetings = meeting_manager.search_meetings(search_query)
        
        meeting_list = []
        for meeting in meetings:
            participants = meeting_manager.get_meeting_participants(str(meeting.id))
            
            meeting_data = {
                'meeting_id': str(meeting.id),
                'title': meeting.title,
                'description': meeting.description,
                'meeting_datetime': meeting.meeting_datetime.isoformat(),
                'duration_minutes': meeting.duration_minutes,
                'location': meeting.location,
                'google_meet_link': meeting.google_meet_link,
                'google_event_id': meeting.google_event_id,
                'meeting_type': meeting.meeting_type,
                'status': meeting.status,
                'priority': meeting.priority,
                'agenda': meeting.agenda,
                'participants': participants,
                'participant_count': len(participants),
                'organizer_name': f"{meeting.organizer.user.first_name} {meeting.organizer.user.last_name}" if meeting.organizer else "Unknown",
                'department': meeting.department.name if meeting.department else "General",
                'created_at': meeting.created_at.isoformat() if meeting.created_at else None
            }
            meeting_list.append(meeting_data)
        
        meeting_manager.close()
        
        return {
            "success": True,
            "search_query": search_query,
            "total_matches": len(meeting_list),
            "meetings": meeting_list
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error searching meetings: {str(e)}"}

if __name__ == "__main__":
    try:
        # Run the MCP server silently - no print statements allowed
        # as they interfere with the MCP protocol communication
        mcp.run()
    except Exception as e:
        # Log errors to stderr (not stdout) if needed
        import sys
        sys.stderr.write(f"FATAL ERROR: Server failed to start: {e}\n")
        import traceback
        traceback.print_exc(file=sys.stderr)
        exit(1)
