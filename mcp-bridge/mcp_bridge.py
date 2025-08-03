"""
MCP Bridge Server - HTTP Gateway for MCP Server

This module provides an HTTP API gateway that directly imports and calls
the MCP tools from comprehensive_server.py without subprocess communication.
"""

import asyncio
import json
import logging
import sys
import uuid
import os
from typing import Any, Dict, List, Optional

import uvicorn
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add the backend-python directory to the Python path
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend-python")
sys.path.insert(0, backend_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPRequest(BaseModel):
    """MCP request model"""
    method: str
    params: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    """MCP response model"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class MCPBridge:
    """Bridge that directly calls MCP tools"""
    
    def __init__(self):
        self.tools = {}
        self.initialized = False
        
    async def initialize(self):
        """Initialize the bridge by importing MCP tools"""
        try:
            # Import the comprehensive server module
            import comprehensive_server
            
            # Manually map all the tool functions
            self.tools = {
                # User operations
                "create_user": comprehensive_server.create_user,
                "get_user_by_id": comprehensive_server.get_user_by_id,
                "list_users": comprehensive_server.list_users,
                "update_user": comprehensive_server.update_user,
                "delete_user": comprehensive_server.delete_user,
                
                # Department operations
                "create_department": comprehensive_server.create_department,
                "list_departments": comprehensive_server.list_departments,
                "get_department_by_id": comprehensive_server.get_department_by_id,
                
                # Patient operations
                "create_patient": comprehensive_server.create_patient,
                "list_patients": comprehensive_server.list_patients,
                "get_patient_by_id": comprehensive_server.get_patient_by_id,
                
                # Room operations
                "create_room": comprehensive_server.create_room,
                "list_rooms": comprehensive_server.list_rooms,
                
                # Bed operations
                "create_bed": comprehensive_server.create_bed,
                "list_beds": comprehensive_server.list_beds,
                "assign_bed_to_patient": comprehensive_server.assign_bed_to_patient,
                "discharge_bed": comprehensive_server.discharge_bed,
                
                # Staff operations
                "create_staff": comprehensive_server.create_staff,
                "list_staff": comprehensive_server.list_staff,
                
                # Equipment operations
                "create_equipment_category": comprehensive_server.create_equipment_category,
                "create_equipment": comprehensive_server.create_equipment,
                "list_equipment": comprehensive_server.list_equipment,
                "update_equipment_status": comprehensive_server.update_equipment_status,
                
                # Supply operations
                "create_supply_category": comprehensive_server.create_supply_category,
                "create_supply": comprehensive_server.create_supply,
                "list_supplies": comprehensive_server.list_supplies,
                "update_supply_stock": comprehensive_server.update_supply_stock,
                
                # Appointment operations
                "create_appointment": comprehensive_server.create_appointment,
                "list_appointments": comprehensive_server.list_appointments,
                
                # Agent interaction logging
                "log_agent_interaction": comprehensive_server.log_agent_interaction,
                
                # Legacy operations
                "create_legacy_user": comprehensive_server.create_legacy_user,
                "list_legacy_users": comprehensive_server.list_legacy_users,
            }
            
            self.initialized = True
            logger.info(f"Successfully loaded {len(self.tools)} tools")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP tools: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool directly"""
        if not self.initialized:
            raise HTTPException(status_code=503, detail="Bridge not initialized")
        
        if tool_name not in self.tools:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        try:
            # Call the tool function directly
            result = self.tools[tool_name](**arguments)
            
            # Handle async tools if needed
            if asyncio.iscoroutine(result):
                result = await result
            
            return result
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        if not self.initialized:
            raise HTTPException(status_code=503, detail="Bridge not initialized")
        
        tools_list = []
        for tool_name, tool_func in self.tools.items():
            tool_info = {
                "name": tool_name,
                "description": getattr(tool_func, '__doc__', 'No description available'),
            }
            tools_list.append(tool_info)
        
        return tools_list

# Global bridge instance
bridge = None

# FastAPI app
app = FastAPI(
    title="Hospital Management System MCP Bridge",
    description="HTTP API bridge for Hospital Management System MCP Server",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize the MCP bridge on startup"""
    global bridge
    
    bridge = MCPBridge()
    await bridge.initialize()
    logger.info("MCP Bridge started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global bridge
    logger.info("MCP Bridge shutting down")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hospital Management System MCP Bridge", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "bridge_active": bridge is not None and bridge.initialized}

@app.get("/tools")
async def list_tools():
    """List all available tools"""
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    try:
        tools = await bridge.list_tools()
        return {"tools": tools, "count": len(tools)}
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, request: Request):
    """Call a specific tool with arguments"""
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    try:
        # Get request body
        body = await request.json() if await request.body() else {}
        
        # Call the tool
        result = await bridge.call_tool(tool_name, body)
        
        return {
            "tool": tool_name,
            "success": True,
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Hospital Management specific endpoints for convenience

@app.post("/users")
async def create_user(request: Request):
    """Create a new user"""
    body = await request.json()
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    result = await bridge.call_tool("create_user", body)
    return result

@app.get("/users")
async def list_users():
    """List all users"""
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    result = await bridge.call_tool("list_users", {})
    return result

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get user by ID"""
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    result = await bridge.call_tool("get_user_by_id", {"user_id": user_id})
    return result

@app.post("/patients")
async def create_patient(request: Request):
    """Create a new patient"""
    body = await request.json()
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    result = await bridge.call_tool("create_patient", body)
    return result

@app.get("/patients")
async def list_patients():
    """List all patients"""
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    result = await bridge.call_tool("list_patients", {})
    return result

@app.get("/patients/{patient_id}")
async def get_patient(patient_id: str):
    """Get patient by ID"""
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    result = await bridge.call_tool("get_patient_by_id", {"patient_id": patient_id})
    return result

@app.post("/departments")
async def create_department(request: Request):
    """Create a new department"""
    body = await request.json()
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    result = await bridge.call_tool("create_department", body)
    return result

@app.get("/departments")
async def list_departments():
    """List all departments"""
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    result = await bridge.call_tool("list_departments", {})
    return result

@app.get("/departments/{department_id}")
async def get_department(department_id: str):
    """Get department by ID"""
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    result = await bridge.call_tool("get_department_by_id", {"department_id": department_id})
    return result

@app.post("/beds")
async def create_bed(request: Request):
    """Create a new bed"""
    body = await request.json()
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    result = await bridge.call_tool("create_bed", body)
    return result

@app.get("/beds")
async def list_beds(status: str = None):
    """List all beds"""
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    params = {"status": status} if status else {}
    result = await bridge.call_tool("list_beds", params)
    return result

@app.post("/beds/{bed_id}/assign")
async def assign_bed(bed_id: str, request: Request):
    """Assign a bed to a patient"""
    body = await request.json()
    body["bed_id"] = bed_id
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    result = await bridge.call_tool("assign_bed_to_patient", body)
    return result

@app.post("/beds/{bed_id}/discharge")
async def discharge_bed(bed_id: str, request: Request):
    """Discharge a patient from a bed"""
    body = await request.json() if await request.body() else {}
    body["bed_id"] = bed_id
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    result = await bridge.call_tool("discharge_bed", body)
    return result

@app.get("/staff")
async def list_staff(department_id: str = None, status: str = None):
    """List all staff members"""
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    params = {}
    if department_id:
        params["department_id"] = department_id
    if status:
        params["status"] = status
    
    result = await bridge.call_tool("list_staff", params)
    return result

@app.get("/equipment")
async def list_equipment(status: str = None, department_id: str = None):
    """List all equipment"""
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    params = {}
    if status:
        params["status"] = status
    if department_id:
        params["department_id"] = department_id
    
    result = await bridge.call_tool("list_equipment", params)
    return result

@app.get("/supplies")
async def list_supplies(low_stock_only: bool = False):
    """List all supplies"""
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    result = await bridge.call_tool("list_supplies", {"low_stock_only": low_stock_only})
    return result

@app.get("/appointments")
async def list_appointments(doctor_id: str = None, patient_id: str = None, date: str = None):
    """List appointments"""
    if not bridge:
        raise HTTPException(status_code=503, detail="Bridge not initialized")
    
    params = {}
    if doctor_id:
        params["doctor_id"] = doctor_id
    if patient_id:
        params["patient_id"] = patient_id
    if date:
        params["date"] = date
    
    result = await bridge.call_tool("list_appointments", params)
    return result

# Claude API Proxy Endpoint
class ClaudeRequest(BaseModel):
    model: str
    max_tokens: int
    messages: List[Dict[str, str]]
    api_key: str
    system: Optional[str] = None

@app.post("/claude")
async def claude_proxy(claude_request: ClaudeRequest):
    """Proxy Claude API requests to avoid CORS issues"""
    try:
        # Prepare the request data for Claude API
        api_data = {
            "model": claude_request.model,
            "max_tokens": claude_request.max_tokens,
            "messages": claude_request.messages
        }
        
        # Add system message if provided
        if claude_request.system:
            api_data["system"] = claude_request.system
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": claude_request.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # Make request to Claude API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                json=api_data,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Claude API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Claude API error: {response.text}"
                )
                
    except httpx.TimeoutException:
        logger.error("Claude API request timeout")
        raise HTTPException(status_code=504, detail="Claude API request timeout")
    except Exception as e:
        logger.error(f"Error calling Claude API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calling Claude API: {str(e)}")

# OpenAI API Proxy Endpoint
class OpenAIRequest(BaseModel):
    model: str
    max_tokens: int
    messages: List[Dict[str, str]]
    api_key: str

@app.post("/openai")
async def openai_proxy(openai_request: OpenAIRequest):
    """Proxy OpenAI API requests to avoid CORS issues"""
    try:
        # Prepare the request data for OpenAI API
        api_data = {
            "model": openai_request.model,
            "max_tokens": openai_request.max_tokens,
            "messages": openai_request.messages
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_request.api_key}"
        }
        
        # Make request to OpenAI API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json=api_data,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"OpenAI API error: {response.text}"
                )
                
    except httpx.TimeoutException:
        logger.error("OpenAI API request timeout")
        raise HTTPException(status_code=504, detail="OpenAI API request timeout")
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calling OpenAI API: {str(e)}")

# Groq API Proxy Endpoint
class GroqRequest(BaseModel):
    model: str
    max_tokens: int
    messages: List[Dict[str, str]]
    api_key: str

@app.post("/groq")
async def groq_proxy(groq_request: GroqRequest):
    """Proxy Groq API requests to avoid CORS issues"""
    try:
        # Prepare the request data for Groq API
        api_data = {
            "model": groq_request.model,
            "max_tokens": groq_request.max_tokens,
            "messages": groq_request.messages
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {groq_request.api_key}"
        }
        
        # Make request to Groq API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=api_data,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Groq API error: {response.text}"
                )
                
    except httpx.TimeoutException:
        logger.error("Groq API request timeout")
        raise HTTPException(status_code=504, detail="Groq API request timeout")
    except Exception as e:
        logger.error(f"Error calling Groq API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calling Groq API: {str(e)}")

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "mcp_bridge:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )
