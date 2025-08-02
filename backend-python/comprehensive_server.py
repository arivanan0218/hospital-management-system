"""Hospital Management System MCP Server - Complete CRUD Operations for All Tables."""

import random
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from mcp.server.fastmcp import FastMCP

# Import database modules
try:
    from database import (
        User, Department, Patient, Room, Bed, Staff, Equipment, EquipmentCategory,
        Supply, SupplyCategory, InventoryTransaction, AgentInteraction, Appointment,
        LegacyUser, SessionLocal
    )
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("⚠️  Database modules not available. Install dependencies: pip install sqlalchemy psycopg2-binary")

# Initialize FastMCP server
mcp = FastMCP("hospital-management-system")

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

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
