"""Hospital Management System Multi-Agent MCP Server"""

import json
import os
import random
import sys
import traceback
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Optional
import uvicorn

from sqlalchemy.orm import Session
from sqlalchemy import Date, text
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

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
    print("WARNING: Database modules not available. Install dependencies: pip install sqlalchemy psycopg2-binary")

# Import multi-agent system
try:
    from agents.orchestrator_agent import OrchestratorAgent
    MULTI_AGENT_AVAILABLE = True
except ImportError:
    MULTI_AGENT_AVAILABLE = False
    print("WARNING: Multi-agent system not available")

# Initialize FastMCP server
mcp = FastMCP("hospital-management-system-multi-agent")

# Initialize orchestrator agent
orchestrator = None
if MULTI_AGENT_AVAILABLE:
    try:
        orchestrator = OrchestratorAgent()
        print("🤖 Multi-agent system initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize multi-agent system: {str(e)}")
        MULTI_AGENT_AVAILABLE = False

# Database helper functions (kept for backward compatibility)
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
# MULTI-AGENT SYSTEM TOOLS
# ================================

@mcp.tool()
def get_system_status() -> Dict[str, Any]:
    """Get comprehensive system status from the orchestrator."""
    if not MULTI_AGENT_AVAILABLE or not orchestrator:
        return {"error": "Multi-agent system not available"}
    
    try:
        if hasattr(orchestrator, 'get_system_status'):
            return orchestrator.get_system_status()
        else:
            # Fallback: provide basic system status
            return {
                "success": True,
                "status": "operational",
                "database": "connected" if DATABASE_AVAILABLE else "disconnected",
                "multi_agent": "active",
                "agents_count": len(orchestrator.agents),
                "total_tools": len(orchestrator.get_tools()) if hasattr(orchestrator, 'get_tools') else 0,
                "agents": {name: {
                    "status": "active",
                    "tools_count": len(agent.get_tools()) if hasattr(agent, 'get_tools') else 0
                } for name, agent in orchestrator.agents.items()}
            }
    except Exception as e:
        return {"error": f"Failed to get system status: {str(e)}"}

@mcp.tool()
def get_agent_info(agent_name: str = None) -> Dict[str, Any]:
    """Get information about agents in the system."""
    if not MULTI_AGENT_AVAILABLE or not orchestrator:
        return {"error": "Multi-agent system not available"}
    
    try:
        if hasattr(orchestrator, 'get_agent_info'):
            return orchestrator.get_agent_info(agent_name)
        else:
            # Fallback: provide basic agent information
            agents_info = {}
            for name, agent in orchestrator.agents.items():
                agents_info[name] = {
                    "name": agent.agent_name,
                    "description": f"{agent.agent_name} handles {agent.agent_name.lower()}-related operations",
                    "tools_count": len(agent.get_tools()) if hasattr(agent, 'get_tools') else 0,
                    "status": "active"
                }
            
            if agent_name:
                return agents_info.get(agent_name, {"error": f"Agent '{agent_name}' not found"})
            else:
                return {
                    "total_agents": len(agents_info),
                    "agents": agents_info
                }
    except Exception as e:
        return {"error": f"Failed to get agent info: {str(e)}"}

@mcp.tool()
def list_agents() -> Dict[str, Any]:
    """List all available agents in the multi-agent system."""
    if not MULTI_AGENT_AVAILABLE or not orchestrator:
        return {"error": "Multi-agent system not available"}
    
    try:
        agents_list = []
        for name, agent in orchestrator.agents.items():
            agents_list.append({
                "name": agent.agent_name,
                "description": f"Handles {agent.agent_name.lower()}-related hospital operations",
                "tools_count": len(agent.get_tools()) if hasattr(agent, 'get_tools') else 0
            })
        
        return {
            "success": True,
            "total_agents": len(agents_list),
            "agents": agents_list
        }
    except Exception as e:
        return {"error": f"Failed to list agents: {str(e)}"}

