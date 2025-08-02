"""
ChatGPT-like Server for Hospital Management System
Connects the React frontend to MCP Hospital Management Tools
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Import the hospital management client
from client import HospitalManagementClient


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hospital Management ChatBot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global MCP client instance
hospital_client: Optional[HospitalManagementClient] = None


class ChatMessage(BaseModel):
    message: str
    timestamp: str = None
    user_id: str = "user"


class ChatResponse(BaseModel):
    response: str
    timestamp: str
    type: str = "text"  # text, data, error
    data: Optional[Dict[Any, Any]] = None


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


class HospitalChatBot:
    """Intelligent ChatBot that processes natural language queries and executes hospital management tasks."""
    
    def __init__(self):
        self.client = None
        self.conversation_history = []
        
    async def initialize(self):
        """Initialize the MCP client connection."""
        try:
            self.client = HospitalManagementClient()
            # We'll connect during the first request to avoid startup delays
            logger.info("ChatBot initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize ChatBot: {e}")
            return False
    
    async def ensure_connection(self):
        """Ensure MCP client is connected."""
        if not self.client:
            await self.initialize()
        
        # Only connect if not already connected
        if not hasattr(self.client, 'session') or not self.client.session:
            try:
                # Initialize the connection using the same method as in client.py
                from mcp import ClientSession, StdioServerParameters
                from mcp.client.stdio import stdio_client
                import sys
                import os
                
                # Get the server script path
                current_dir = os.path.dirname(os.path.abspath(__file__))
                server_script = os.path.join(current_dir, "comprehensive_server.py")
                
                # Create stdio client
                server_params = StdioServerParameters(
                    command=sys.executable,
                    args=[server_script],
                    env=None
                )
                
                self.client.stdio_context = stdio_client(server_params)
                session = await self.client.stdio_context.__aenter__()
                self.client.session = session
                
                # Initialize session
                await session.initialize()
                
                logger.info("MCP client connected successfully")
            except Exception as e:
                logger.error(f"Failed to connect MCP client: {e}")
                # Create a fallback response instead of raising an exception
                return False
        return True
    
    async def process_message(self, message: str) -> ChatResponse:
        """Process user message and return appropriate response."""
        try:
            connected = await self.ensure_connection()
            
            if not connected:
                return ChatResponse(
                    response="🔧 **Hospital Management System**\n\nI'm currently unable to connect to the MCP server. However, I can still help you with:\n\n• **General Information** - Hospital management guidance\n• **Documentation** - System capabilities and features\n• **Troubleshooting** - Setup and configuration help\n\nTo access full functionality, please ensure:\n1. MCP server is running (`python server.py`)\n2. All dependencies are installed\n3. No port conflicts on 8080\n\nHow can I assist you today?",
                    timestamp=datetime.now().isoformat(),
                    type="text"
                )
            
            # Store the conversation
            self.conversation_history.append({
                "user": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Analyze user intent and execute appropriate actions
            response = await self._analyze_and_execute(message)
            
            # Store bot response
            self.conversation_history.append({
                "bot": response.response,
                "timestamp": datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return ChatResponse(
                response=f"I apologize, but I encountered an error: {str(e)}\n\nI can still help you with general hospital management questions. What would you like to know?",
                timestamp=datetime.now().isoformat(),
                type="error"
            )
    
    async def _analyze_and_execute(self, message: str) -> ChatResponse:
        """Analyze user message and execute appropriate hospital management actions."""
        message_lower = message.lower()
        
        # Greeting patterns
        if any(greeting in message_lower for greeting in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            return ChatResponse(
                response="Hello! I'm your Hospital Management AI Assistant. I can help you with:\n\n" +
                        "🏥 **Hospital Operations:**\n" +
                        "• Patient management (admission, discharge, records)\n" +
                        "• Bed allocation and management\n" +
                        "• Staff scheduling and management\n" +
                        "• Equipment tracking and maintenance\n" +
                        "• Supply inventory management\n" +
                        "• Appointment scheduling\n\n" +
                        "🤖 **AI Features:**\n" +
                        "• Autonomous hospital management\n" +
                        "• Intelligent resource optimization\n" +
                        "• Predictive analytics\n" +
                        "• Hospital state analysis\n\n" +
                        "Just ask me anything about hospital management, and I'll help you!",
                timestamp=datetime.now().isoformat(),
                type="text"
            )
        
        # Help patterns
        elif any(help_word in message_lower for help_word in ["help", "what can you do", "capabilities"]):
            return await self._show_capabilities()
        
        # Hospital analysis
        elif any(word in message_lower for word in ["analyze", "analysis", "hospital state", "overview", "status"]):
            return await self._analyze_hospital_state()
        
        # Patient management
        elif any(word in message_lower for word in ["patient", "patients", "admission", "admit"]):
            return await self._handle_patient_queries(message)
        
        # Bed management
        elif any(word in message_lower for word in ["bed", "beds", "room", "rooms"]):
            return await self._handle_bed_queries(message)
        
        # Staff management
        elif any(word in message_lower for word in ["staff", "doctor", "nurse", "employee"]):
            return await self._handle_staff_queries(message)
        
        # Equipment management
        elif any(word in message_lower for word in ["equipment", "machine", "device"]):
            return await self._handle_equipment_queries(message)
        
        # Supply management
        elif any(word in message_lower for word in ["supply", "supplies", "inventory", "stock"]):
            return await self._handle_supply_queries(message)
        
        # Appointment management
        elif any(word in message_lower for word in ["appointment", "schedule", "booking"]):
            return await self._handle_appointment_queries(message)
        
        # Autonomous operations
        elif any(word in message_lower for word in ["autonomous", "automatic", "ai management", "optimize"]):
            return await self._handle_autonomous_operations(message)
        
        # Department management
        elif any(word in message_lower for word in ["department", "departments"]):
            return await self._handle_department_queries(message)
        
        # Users management
        elif any(word in message_lower for word in ["user", "users", "account"]):
            return await self._handle_user_queries(message)
        
        else:
            # Default intelligent response
            return ChatResponse(
                response="I understand you're asking about hospital management. Here are some things I can help you with:\n\n" +
                        "• **Analyze hospital state** - Get comprehensive analysis\n" +
                        "• **Patient management** - Add, view, or manage patients\n" +
                        "• **Bed management** - Check availability and allocate beds\n" +
                        "• **Staff operations** - Manage doctors, nurses, and staff\n" +
                        "• **Equipment tracking** - Monitor and maintain equipment\n" +
                        "• **Supply management** - Track inventory and supplies\n" +
                        "• **Autonomous AI** - Let AI optimize hospital operations\n\n" +
                        "Please be more specific about what you'd like to do!",
                timestamp=datetime.now().isoformat(),
                type="text"
            )
    
    async def _show_capabilities(self) -> ChatResponse:
        """Show bot capabilities."""
        capabilities = {
            "AI_Features": [
                "Autonomous hospital management",
                "Intelligent resource optimization", 
                "Predictive analytics",
                "Hospital state analysis"
            ],
            "Patient_Management": [
                "Patient admission and discharge",
                "Medical record management",
                "Patient search and tracking"
            ],
            "Resource_Management": [
                "Bed allocation optimization",
                "Equipment tracking and maintenance",
                "Supply inventory management",
                "Staff scheduling optimization"
            ],
            "Administrative": [
                "Appointment scheduling",
                "Department management",
                "User account management",
                "Reporting and analytics"
            ]
        }
        
        response_text = "🤖 **Hospital Management AI Capabilities:**\n\n"
        for category, features in capabilities.items():
            response_text += f"**{category.replace('_', ' ')}:**\n"
            for feature in features:
                response_text += f"• {feature}\n"
            response_text += "\n"
        
        return ChatResponse(
            response=response_text,
            timestamp=datetime.now().isoformat(),
            type="data",
            data=capabilities
        )
    
    async def _analyze_hospital_state(self) -> ChatResponse:
        """Perform hospital state analysis."""
        try:
            if not hasattr(self.client, 'session') or not self.client.session:
                return ChatResponse(
                    response="📊 **Hospital State Analysis**\n\n⚠️ Unable to connect to MCP server for live data.\n\nTo perform analysis, ensure:\n1. MCP server is running\n2. Database is accessible\n3. All services are connected\n\nI can provide general guidance on:\n• Hospital analytics best practices\n• Key performance indicators\n• Resource optimization strategies\n\nWould you like information on any of these topics?",
                    timestamp=datetime.now().isoformat(),
                    type="text"
                )
            
            analysis = await self.client.analyze_hospital_state()
            
            response_text = f"📊 **Hospital State Analysis:**\n\n"
            response_text += f"👥 **Users:** {analysis['total_users']}\n"
            response_text += f"🏢 **Departments:** {analysis['total_departments']}\n"
            response_text += f"🤒 **Patients:** {analysis['total_patients']}\n"
            response_text += f"🛏️ **Bed Occupancy:** {analysis['bed_occupancy']['percentage']:.1f}%\n"
            response_text += f"   • Available: {analysis['bed_occupancy']['available']}\n"
            response_text += f"   • Occupied: {analysis['bed_occupancy']['occupied']}\n"
            response_text += f"🔧 **Equipment Issues:** {analysis['equipment_status']['issues']}\n"
            response_text += f"📦 **Supply Alerts:** {analysis['supply_alerts']}\n"
            response_text += f"📅 **Appointments:** {analysis['upcoming_appointments']}\n"
            
            if analysis.get('recommendations'):
                response_text += f"\n💡 **AI Recommendations:**\n"
                for i, rec in enumerate(analysis['recommendations'], 1):
                    response_text += f"{i}. {rec}\n"
            
            return ChatResponse(
                response=response_text,
                timestamp=datetime.now().isoformat(),
                type="data",
                data=analysis
            )
        except Exception as e:
            return ChatResponse(
                response=f"Unable to analyze hospital state: {str(e)}\n\nTry checking the connection or ask for general hospital management guidance.",
                timestamp=datetime.now().isoformat(),
                type="error"
            )
    
    async def _handle_patient_queries(self, message: str) -> ChatResponse:
        """Handle patient-related queries."""
        message_lower = message.lower()
        
        if "list" in message_lower or "show" in message_lower or "view" in message_lower:
            return await self._list_patients()
        elif "add" in message_lower or "create" in message_lower or "new" in message_lower:
            return await self._guide_patient_creation()
        elif "admit" in message_lower:
            return await self._guide_patient_admission()
        else:
            return ChatResponse(
                response="I can help you with patient management:\n\n" +
                        "• **View patients** - Say 'show patients' or 'list patients'\n" +
                        "• **Add new patient** - Say 'add patient' or 'create patient'\n" +
                        "• **Intelligent admission** - Say 'admit patient'\n\n" +
                        "What would you like to do?",
                timestamp=datetime.now().isoformat(),
                type="text"
            )
    
    async def _list_patients(self) -> ChatResponse:
        """List all patients."""
        try:
            result = await self.client._safe_call_tool("list_patients", {})
            patients = result.get("patients", [])
            
            if not patients:
                return ChatResponse(
                    response="No patients found in the system.",
                    timestamp=datetime.now().isoformat(),
                    type="text"
                )
            
            response_text = f"👥 **Patients ({len(patients)} total):**\n\n"
            
            for i, patient in enumerate(patients[:10], 1):  # Show first 10
                response_text += f"**{i}. {patient.get('first_name', '')} {patient.get('last_name', '')}**\n"
                response_text += f"   • ID: {patient.get('patient_number', 'N/A')}\n"
                response_text += f"   • DOB: {patient.get('date_of_birth', 'N/A')}\n"
                response_text += f"   • Gender: {patient.get('gender', 'N/A')}\n"
                response_text += f"   • Blood Type: {patient.get('blood_type', 'N/A')}\n\n"
            
            if len(patients) > 10:
                response_text += f"... and {len(patients) - 10} more patients.\n"
            
            return ChatResponse(
                response=response_text,
                timestamp=datetime.now().isoformat(),
                type="data",
                data={"patients": patients}
            )
        except Exception as e:
            return ChatResponse(
                response=f"Unable to retrieve patients: {str(e)}",
                timestamp=datetime.now().isoformat(),
                type="error"
            )
    
    async def _guide_patient_creation(self) -> ChatResponse:
        """Guide user through patient creation."""
        return ChatResponse(
            response="To create a new patient, I need the following information:\n\n" +
                    "**Required:**\n" +
                    "• Patient Number (e.g., P1234)\n" +
                    "• First Name\n" +
                    "• Last Name\n" +
                    "• Date of Birth (YYYY-MM-DD)\n\n" +
                    "**Optional:**\n" +
                    "• Gender\n" +
                    "• Phone\n" +
                    "• Email\n" +
                    "• Address\n" +
                    "• Blood Type\n" +
                    "• Allergies\n" +
                    "• Medical History\n\n" +
                    "Please provide the patient details in this format:\n" +
                    "`Create patient: John Doe, P1234, 1990-01-01, male, 555-1234, john@email.com`",
            timestamp=datetime.now().isoformat(),
            type="text"
        )
    
    async def _guide_patient_admission(self) -> ChatResponse:
        """Guide intelligent patient admission."""
        return ChatResponse(
            response="🏥 **Intelligent Patient Admission**\n\n" +
                    "I can automatically handle patient admission with:\n" +
                    "• Optimal bed assignment\n" +
                    "• Automatic appointment scheduling\n" +
                    "• Supply allocation\n" +
                    "• Department coordination\n\n" +
                    "To admit a patient, provide their details:\n" +
                    "`Admit patient: Jane Smith, P5678, 1985-06-15, female, 555-9876, jane@email.com`\n\n" +
                    "I'll handle the rest automatically!",
            timestamp=datetime.now().isoformat(),
            type="text"
        )
    
    async def _handle_bed_queries(self, message: str) -> ChatResponse:
        """Handle bed-related queries."""
        try:
            result = await self.client._safe_call_tool("list_beds", {})
            beds = result.get("beds", [])
            
            if not beds:
                return ChatResponse(
                    response="🛏️ **Bed Status:**\n\n⚠️ **No beds found in the system.**\n\nTo get started:\n• Add beds through the hospital management interface\n• Configure departments and rooms first\n• Contact your system administrator\n\nOnce beds are added, I can provide detailed availability information.",
                    timestamp=datetime.now().isoformat(),
                    type="text"
                )
            
            available_beds = [b for b in beds if b.get("status") == "available"]
            occupied_beds = [b for b in beds if b.get("status") == "occupied"]
            
            # Calculate occupancy rate safely
            occupancy_rate = (len(occupied_beds) / len(beds) * 100) if len(beds) > 0 else 0
            
            response_text = f"🛏️ **Bed Status:**\n\n"
            response_text += f"**Total Beds:** {len(beds)}\n"
            response_text += f"**Available:** {len(available_beds)}\n"
            response_text += f"**Occupied:** {len(occupied_beds)}\n"
            response_text += f"**Occupancy Rate:** {occupancy_rate:.1f}%\n\n"
            
            if available_beds:
                response_text += "**Available Beds:**\n"
                for bed in available_beds[:5]:
                    response_text += f"• Bed {bed.get('bed_number', 'N/A')} - {bed.get('bed_type', 'Standard')}\n"
                
                if len(available_beds) > 5:
                    response_text += f"... and {len(available_beds) - 5} more available beds.\n"
            else:
                response_text += "⚠️ **No beds currently available.**\n"
            
            if len(occupied_beds) > 0:
                response_text += f"\n**Occupied Beds:** {len(occupied_beds)}\n"
                for bed in occupied_beds[:3]:
                    response_text += f"• Bed {bed.get('bed_number', 'N/A')} - {bed.get('bed_type', 'Standard')}\n"
                
                if len(occupied_beds) > 3:
                    response_text += f"... and {len(occupied_beds) - 3} more occupied beds.\n"
            
            return ChatResponse(
                response=response_text,
                timestamp=datetime.now().isoformat(),
                type="data",
                data={"beds": beds, "available": available_beds, "occupied": occupied_beds}
            )
        except Exception as e:
            return ChatResponse(
                response=f"Unable to retrieve bed information: {str(e)}\n\nThis might be because:\n• The MCP server is not running\n• Database connection issues\n• Network connectivity problems\n\nPlease check the system status and try again.",
                timestamp=datetime.now().isoformat(),
                type="error"
            )
    
    async def _handle_staff_queries(self, message: str) -> ChatResponse:
        """Handle staff-related queries."""
        try:
            result = await self.client._safe_call_tool("list_staff", {})
            staff = result.get("staff", [])
            
            response_text = f"👨‍⚕️ **Staff Overview ({len(staff)} total):**\n\n"
            
            # Group by position
            positions = {}
            for member in staff:
                pos = member.get("position", "Unknown")
                if pos not in positions:
                    positions[pos] = []
                positions[pos].append(member)
            
            for position, members in positions.items():
                response_text += f"**{position.title()}s:** {len(members)}\n"
                for member in members[:3]:  # Show first 3
                    user_id = member.get("user_id")
                    response_text += f"• Staff ID: {member.get('employee_id', 'N/A')}\n"
                response_text += "\n"
            
            return ChatResponse(
                response=response_text,
                timestamp=datetime.now().isoformat(),
                type="data",
                data={"staff": staff, "positions": positions}
            )
        except Exception as e:
            return ChatResponse(
                response=f"Unable to retrieve staff information: {str(e)}",
                timestamp=datetime.now().isoformat(),
                type="error"
            )
    
    async def _handle_equipment_queries(self, message: str) -> ChatResponse:
        """Handle equipment-related queries."""
        try:
            result = await self.client._safe_call_tool("list_equipment", {})
            equipment = result.get("equipment", [])
            
            # Group by status
            status_counts = {}
            for item in equipment:
                status = item.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            response_text = f"🔧 **Equipment Status ({len(equipment)} total):**\n\n"
            
            for status, count in status_counts.items():
                response_text += f"**{status.title()}:** {count}\n"
            
            # Show maintenance needed items
            maintenance_needed = [e for e in equipment if e.get("status") in ["maintenance", "needs_maintenance", "out_of_order"]]
            if maintenance_needed:
                response_text += f"\n⚠️ **Needs Attention ({len(maintenance_needed)}):**\n"
                for item in maintenance_needed[:5]:
                    response_text += f"• {item.get('name', 'Unknown')} - {item.get('status', 'Unknown')}\n"
            
            return ChatResponse(
                response=response_text,
                timestamp=datetime.now().isoformat(),
                type="data",
                data={"equipment": equipment, "status_counts": status_counts}
            )
        except Exception as e:
            return ChatResponse(
                response=f"Unable to retrieve equipment information: {str(e)}",
                timestamp=datetime.now().isoformat(),
                type="error"
            )
    
    async def _handle_supply_queries(self, message: str) -> ChatResponse:
        """Handle supply-related queries."""
        try:
            # Get all supplies
            all_supplies = await self.client._safe_call_tool("list_supplies", {})
            supplies = all_supplies.get("supplies", [])
            
            # Get low stock supplies
            low_stock_result = await self.client._safe_call_tool("list_supplies", {"low_stock_only": True})
            low_stock = low_stock_result.get("supplies", [])
            
            response_text = f"📦 **Supply Inventory ({len(supplies)} total):**\n\n"
            
            if low_stock:
                response_text += f"⚠️ **Low Stock Alerts ({len(low_stock)}):**\n"
                for supply in low_stock[:5]:
                    response_text += f"• {supply.get('name', 'Unknown')}: {supply.get('current_stock', 0)} units\n"
                response_text += "\n"
            else:
                response_text += "✅ **All supplies adequately stocked**\n\n"
            
            # Show supply categories
            categories = {}
            for supply in supplies:
                cat_id = supply.get("category_id", "unknown")
                if cat_id not in categories:
                    categories[cat_id] = 0
                categories[cat_id] += 1
            
            response_text += f"**Supply Categories:**\n"
            for cat_id, count in categories.items():
                response_text += f"• Category {cat_id}: {count} items\n"
            
            return ChatResponse(
                response=response_text,
                timestamp=datetime.now().isoformat(),
                type="data",
                data={"supplies": supplies, "low_stock": low_stock}
            )
        except Exception as e:
            return ChatResponse(
                response=f"Unable to retrieve supply information: {str(e)}",
                timestamp=datetime.now().isoformat(),
                type="error"
            )
    
    async def _handle_appointment_queries(self, message: str) -> ChatResponse:
        """Handle appointment-related queries."""
        try:
            result = await self.client._safe_call_tool("list_appointments", {})
            appointments = result.get("appointments", [])
            
            response_text = f"📅 **Appointments ({len(appointments)} total):**\n\n"
            
            if appointments:
                # Show upcoming appointments
                for i, apt in enumerate(appointments[:5], 1):
                    response_text += f"**{i}. {apt.get('appointment_date', 'TBD')[:10]}**\n"
                    response_text += f"   • Patient ID: {apt.get('patient_id', 'N/A')}\n"
                    response_text += f"   • Doctor ID: {apt.get('doctor_id', 'N/A')}\n"
                    response_text += f"   • Reason: {apt.get('reason', 'General')}\n"
                    response_text += f"   • Duration: {apt.get('duration_minutes', 30)} minutes\n\n"
                
                if len(appointments) > 5:
                    response_text += f"... and {len(appointments) - 5} more appointments.\n"
            else:
                response_text += "No appointments scheduled.\n"
            
            return ChatResponse(
                response=response_text,
                timestamp=datetime.now().isoformat(),
                type="data",
                data={"appointments": appointments}
            )
        except Exception as e:
            return ChatResponse(
                response=f"Unable to retrieve appointment information: {str(e)}",
                timestamp=datetime.now().isoformat(),
                type="error"
            )
    
    async def _handle_autonomous_operations(self, message: str) -> ChatResponse:
        """Handle autonomous AI operations."""
        try:
            response_text = "🤖 **Starting Autonomous Hospital Management...**\n\n"
            
            # Run autonomous management
            await self.client.autonomous_hospital_management()
            
            response_text += "✅ **Autonomous management completed!**\n\n"
            response_text += "**Operations Performed:**\n"
            response_text += "• Bed allocation optimization\n"
            response_text += "• Equipment usage analysis\n"
            response_text += "• Supply level monitoring\n"
            response_text += "• Maintenance scheduling\n"
            response_text += "• Patient flow optimization\n\n"
            response_text += "**Next Steps:**\n"
            response_text += "• Review optimization recommendations\n"
            response_text += "• Monitor system performance\n"
            response_text += "• Schedule follow-up analysis\n"
            
            return ChatResponse(
                response=response_text,
                timestamp=datetime.now().isoformat(),
                type="data"
            )
        except Exception as e:
            return ChatResponse(
                response=f"Unable to run autonomous operations: {str(e)}",
                timestamp=datetime.now().isoformat(),
                type="error"
            )
    
    async def _handle_department_queries(self, message: str) -> ChatResponse:
        """Handle department-related queries."""
        try:
            result = await self.client._safe_call_tool("list_departments", {})
            departments = result.get("departments", [])
            
            response_text = f"🏢 **Departments ({len(departments)} total):**\n\n"
            
            for i, dept in enumerate(departments, 1):
                response_text += f"**{i}. {dept.get('name', 'Unknown')}**\n"
                response_text += f"   • Floor: {dept.get('floor_number', 'N/A')}\n"
                response_text += f"   • Phone: {dept.get('phone', 'N/A')}\n"
                response_text += f"   • Email: {dept.get('email', 'N/A')}\n"
                response_text += f"   • Description: {dept.get('description', 'N/A')}\n\n"
            
            return ChatResponse(
                response=response_text,
                timestamp=datetime.now().isoformat(),
                type="data",
                data={"departments": departments}
            )
        except Exception as e:
            return ChatResponse(
                response=f"Unable to retrieve department information: {str(e)}",
                timestamp=datetime.now().isoformat(),
                type="error"
            )
    
    async def _handle_user_queries(self, message: str) -> ChatResponse:
        """Handle user-related queries."""
        try:
            result = await self.client._safe_call_tool("list_users", {})
            users = result.get("users", [])
            
            # Group by role
            roles = {}
            for user in users:
                role = user.get("role", "unknown")
                if role not in roles:
                    roles[role] = []
                roles[role].append(user)
            
            response_text = f"👤 **Users ({len(users)} total):**\n\n"
            
            for role, role_users in roles.items():
                response_text += f"**{role.title()}s:** {len(role_users)}\n"
                for user in role_users[:3]:  # Show first 3
                    response_text += f"• {user.get('first_name', '')} {user.get('last_name', '')} ({user.get('username', 'N/A')})\n"
                response_text += "\n"
            
            return ChatResponse(
                response=response_text,
                timestamp=datetime.now().isoformat(),
                type="data",
                data={"users": users, "roles": roles}
            )
        except Exception as e:
            return ChatResponse(
                response=f"Unable to retrieve user information: {str(e)}",
                timestamp=datetime.now().isoformat(),
                type="error"
            )


# Initialize the chatbot
chatbot = HospitalChatBot()


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    await chatbot.initialize()
    logger.info("Hospital Management ChatBot Server started")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat."""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            logger.info(f"Received message: {user_message}")
            
            # Process message with chatbot
            response = await chatbot.process_message(user_message)
            
            # Send response back to client
            await manager.send_personal_message(
                json.dumps(response.dict()), 
                websocket
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.post("/api/chat")
async def chat_endpoint(message: ChatMessage):
    """REST API endpoint for chat."""
    try:
        response = await chatbot.process_message(message.message)
        return response
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/hospital/status")
async def hospital_status():
    """Get current hospital status."""
    try:
        await chatbot.ensure_connection()
        analysis = await chatbot.client.analyze_hospital_state()
        return {"status": "success", "data": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "chatbot_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
