"""Hospital Management System Multi-Agent MCP Server"""

import random
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
    
    return {"success": False, "message": "Multi-agent system required for this operation"}

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
               capacity: int = None, status: str = "available") -> Dict[str, Any]:
    """Create a new room."""
    if MULTI_AGENT_AVAILABLE and orchestrator:
        result = orchestrator.route_request("create_room",
                                           room_number=room_number, department_id=department_id,
                                           room_type=room_type, capacity=capacity, status=status)
        return result.get("result", result)
    
    return {"success": False, "message": "Multi-agent system required for this operation"}

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
    
    return {"success": False, "message": "Multi-agent system required for this operation"}

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
    
    return {"success": False, "message": "Multi-agent system required for this operation"}

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
# HTTP ENDPOINTS FOR FRONTEND
# ================================

# Define request model for tool calls
from pydantic import BaseModel
from fastapi import HTTPException, Request, Response
from starlette.routing import Route
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
        system_tools = ["get_system_status", "get_agent_info", "list_agents", "execute_workflow"]
        
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
                "content": [{"type": "text", "text": str(result) if not isinstance(result, str) else result}]
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
        custom_routes = [
            Route("/tools/call", call_tool_http, methods=["POST"]),
            Route("/tools/list", list_tools_http, methods=["GET"]),
            Route("/health", health_check, methods=["GET"]),
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