@mcp.tool()
def execute_workflow(workflow_name: str, workflow_params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute complex multi-agent workflows."""
    if not MULTI_AGENT_AVAILABLE or not orchestrator:
        return {"error": "Multi-agent system not available"}
    
    try:
        return orchestrator.execute_workflow(workflow_name, workflow_params)
    except Exception as e:
        return {"error": f"Failed to execute workflow: {str(e)}"}

# ================================
# USER MANAGEMENT TOOLS
# ================================

@mcp.tool()
def create_user(username: str, email: str, password_hash: str, role: str, 
                first_name: str, last_name: str, phone: str = None) -> Dict[str, Any]:
    """Create a new user in the database."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("create_user", 
                                           username=username, email=email, password_hash=password_hash,
                                           role=role, first_name=first_name, last_name=last_name, phone=phone)
        return result.get("result", result)
    
    # Fallback to direct implementation if multi-agent not available
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    
    try:
        db = get_db_session()
        user = User(
            username=username, email=email, password_hash=password_hash, role=role,
            first_name=first_name, last_name=last_name, phone=phone
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
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("get_user_by_id", user_id=user_id)
        return result.get("result", result)
    
    # Fallback implementation
    if not DATABASE_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        db = get_db_session()
        user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
        result = serialize_model(user) if user else None
        db.close()
        return {"data": result} if result else {"error": "User not found"}
    except Exception as e:
        return {"error": f"Failed to get user: {str(e)}"}

@mcp.tool()
def list_users() -> Dict[str, Any]:
    """List all users in the database."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("list_users")
        return result.get("result", result)
    
    # Fallback implementation
    if not DATABASE_AVAILABLE:
        return {"error": "Database not available"}
    
    try:
        db = get_db_session()
        users = db.query(User).all()
        result = [serialize_model(user) for user in users]
        db.close()
        return {"data": result}
    except Exception as e:
        return {"error": f"Failed to list users: {str(e)}"}

@mcp.tool()
def update_user(user_id: str, username: str = None, email: str = None, role: str = None,
               first_name: str = None, last_name: str = None, phone: str = None, 
               is_active: bool = None) -> Dict[str, Any]:
    """Update user information."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("update_user", 
                                           user_id=user_id, username=username, email=email, role=role,
                                           first_name=first_name, last_name=last_name, phone=phone, is_active=is_active)
        return result.get("result", result)
    
    # Fallback implementation would go here
    return {"success": False, "message": "Multi-agent system required for this operation"}

@mcp.tool()
def delete_user(user_id: str) -> Dict[str, Any]:
    """Delete a user from the database."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("delete_user", user_id=user_id)
        return result.get("result", result)
    
    return {"success": False, "message": "Multi-agent system required for this operation"}

# ================================
# PATIENT MANAGEMENT TOOLS
# ================================

@mcp.tool()
def create_patient(first_name: str, last_name: str, date_of_birth: str,
                  gender: str = None, phone: str = None, email: str = None,
                  address: str = None, emergency_contact_name: str = None,
                  emergency_contact_phone: str = None, blood_type: str = None,
                  allergies: str = None, medical_history: str = None) -> Dict[str, Any]:
    """Create a new patient record."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("create_patient",
                                           first_name=first_name, last_name=last_name, date_of_birth=date_of_birth,
                                           gender=gender, phone=phone, email=email, address=address,
                                           emergency_contact_name=emergency_contact_name,
                                           emergency_contact_phone=emergency_contact_phone,
                                           blood_type=blood_type, allergies=allergies, medical_history=medical_history)
        return result.get("result", result)
    
    return {"success": False, "message": "Multi-agent system required for this operation"}

@mcp.tool()
def list_patients() -> Dict[str, Any]:
    """List all patients."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("list_patients")
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

@mcp.tool()
def get_patient_by_id(patient_id: str) -> Dict[str, Any]:
    """Get a patient by ID."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("get_patient_by_id", patient_id=patient_id)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

