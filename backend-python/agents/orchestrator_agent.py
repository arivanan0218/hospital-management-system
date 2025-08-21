"""Orchestrator Agent - Master coordinator for multi-agent hospital management system"""

import uuid
import json
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, date
from .base_agent import BaseAgent

# Import all specialized agents
try:
    from .user_agent import UserAgent
    from .department_agent import DepartmentAgent
    from .patient_agent import PatientAgent
    from .room_bed_agent import RoomBedAgent
    from .staff_agent import StaffAgent
    from .equipment_agent import EquipmentAgent
    from .inventory_agent import InventoryAgent
    from .appointment_agent import AppointmentAgent
    from .medical_document_agent import MedicalDocumentAgent
    from .meeting_agent import MeetingAgent  # NEW
    from .discharge_agent import DischargeAgent  # NEW
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False


class OrchestratorAgent(BaseAgent):
    """Master orchestrator agent that coordinates all specialized agents"""
    
    def __init__(self):
        super().__init__("Orchestrator Agent", "orchestrator_agent")
        self.agents = {}
        self.agent_routing = {}
        self.initialize_agents()
        self.setup_routing()
    
    def initialize_agents(self):
        """Initialize all specialized agents"""
        if not AGENTS_AVAILABLE:
            print("WARNING: Specialized agents not available")
            return
        
        try:
            self.agents = {
                "user": UserAgent(),
                "department": DepartmentAgent(),
                "patient": PatientAgent(),
                "room_bed": RoomBedAgent(),
                "staff": StaffAgent(),
                "equipment": EquipmentAgent(),
                "inventory": InventoryAgent(),
                "appointment": AppointmentAgent(),
                "medical_document": MedicalDocumentAgent(),
                "meeting": MeetingAgent(),  # NEW
                "discharge": DischargeAgent(),  # NEW
            }
            print(f"✅ Initialized {len(self.agents)} specialized agents")
        except Exception as e:
            print(f"❌ Failed to initialize agents: {str(e)}")
    
    def setup_routing(self):
        """Setup routing table for tool -> agent mapping"""
        self.agent_routing = {}
        
        for agent_name, agent in self.agents.items():
            for tool in agent.get_tools():
                self.agent_routing[tool] = agent_name
        
        print(f"📋 Setup routing for {len(self.agent_routing)} tools across {len(self.agents)} agents")
    
    def get_tools(self) -> List[str]:
        """Return list of all tools from all agents plus orchestrator-specific tools"""
        all_tools = ["get_system_status", "route_request", "execute_workflow", "get_agent_info"]
        
        for agent in self.agents.values():
            all_tools.extend(agent.get_tools())
        
        return all_tools
    
    def get_capabilities(self) -> List[str]:
        """Return list of orchestrator capabilities"""
        return [
            "Multi-agent coordination and routing",
            "Complex workflow execution",
            "Cross-agent operation management",
            "System-wide status monitoring",
            "Agent load balancing and failover",
            "Comprehensive hospital management orchestration"
        ]
    
    def route_request(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Route a tool request to the appropriate specialized agent"""
        import inspect
        
        try:
            if tool_name in self.agent_routing:
                agent_name = self.agent_routing[tool_name]
                agent = self.agents[agent_name]
                
                # Check if agent has the method
                if hasattr(agent, tool_name):
                    method = getattr(agent, tool_name)
                    
                    # Filter parameters to only include what the method expects
                    method_signature = inspect.signature(method)
                    filtered_kwargs = {}
                    
                    for param_name in method_signature.parameters:
                        if param_name in kwargs:
                            filtered_kwargs[param_name] = kwargs[param_name]
                    
                    # Execute method with filtered parameters
                    result = method(**filtered_kwargs)
                    
                    # Log the routing
                    self.log_interaction(
                        query=f"Route {tool_name} to {agent_name} agent",
                        response=f"Successfully executed {tool_name}",
                        tool_used="route_request",
                        metadata={"target_agent": agent_name, "tool": tool_name}
                    )
                    
                    return {"success": True, "agent": agent_name, "result": result}
                else:
                    return {"success": False, "message": f"Method {tool_name} not found in {agent_name} agent"}
            else:
                return {"success": False, "message": f"No agent found for tool: {tool_name}"}
        except Exception as e:
            return {"success": False, "message": f"Failed to route request: {str(e)}"}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status from all agents"""
        try:
            system_status = {
                "orchestrator": {
                    "status": "active",
                    "agents_initialized": len(self.agents),
                    "tools_available": len(self.get_tools()),
                    "timestamp": datetime.now().isoformat()
                },
                "agents": {}
            }
            
            for agent_name, agent in self.agents.items():
                try:
                    agent_info = agent.get_agent_info()
                    system_status["agents"][agent_name] = agent_info
                except Exception as e:
                    system_status["agents"][agent_name] = {
                        "status": "error",
                        "error": str(e)
                    }
            
            # Log the interaction
            self.log_interaction(
                query="Get system status",
                response=f"System status retrieved for {len(self.agents)} agents",
                tool_used="get_system_status"
            )
            
            return {"success": True, "data": system_status}
        except Exception as e:
            return {"success": False, "message": f"Failed to get system status: {str(e)}"}
    
    def get_agent_info(self, agent_name: str = None) -> Dict[str, Any]:
        """Get information about a specific agent or all agents"""
        try:
            if agent_name:
                if agent_name in self.agents:
                    agent_info = self.agents[agent_name].get_agent_info()
                    return {"success": True, "data": agent_info}
                else:
                    return {"success": False, "message": f"Agent {agent_name} not found"}
            else:
                all_agents_info = {}
                for name, agent in self.agents.items():
                    all_agents_info[name] = agent.get_agent_info()
                
                return {"success": True, "data": all_agents_info}
        except Exception as e:
            return {"success": False, "message": f"Failed to get agent info: {str(e)}"}
    
    def execute_workflow(self, workflow_name: str, workflow_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complex multi-agent workflows"""
        try:
            if workflow_name == "patient_admission":
                return self._workflow_patient_admission(**workflow_params)
            elif workflow_name == "equipment_maintenance":
                return self._workflow_equipment_maintenance(**workflow_params)
            elif workflow_name == "staff_scheduling":
                return self._workflow_staff_scheduling(**workflow_params)
            elif workflow_name == "inventory_restock":
                return self._workflow_inventory_restock(**workflow_params)
            elif workflow_name == "patient_discharge":
                return self._workflow_patient_discharge(**workflow_params)
            else:
                return {"success": False, "message": f"Unknown workflow: {workflow_name}"}
        except Exception as e:
            return {"success": False, "message": f"Failed to execute workflow: {str(e)}"}
    
    # COMPLEX WORKFLOW IMPLEMENTATIONS
    
    def _workflow_patient_admission(self, patient_data: Dict, bed_preferences: Dict = None) -> Dict[str, Any]:
        """Complex workflow for patient admission"""
        try:
            results = {"steps": [], "patient_id": None, "bed_id": None}
            
            # Step 1: Create patient record
            patient_result = self.route_request("create_patient", **patient_data)
            results["steps"].append({"step": "create_patient", "result": patient_result})
            
            if not patient_result.get("success"):
                return {"success": False, "message": "Failed to create patient", "details": results}
            
            patient_id = patient_result["result"]["data"]["id"]
            results["patient_id"] = patient_id
            
            # Step 2: Find available bed
            bed_preferences = bed_preferences or {}
            bed_result = self.route_request("list_beds", status="available")
            results["steps"].append({"step": "find_available_beds", "result": bed_result})
            
            if not bed_result.get("data") or len(bed_result["data"]) == 0:
                return {"success": False, "message": "No available beds", "details": results}
            
            # Select first available bed (could be enhanced with preferences)
            selected_bed = bed_result["data"][0]
            bed_id = selected_bed["id"]
            results["bed_id"] = bed_id
            
            # Step 3: Assign bed to patient
            assign_result = self.route_request("assign_bed_to_patient", 
                                             bed_id=bed_id, 
                                             patient_id=patient_id,
                                             admission_date=datetime.now().strftime("%Y-%m-%d"))
            results["steps"].append({"step": "assign_bed", "result": assign_result})
            
            if not assign_result.get("success"):
                return {"success": False, "message": "Failed to assign bed", "details": results}
            
            # Log the workflow
            self.log_interaction(
                query=f"Execute patient admission workflow for {patient_data.get('first_name', '')} {patient_data.get('last_name', '')}",
                response=f"Patient admitted successfully - ID: {patient_id}, Bed: {bed_id}",
                tool_used="execute_workflow",
                metadata={"workflow": "patient_admission", "patient_id": patient_id, "bed_id": bed_id}
            )
            
            return {"success": True, "message": "Patient admission completed", "details": results}
        except Exception as e:
            return {"success": False, "message": f"Patient admission workflow failed: {str(e)}"}
    
    def _workflow_patient_discharge(self, patient_id: str, discharge_date: str = None) -> Dict[str, Any]:
        """Complex workflow for patient discharge"""
        try:
            results = {"steps": [], "patient_id": patient_id}
            discharge_date = discharge_date or datetime.now().strftime("%Y-%m-%d")
            
            # Step 1: Find patient's current bed
            patient_result = self.route_request("get_patient_by_id", patient_id=patient_id)
            results["steps"].append({"step": "get_patient", "result": patient_result})
            
            if not patient_result.get("data"):
                return {"success": False, "message": "Patient not found", "details": results}
            
            # Step 2: Find occupied beds for this patient
            bed_result = self.route_request("list_beds", status="occupied")
            patient_beds = [bed for bed in bed_result.get("data", []) if bed.get("patient_id") == patient_id]
            
            if not patient_beds:
                return {"success": False, "message": "No occupied bed found for patient", "details": results}
            
            # Step 3: Discharge from all beds
            for bed in patient_beds:
                discharge_result = self.route_request("discharge_bed", 
                                                    bed_id=bed["id"],
                                                    discharge_date=discharge_date)
                results["steps"].append({"step": f"discharge_bed_{bed['id']}", "result": discharge_result})
            
            # Log the workflow
            self.log_interaction(
                query=f"Execute patient discharge workflow for patient {patient_id}",
                response=f"Patient discharged successfully from {len(patient_beds)} bed(s)",
                tool_used="execute_workflow",
                metadata={"workflow": "patient_discharge", "patient_id": patient_id, "beds_discharged": len(patient_beds)}
            )
            
            return {"success": True, "message": "Patient discharge completed", "details": results}
        except Exception as e:
            return {"success": False, "message": f"Patient discharge workflow failed: {str(e)}"}
    
    def _workflow_equipment_maintenance(self, equipment_id: str, maintenance_type: str = "routine") -> Dict[str, Any]:
        """Complex workflow for equipment maintenance"""
        try:
            results = {"steps": [], "equipment_id": equipment_id}
            
            # Step 1: Get equipment details
            equipment_result = self.route_request("get_equipment_by_id", equipment_id=equipment_id)
            results["steps"].append({"step": "get_equipment", "result": equipment_result})
            
            if not equipment_result.get("data"):
                return {"success": False, "message": "Equipment not found", "details": results}
            
            # Step 2: Update equipment status to maintenance
            status_result = self.route_request("update_equipment_status", 
                                             equipment_id=equipment_id,
                                             status="maintenance",
                                             notes=f"Scheduled {maintenance_type} maintenance")
            results["steps"].append({"step": "update_status", "result": status_result})
            
            # Step 3: Schedule maintenance (if method exists)
            maintenance_date = datetime.now().strftime("%Y-%m-%d")
            schedule_result = self.route_request("schedule_equipment_maintenance",
                                               equipment_id=equipment_id,
                                               maintenance_date=maintenance_date,
                                               maintenance_type=maintenance_type)
            results["steps"].append({"step": "schedule_maintenance", "result": schedule_result})
            
            # Log the workflow
            self.log_interaction(
                query=f"Execute equipment maintenance workflow for {equipment_id}",
                response=f"Equipment maintenance scheduled successfully",
                tool_used="execute_workflow",
                metadata={"workflow": "equipment_maintenance", "equipment_id": equipment_id, "maintenance_type": maintenance_type}
            )
            
            return {"success": True, "message": "Equipment maintenance workflow completed", "details": results}
        except Exception as e:
            return {"success": False, "message": f"Equipment maintenance workflow failed: {str(e)}"}
    
    def _workflow_inventory_restock(self, supply_id: str, quantity: int, user_id: str = None) -> Dict[str, Any]:
        """Complex workflow for inventory restocking"""
        try:
            results = {"steps": [], "supply_id": supply_id}
            
            # Step 1: Get current supply info
            supply_result = self.route_request("get_supply_by_id", supply_id=supply_id)
            results["steps"].append({"step": "get_supply", "result": supply_result})
            
            if not supply_result.get("data"):
                return {"success": False, "message": "Supply not found", "details": results}
            
            # Step 2: Update stock
            stock_result = self.route_request("update_supply_stock",
                                             supply_id=supply_id,
                                             quantity_change=quantity,
                                             transaction_type="restock",
                                             user_id=user_id,
                                             notes=f"Automated restock - {quantity} units")
            results["steps"].append({"step": "update_stock", "result": stock_result})
            
            # Log the workflow
            self.log_interaction(
                query=f"Execute inventory restock workflow for supply {supply_id}",
                response=f"Inventory restocked with {quantity} units",
                tool_used="execute_workflow",
                metadata={"workflow": "inventory_restock", "supply_id": supply_id, "quantity": quantity}
            )
            
            return {"success": True, "message": "Inventory restock completed", "details": results}
        except Exception as e:
            return {"success": False, "message": f"Inventory restock workflow failed: {str(e)}"}
    
    def _workflow_staff_scheduling(self, department_id: str, date: str) -> Dict[str, Any]:
        """Complex workflow for staff scheduling"""
        try:
            results = {"steps": [], "department_id": department_id, "date": date}
            
            # Step 1: Get department staff
            staff_result = self.route_request("list_staff", department_id=department_id, status="active")
            results["steps"].append({"step": "get_department_staff", "result": staff_result})
            
            if not staff_result.get("data"):
                return {"success": False, "message": "No active staff found in department", "details": results}
            
            # Step 2: Get department schedule requirements (simplified)
            staff_list = staff_result["data"]
            schedule_info = {
                "total_staff": len(staff_list),
                "date": date,
                "department_id": department_id,
                "staff_members": [{"id": staff["id"], "position": staff["position"]} for staff in staff_list]
            }
            results["steps"].append({"step": "generate_schedule", "result": {"success": True, "data": schedule_info}})
            
            # Log the workflow
            self.log_interaction(
                query=f"Execute staff scheduling workflow for department {department_id} on {date}",
                response=f"Staff schedule generated for {len(staff_list)} staff members",
                tool_used="execute_workflow",
                metadata={"workflow": "staff_scheduling", "department_id": department_id, "staff_count": len(staff_list)}
            )
            
            return {"success": True, "message": "Staff scheduling completed", "details": results}
        except Exception as e:
            return {"success": False, "message": f"Staff scheduling workflow failed: {str(e)}"}