@mcp.tool()
def search_patients(patient_number: str = None, first_name: str = None, 
                   last_name: str = None, phone: str = None, email: str = None) -> Dict[str, Any]:
    """Search for patients by various criteria."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("search_patients",
                                           patient_number=patient_number, first_name=first_name,
                                           last_name=last_name, phone=phone, email=email)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

# ================================
# DEPARTMENT MANAGEMENT TOOLS
# ================================

@mcp.tool()
def create_department(name: str, description: str = None, head_doctor_id: str = None,
                     floor_number: int = None, phone: str = None, email: str = None) -> Dict[str, Any]:
    """Create a new department."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("create_department",
                                           name=name, description=description, head_doctor_id=head_doctor_id,
                                           floor_number=floor_number, phone=phone, email=email)
        return result.get("result", result)
    # Direct DB fallback
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
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("list_departments")
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

@mcp.tool()
def get_department_by_id(department_id: str) -> Dict[str, Any]:
    """Get a department by ID."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("get_department_by_id", department_id=department_id)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

# ================================
# ROOM & BED MANAGEMENT TOOLS
# ================================

@mcp.tool()
def create_room(room_number: str, department_id: str, room_type: str = None,
               floor_number: int = None, capacity: int = None, status: str = "available") -> Dict[str, Any]:
    """Create a new room."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("create_room",
                                           room_number=room_number, department_id=department_id,
                                           room_type=room_type, floor_number=floor_number, 
                                           capacity=capacity, status=status)
        return result.get("result", result)
    # Direct DB fallback
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
def list_rooms(department_id: str = None, status: str = None) -> Dict[str, Any]:
    """List rooms with optional filtering."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("list_rooms", department_id=department_id, status=status)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

@mcp.tool()
def create_bed(bed_number: str, room_id: str, bed_type: str = None, status: str = "available") -> Dict[str, Any]:
    """Create a new bed."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("create_bed",
                                           bed_number=bed_number, room_id=room_id,
                                           bed_type=bed_type, status=status)
        return result.get("result", result)
    # Direct DB fallback
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
def list_beds(status: str = None, room_id: str = None) -> Dict[str, Any]:
    """List beds with optional filtering."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("list_beds", status=status, room_id=room_id)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

@mcp.tool()
def assign_bed_to_patient(bed_id: str, patient_id: str, admission_date: str = None) -> Dict[str, Any]:
    """Assign a bed to a patient."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("assign_bed_to_patient",
                                           bed_id=bed_id, patient_id=patient_id, admission_date=admission_date)
        return result.get("result", result)
    
    return {"success": False, "message": "Multi-agent system required for this operation"}

@mcp.tool()
def discharge_bed(bed_id: str, discharge_date: str = None) -> Dict[str, Any]:
    """Discharge a patient from a bed."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("discharge_bed", bed_id=bed_id, discharge_date=discharge_date)
        return result.get("result", result)
    
    return {"success": False, "message": "Multi-agent system required for this operation"}

# ================================
# STAFF MANAGEMENT TOOLS
@mcp.tool()
def create_equipment(equipment_id: str, name: str, category_id: str, model: str = None,
                    manufacturer: str = None, serial_number: str = None, purchase_date: str = None,
                    warranty_expiry: str = None, location: str = None, department_id: str = None,
                    cost: float = None) -> Dict[str, Any]:
    """Create a new equipment item."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("create_equipment",
                                           equipment_id=equipment_id, name=name, category_id=category_id,
                                           model=model, manufacturer=manufacturer, serial_number=serial_number,
                                           purchase_date=purchase_date, warranty_expiry=warranty_expiry,
                                           location=location, department_id=department_id, cost=cost)
        return result.get("result", result)
    # Direct DB fallback
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
def create_supply(item_code: str, name: str, category_id: str, unit_of_measure: str,
                 description: str = None, minimum_stock_level: int = 0, maximum_stock_level: int = None,
                 current_stock: int = 0, unit_cost: float = None, supplier: str = None,
                 expiry_date: str = None, location: str = None) -> Dict[str, Any]:
    """Create a new supply item."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("create_supply",
                                           item_code=item_code, name=name, category_id=category_id,
                                           unit_of_measure=unit_of_measure, description=description,
                                           minimum_stock_level=minimum_stock_level, maximum_stock_level=maximum_stock_level,
                                           current_stock=current_stock, unit_cost=unit_cost, supplier=supplier,
                                           expiry_date=expiry_date, location=location)
        return result.get("result", result)
    # Direct DB fallback
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
# ================================

@mcp.tool()
def create_staff(user_id: str, employee_id: str, department_id: str, position: str,
                hire_date: str = None, salary: float = None, status: str = "active") -> Dict[str, Any]:
    """Create a new staff record."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("create_staff",
                                           user_id=user_id, employee_id=employee_id, department_id=department_id,
                                           position=position, hire_date=hire_date, salary=salary, status=status)
        return result.get("result", result)
    # Direct DB fallback
    if not DATABASE_AVAILABLE:
        return {"success": False, "message": "Database not available"}
    try:
        db = get_db_session()
        staff = Staff(
            user_id=uuid.UUID(user_id),
            employee_id=employee_id,
            department_id=uuid.UUID(department_id),
            position=position,
            hire_date=datetime.strptime(hire_date, "%Y-%m-%d").date() if hire_date else date.today(),
            salary=Decimal(str(salary)) if salary else None,
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
def list_staff(department_id: str = None, status: str = None, position: str = None) -> Dict[str, Any]:
    """List staff with optional filtering."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("list_staff",
                                           department_id=department_id, status=status, position=position)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

@mcp.tool()
def get_staff_by_id(staff_id: str) -> Dict[str, Any]:
    """Get a staff member by ID."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("get_staff_by_id", staff_id=staff_id)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

@mcp.tool()
def update_staff(staff_id: str, employee_id: str = None, department_id: str = None,
                position: str = None, salary: float = None, status: str = None) -> Dict[str, Any]:
    """Update staff information (supports both UUID and employee_id)."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("update_staff",
                                           staff_id=staff_id, employee_id=employee_id,
                                           department_id=department_id, position=position,
                                           salary=salary, status=status)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

@mcp.tool()
def update_staff_status(staff_id: str, status: str, notes: str = None) -> Dict[str, Any]:
    """Update staff status (active, inactive, on_leave, terminated)."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("update_staff_status",
                                           staff_id=staff_id, status=status, notes=notes)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

# Continue with remaining tools...
# [The file would continue with all other tools following the same pattern]

# ================================
# MEDICAL DOCUMENT MANAGEMENT TOOLS  
# ================================

@mcp.tool()
def upload_medical_document(patient_id: str, file_content: str, file_name: str, 
                          document_type: str = "prescription", mime_type: str = None) -> Dict[str, Any]:
    """Upload a medical document for a patient."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("upload_medical_document",
                                           patient_id=patient_id, file_content=file_content,
                                           file_name=file_name, document_type=document_type, 
                                           mime_type=mime_type)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

@mcp.tool()
def process_medical_document(document_id: str) -> Dict[str, Any]:
    """Process uploaded medical document with OCR and AI extraction."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("process_medical_document", document_id=document_id)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

@mcp.tool()
def get_patient_medical_history(patient_id: str) -> Dict[str, Any]:
    """Get comprehensive medical history for a patient from uploaded documents."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("get_patient_medical_history", patient_id=patient_id)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

@mcp.tool()
def search_medical_documents(patient_id: str = None, document_type: str = None, 
                           date_from: str = None, date_to: str = None) -> Dict[str, Any]:
    """Search medical documents with filters."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("search_medical_documents",
                                           patient_id=patient_id, document_type=document_type,
                                           date_from=date_from, date_to=date_to)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

@mcp.tool()
def query_medical_knowledge(query: str, patient_id: str = None) -> Dict[str, Any]:
    """Query medical documents using RAG system for intelligent answers."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("query_medical_knowledge", 
                                           query=query, patient_id=patient_id)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

@mcp.tool()
def extract_medical_entities(text: str) -> Dict[str, Any]:
    """Extract medical entities from text using AI."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("extract_medical_entities", text=text)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

@mcp.tool()
def get_medical_timeline(patient_id: str) -> Dict[str, Any]:
    """Get chronological medical timeline for a patient."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("get_medical_timeline", patient_id=patient_id)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for this operation"}

# ================================
# MEETING SCHEDULING TOOLS
# ================================

@mcp.tool()
def schedule_meeting(query: str) -> Dict[str, Any]:
    """Schedule a meeting using natural language.
    
    Args:
        query: Natural language description of the meeting to schedule
               (e.g., "Schedule a patient consultation with Dr. Smith tomorrow at 2 PM")
    """
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("schedule_meeting", query=query)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for meeting scheduling"}

@mcp.tool()
def list_meetings(date_str: str = None, days_ahead: int = 7) -> Dict[str, Any]:
    """List meetings with optional date filter.
    
    Args:
        date_str: Specific date in YYYY-MM-DD format (optional)
        days_ahead: Number of days ahead to look for upcoming meetings (default 7)
    """
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("list_meetings",
                                           date_str=date_str,
                                           days_ahead=days_ahead)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for listing meetings"}

@mcp.tool()
def get_meeting_by_id(meeting_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific meeting.
    
    Args:
        meeting_id: The ID of the meeting to retrieve
    """
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("get_meeting_by_id", meeting_id=meeting_id)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for meeting retrieval"}

@mcp.tool()
def update_meeting_status(meeting_id: str, status: str) -> Dict[str, Any]:
    """Update the status of a meeting.
    
    Args:
        meeting_id: The ID of the meeting to update
        status: New status (scheduled, in_progress, completed, cancelled)
    """
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("update_meeting_status",
                                           meeting_id=meeting_id,
                                           status=status)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for meeting updates"}

@mcp.tool()
def add_meeting_notes(meeting_id: str, notes: str, action_items: str = None) -> Dict[str, Any]:
    """Add notes to a meeting.
    
    Args:
        meeting_id: The ID of the meeting
        notes: The notes to add
        action_items: Optional action items from the meeting
    """
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("add_meeting_notes",
                                           meeting_id=meeting_id,
                                           notes=notes,
                                           action_items=action_items)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for adding meeting notes"}

@mcp.tool()
def send_email(to_emails: str, subject: str, message: str, from_name: str = "Hospital Management System") -> Dict[str, Any]:
    """Send email notifications to staff members.
    
    Args:
        to_emails: Comma-separated list of email addresses
        subject: Email subject line
        message: Email message content
        from_name: Sender name (default: Hospital Management System)
    """
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from dotenv import load_dotenv
        import os
        
        # Load email configuration
        load_dotenv()
        
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        email_username = os.getenv('EMAIL_USERNAME')
        email_password = os.getenv('EMAIL_PASSWORD')
        from_email = os.getenv('EMAIL_FROM_ADDRESS', email_username)
        
        if not email_username or not email_password:
            return {"success": False, "message": "Email credentials not configured"}
        
        # Parse email addresses
        email_list = [email.strip() for email in to_emails.split(',')]
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = f"{from_name} <{from_email}>"
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        
        # Send emails
        sent_count = 0
        failed_emails = []
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_username, email_password)
            
            for email_addr in email_list:
                try:
                    msg['To'] = email_addr
                    server.send_message(msg)
                    sent_count += 1
                except Exception as e:
                    failed_emails.append(f"{email_addr}: {str(e)}")
                finally:
                    del msg['To']  # Remove for next iteration
        
        return {
            "success": True,
            "message": f"Sent {sent_count}/{len(email_list)} emails successfully",
            "sent_count": sent_count,
            "total_emails": len(email_list),
            "failed_emails": failed_emails
        }
        
    except Exception as e:
        return {"success": False, "message": f"Email sending failed: {str(e)}"}

# ================================
# DISCHARGE REPORT TOOLS
# ================================

@mcp.tool()
def generate_discharge_report(
    bed_id: str,
    discharge_condition: str = "stable",
    discharge_destination: str = "home"
) -> Dict[str, Any]:
    """Generate a comprehensive patient discharge report.
    
    Args:
        bed_id: The bed ID where the patient is located
        discharge_condition: Condition of patient at discharge (default: stable)
        discharge_destination: Where patient is going (default: home)
    """
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("generate_discharge_report",
                                           bed_id=bed_id,
                                           discharge_condition=discharge_condition,
                                           discharge_destination=discharge_destination)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for discharge report generation"}

@mcp.tool()
def add_treatment_record_simple(
    patient_id: str,
    doctor_id: str,
    treatment_type: str,
    treatment_name: str
) -> Dict[str, Any]:
    """Add a simple treatment record for discharge reporting.
    
    Args:
        patient_id: The ID of the patient
        doctor_id: The ID of the doctor who provided treatment
        treatment_type: Type of treatment
        treatment_name: Name of the treatment
    """
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("add_treatment_record_simple",
                                           patient_id=patient_id,
                                           doctor_id=doctor_id,
                                           treatment_type=treatment_type,
                                           treatment_name=treatment_name)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for adding treatment records"}

@mcp.tool()
def add_equipment_usage_simple(
    patient_id: str,
    equipment_id: str,
    staff_id: str,
    purpose: str
) -> Dict[str, Any]:
    """Add equipment usage record for discharge reporting.
    
    Args:
        patient_id: The ID of the patient
        equipment_id: The ID of the equipment used
        staff_id: The ID of the staff member who used the equipment
        purpose: Purpose of equipment usage
    """
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("add_equipment_usage_simple",
                                           patient_id=patient_id,
                                           equipment_id=equipment_id,
                                           staff_id=staff_id,
                                           purpose=purpose)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for adding equipment usage records"}

@mcp.tool()
def assign_staff_to_patient_simple(
    patient_id: str,
    staff_id: str,
    role: str
) -> Dict[str, Any]:
    """Assign staff to patient for discharge reporting.
    
    Args:
        patient_id: The ID of the patient
        staff_id: The ID of the staff member
        role: Role of staff member in patient care
    """
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("assign_staff_to_patient_simple",
                                           patient_id=patient_id,
                                           staff_id=staff_id,
                                           role=role)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for staff assignment"}

@mcp.tool()
def complete_equipment_usage_simple(usage_id: str) -> Dict[str, Any]:
    """Complete equipment usage record.
    
    Args:
        usage_id: The ID of the equipment usage record to complete
    """
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("complete_equipment_usage_simple", usage_id=usage_id)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for completing equipment usage"}

@mcp.tool()
def list_discharge_reports(patient_id: str = None) -> Dict[str, Any]:
    """List discharge reports.
    
    Args:
        patient_id: Filter by patient ID (optional)
    """
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("list_discharge_reports", patient_id=patient_id)
        return result.get("result", result)
    
    return {"error": "Multi-agent system required for listing discharge reports"}

@mcp.tool()
def download_discharge_report(report_number: str, download_format: str = "pdf") -> Dict[str, Any]:
    """Download a discharge report in the specified format.
    
    Args:
        report_number: The report number to download
        download_format: Format for download - "pdf", "markdown", or "zip" (default: pdf)
    """
    try:
        from report_manager import download_discharge_report as download_report_func
        result = download_report_func(report_number, format=download_format)  # Fix parameter name
        return result
    except Exception as e:
        return {"success": False, "error": str(e), "message": f"Failed to download report: {str(e)}"}

@mcp.tool()
def get_discharge_report_storage_stats() -> Dict[str, Any]:
    """Get storage statistics for discharge reports system."""
    try:
        from report_manager import ReportManager
        manager = ReportManager()
        result = manager.get_storage_stats()
        return result
    except Exception as e:
        return {"success": False, "error": str(e), "message": f"Failed to get storage stats: {str(e)}"}

@mcp.tool()
def list_available_discharge_reports(status: str = "all", patient_name: str = None, 
                                   from_date: str = None, to_date: str = None, 
                                   limit: int = 50) -> Dict[str, Any]:
    """List available discharge reports with filtering options.
    
    Args:
        status: Report status filter - "current", "archived", or "all" (default: all)
        patient_name: Filter by patient name (partial match, optional)
        from_date: Start date filter in YYYY-MM-DD format (optional)
        to_date: End date filter in YYYY-MM-DD format (optional)
        limit: Maximum number of reports to return (default: 50)
    """
    try:
        from report_manager import ReportManager
        manager = ReportManager()
        reports = manager.list_reports(
            status=status, 
            patient_name=patient_name,
            from_date=from_date, 
            to_date=to_date, 
            limit=limit
        )
        return {"success": True, "data": reports, "count": len(reports)}
    except Exception as e:
        return {"success": False, "error": str(e), "message": f"Failed to list reports: {str(e)}"}

@mcp.tool()
def archive_old_discharge_reports(days_old: int = 30) -> Dict[str, Any]:
    """Archive discharge reports older than specified days.
    
    Args:
        days_old: Reports older than this many days will be archived (default: 30)
    """
    try:
        from report_manager import ReportManager
        manager = ReportManager()
        result = manager.archive_old_reports(days_old)
        return result
    except Exception as e:
        return {"success": False, "error": str(e), "message": f"Failed to archive reports: {str(e)}"}

# ================================
# HTTP ENDPOINTS FOR FRONTEND
# ================================

# Define request model for tool calls
from pydantic import BaseModel
from fastapi import HTTPException, Request, Response
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse

class ToolCallRequest(BaseModel):
    method: str
    id: int
    jsonrpc: str = "2.0"
    params: dict

# Tool call endpoint handler
async def call_tool_http(request: Request):
    try:
        data = await request.json()
        tool_name = data.get("params", {}).get("name")
        arguments = data.get("params", {}).get("arguments", {})
        
        if not tool_name:
            raise HTTPException(status_code=400, detail="Tool name is required")
        
        # System-level tools that should not be routed through orchestrator
        system_tools = ["get_system_status", "get_agent_info", "list_agents", "execute_workflow", 
                       "download_discharge_report", "get_discharge_report_storage_stats", 
                       "list_available_discharge_reports", "archive_old_discharge_reports"]
        
        if tool_name in system_tools:
            # Handle system tools directly
            if tool_name == "get_system_status":
                result = get_system_status()
            elif tool_name == "get_agent_info":
                result = get_agent_info(**arguments)
            elif tool_name == "list_agents":
                result = list_agents()
            elif tool_name == "execute_workflow":
                result = execute_workflow(**arguments)
            elif tool_name == "download_discharge_report":
                result = download_discharge_report(**arguments)
            elif tool_name == "get_discharge_report_storage_stats":
                result = get_discharge_report_storage_stats(**arguments)
            elif tool_name == "list_available_discharge_reports":
                result = list_available_discharge_reports(**arguments)
            elif tool_name == "archive_old_discharge_reports":
                result = archive_old_discharge_reports(**arguments)
            else:
                result = {"error": f"System tool {tool_name} not implemented"}
        else:
            # Try to execute through orchestrator for other tools
            if MULTI_AGENT_AVAILABLE and orchestrator:
                try:
                    result = orchestrator.route_request(tool_name, **arguments)
                except Exception as agent_error:
                    print(f"⚠️ Agent routing failed for {tool_name}: {agent_error}")
                    # Fall through to direct tool execution
                    result = {"error": f"Agent routing failed: {str(agent_error)}"}
            else:
                result = {"error": "Multi-agent system not available"}
        
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": data.get("id", 1),
            "result": {
                "content": [{"type": "text", "text": json.dumps(result) if not isinstance(result, str) else result}]
            }
        })
        
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": data.get("id", 1),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }, status_code=500)

# List tools endpoint handler
async def list_tools_http(request: Request):
    try:
        tools_list = []
        
        # Get tools from orchestrator if available
        if MULTI_AGENT_AVAILABLE and orchestrator:
            orchestrator_tools = orchestrator.get_tools()
            
            # Handle if get_tools() returns a list or dict
            if isinstance(orchestrator_tools, list):
                for tool_name in orchestrator_tools:
                    tools_list.append({
                        "name": tool_name,
                        "description": f"Multi-agent tool: {tool_name}"
                    })
            elif isinstance(orchestrator_tools, dict):
                for tool_name, tool_info in orchestrator_tools.items():
                    tools_list.append({
                        "name": tool_name,
                        "description": tool_info.get("description", "Multi-agent tool")
                    })
        else:
            # Fallback: get tools from mcp server registry
            # FastMCP stores tools in the registry
            if hasattr(mcp, '_tools'):
                for tool in mcp._tools:
                    tools_list.append({
                        "name": tool.name,
                        "description": tool.description or "No description available"
                    })
            elif hasattr(mcp, 'registry') and hasattr(mcp.registry, 'tools'):
                for tool_name, tool in mcp.registry.tools.items():
                    tools_list.append({
                        "name": tool_name,
                        "description": getattr(tool, 'description', "No description available")
                    })
        
        return JSONResponse({
            "jsonrpc": "2.0",
            "result": {
                "tools": tools_list
            }
        })
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Failed to list tools: {str(e)}"
            }
        }, status_code=500)

# Health check endpoint handler
async def health_check(request: Request):
    try:
        db_status = "connected" if DATABASE_AVAILABLE else "disconnected"
        agent_status = "active" if MULTI_AGENT_AVAILABLE and orchestrator else "inactive"
        
        return JSONResponse({
            "status": "healthy",
            "database": db_status,
            "server": "running",
            "multi_agent": agent_status,
            "agents_count": len(orchestrator.agents) if orchestrator else 0,
            "tools_count": len(orchestrator.get_tools()) if orchestrator else len(mcp.tools)
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

if __name__ == "__main__":
    import uvicorn
    
    print("🏥 Starting Hospital Management System Multi-Agent MCP Server...")
    print(f"📊 Multi-agent system: {'✅ Available' if MULTI_AGENT_AVAILABLE else '❌ Not available'}")
    print(f"🗃️ Database: {'✅ Available' if DATABASE_AVAILABLE else '❌ Not available'}")
    
    if MULTI_AGENT_AVAILABLE and orchestrator:
        print(f"🤖 Agents initialized: {len(orchestrator.agents)}")
        print(f"🔧 Total tools available: {len(orchestrator.get_tools())}")
    
    try:
        import uvicorn
        
        # Get the SSE app from FastMCP
        app = mcp.sse_app()
        
        print("📡 Starting MCP server with HTTP/SSE support...")
        print("   Server will be available at: http://0.0.0.0:8000")
        print("   Health check: http://0.0.0.0:8000/health")
        
        # Add custom routes to the Starlette app
        import os
        reports_dir = os.path.join(os.path.dirname(__file__), "reports", "discharge")
        
        custom_routes = [
            Route("/tools/call", call_tool_http, methods=["POST"]),
            Route("/tools/list", list_tools_http, methods=["GET"]),
            Route("/health", health_check, methods=["GET"]),
            Mount("/discharge", StaticFiles(directory=reports_dir), name="static"),
        ]
        
        # Add routes to existing app
        app.routes.extend(custom_routes)
        
        # Add CORS middleware for frontend communication
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:3000", "http://127.0.0.1:3000",
                "http://localhost:5173", "http://127.0.0.1:5173"
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        print("📡 Added custom HTTP endpoints:")
        print("   POST /tools/call - Call MCP tools via HTTP")
        print("   GET /tools/list - List available tools")
        print("   GET /health - Health check")
        
        # Run with uvicorn - bind to 0.0.0.0 for Docker container access
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
    except Exception as e:
        import sys
        sys.stderr.write(f"FATAL ERROR: Server failed to start: {e}\n")
        import traceback
        traceback.print_exc(file=sys.stderr)
        exit(1)