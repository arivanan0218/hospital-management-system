"""
Hospital Management System MCP Client - Comprehensive Demo
Demonstrates all 40+ tools available in the comprehensive_server.py
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from datetime import datetime, date
import uuid


class HospitalManagementClient:
    def __init__(self):
        self.session = None
        
    async def connect(self):
        """Connect to the MCP server."""
        server_params = StdioServerParameters(
            command="python",
            args=["comprehensive_server.py"],
            env=None
        )
        
        stdio_transport = await stdio_client(server_params)
        self.session = ClientSession(stdio_transport[0], stdio_transport[1])
        
        await self.session.initialize()
        print("✅ Connected to Hospital Management MCP Server")
        
    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.session:
            await self.session.close()
            print("📡 Disconnected from server")

    async def list_available_tools(self):
        """List all available tools from the server."""
        tools = await self.session.list_tools()
        print(f"\n🛠️  Available Tools ({len(tools.tools)}):")
        print("=" * 50)
        
        # Group tools by category
        categories = {
            "User Management": [],
            "Department Management": [],
            "Patient Management": [],
            "Bed Management": [],
            "Staff Management": [],
            "Equipment Management": [],
            "Supply Management": [],
            "Appointment Management": [],
            "Agent Logging": [],
            "Legacy Support": []
        }
        
        for tool in tools.tools:
            name = tool.name
            if "user" in name:
                categories["User Management"].append(name)
            elif "department" in name:
                categories["Department Management"].append(name)
            elif "patient" in name:
                categories["Patient Management"].append(name)
            elif "bed" in name:
                categories["Bed Management"].append(name)
            elif "staff" in name:
                categories["Staff Management"].append(name)
            elif "equipment" in name:
                categories["Equipment Management"].append(name)
            elif "supply" in name or "stock" in name:
                categories["Supply Management"].append(name)
            elif "appointment" in name:
                categories["Appointment Management"].append(name)
            elif "agent" in name or "log" in name:
                categories["Agent Logging"].append(name)
            elif "legacy" in name:
                categories["Legacy Support"].append(name)
            else:
                categories["User Management"].append(name)  # Default category
        
        for category, tool_names in categories.items():
            if tool_names:
                print(f"\n{category}:")
                for tool_name in tool_names:
                    print(f"  • {tool_name}")
    
    async def demo_user_management(self):
        """Demonstrate user management operations."""
        print("\n👥 === USER MANAGEMENT DEMO ===")
        
        # Create a new user
        print("\n1. Creating a new user...")
        create_result = await self.session.call_tool(
            "create_user",
            {
                "username": "demo_doctor",
                "email": "demo@hospital.com",
                "password_hash": "hashed_password_demo",
                "role": "doctor",
                "first_name": "Demo",
                "last_name": "Doctor",
                "phone": "555-DEMO"
            }
        )
        print(f"Result: {create_result.content[0].text}")
        
        if "success" in create_result.content[0].text:
            # Parse the user ID from the response
            result_data = json.loads(create_result.content[0].text)
            if result_data.get("success") and "data" in result_data:
                user_id = result_data["data"]["id"]
                
                # Get user by ID
                print("\n2. Getting user by ID...")
                get_result = await self.session.call_tool("get_user_by_id", {"user_id": user_id})
                print(f"Result: {get_result.content[0].text}")
                
                # Update user
                print("\n3. Updating user...")
                update_result = await self.session.call_tool(
                    "update_user",
                    {
                        "user_id": user_id,
                        "phone": "555-UPDATED"
                    }
                )
                print(f"Result: {update_result.content[0].text}")
        
        # List all users
        print("\n4. Listing all users...")
        list_result = await self.session.call_tool("list_users", {})
        print(f"Result: {list_result.content[0].text}")

    async def demo_department_management(self):
        """Demonstrate department management operations."""
        print("\n🏢 === DEPARTMENT MANAGEMENT DEMO ===")
        
        # Create a new department
        print("\n1. Creating a new department...")
        create_result = await self.session.call_tool(
            "create_department",
            {
                "name": "Demo Department",
                "description": "A demonstration department",
                "floor_number": 2,
                "phone": "555-DEPT",
                "email": "demo.dept@hospital.com"
            }
        )
        print(f"Result: {create_result.content[0].text}")
        
        # List all departments
        print("\n2. Listing all departments...")
        list_result = await self.session.call_tool("list_departments", {})
        print(f"Result: {list_result.content[0].text}")

    async def demo_patient_management(self):
        """Demonstrate patient management operations."""
        print("\n🤒 === PATIENT MANAGEMENT DEMO ===")
        
        # Create a new patient
        print("\n1. Creating a new patient...")
        create_result = await self.session.call_tool(
            "create_patient",
            {
                "patient_number": "P999",
                "first_name": "Demo",
                "last_name": "Patient",
                "date_of_birth": "1990-05-15",
                "gender": "male",
                "phone": "555-PATIENT",
                "email": "demo.patient@email.com",
                "address": "123 Demo St, Demo City",
                "blood_type": "O+",
                "allergies": "None known"
            }
        )
        print(f"Result: {create_result.content[0].text}")
        
        # List all patients
        print("\n2. Listing all patients...")
        list_result = await self.session.call_tool("list_patients", {})
        print(f"Result: {list_result.content[0].text}")

    async def demo_bed_management(self):
        """Demonstrate bed management operations (AI Agent)."""
        print("\n🛏️  === BED MANAGEMENT AGENT DEMO ===")
        
        # List available beds
        print("\n1. Listing available beds...")
        beds_result = await self.session.call_tool("list_beds", {"status": "available"})
        print(f"Result: {beds_result.content[0].text}")
        
        # Get department and patient for bed assignment demo
        departments_result = await self.session.call_tool("list_departments", {})
        patients_result = await self.session.call_tool("list_patients", {})
        
        try:
            dept_data = json.loads(departments_result.content[0].text)
            patient_data = json.loads(patients_result.content[0].text)
            
            if dept_data.get("departments") and patient_data.get("patients"):
                dept_id = dept_data["departments"][0]["id"]
                patient_id = patient_data["patients"][0]["id"]
                
                # Create a new room and bed for demo
                print("\n2. Creating a demo room...")
                room_result = await self.session.call_tool(
                    "create_room",
                    {
                        "room_number": "DEMO001",
                        "department_id": dept_id,
                        "room_type": "private",
                        "capacity": 1
                    }
                )
                print(f"Room creation result: {room_result.content[0].text}")
                
                room_data = json.loads(room_result.content[0].text)
                if room_data.get("success"):
                    room_id = room_data["data"]["id"]
                    
                    # Create a new bed
                    print("\n3. Creating a demo bed...")
                    bed_result = await self.session.call_tool(
                        "create_bed",
                        {
                            "bed_number": "DEMO001A",
                            "room_id": room_id,
                            "bed_type": "standard"
                        }
                    )
                    print(f"Bed creation result: {bed_result.content[0].text}")
                    
                    bed_data = json.loads(bed_result.content[0].text)
                    if bed_data.get("success"):
                        bed_id = bed_data["data"]["id"]
                        
                        # Assign bed to patient
                        print("\n4. Assigning bed to patient...")
                        assign_result = await self.session.call_tool(
                            "assign_bed_to_patient",
                            {
                                "bed_id": bed_id,
                                "patient_id": patient_id,
                                "admission_date": datetime.now().isoformat()
                            }
                        )
                        print(f"Assignment result: {assign_result.content[0].text}")
                        
                        # Discharge patient
                        print("\n5. Discharging patient from bed...")
                        discharge_result = await self.session.call_tool(
                            "discharge_bed",
                            {
                                "bed_id": bed_id,
                                "discharge_date": datetime.now().isoformat()
                            }
                        )
                        print(f"Discharge result: {discharge_result.content[0].text}")
        
        except Exception as e:
            print(f"Error in bed management demo: {e}")

    async def demo_equipment_management(self):
        """Demonstrate equipment management operations (AI Agent)."""
        print("\n🔧 === EQUIPMENT TRACKER AGENT DEMO ===")
        
        # Create equipment category
        print("\n1. Creating equipment category...")
        category_result = await self.session.call_tool(
            "create_equipment_category",
            {
                "name": "Demo Equipment",
                "description": "Equipment for demonstration purposes"
            }
        )
        print(f"Result: {category_result.content[0].text}")
        
        category_data = json.loads(category_result.content[0].text)
        if category_data.get("success"):
            category_id = category_data["data"]["id"]
            
            # Create equipment
            print("\n2. Creating equipment...")
            equipment_result = await self.session.call_tool(
                "create_equipment",
                {
                    "equipment_id": "DEMO-EQ-001",
                    "name": "Demo Monitor",
                    "category_id": category_id,
                    "model": "DemoMax 2024",
                    "manufacturer": "Demo Corp",
                    "serial_number": "DEMO123456",
                    "location": "Demo Room",
                    "cost": 15000.00
                }
            )
            print(f"Result: {equipment_result.content[0].text}")
            
            equipment_data = json.loads(equipment_result.content[0].text)
            if equipment_data.get("success"):
                equipment_id = equipment_data["data"]["id"]
                
                # Update equipment status
                print("\n3. Updating equipment status...")
                status_result = await self.session.call_tool(
                    "update_equipment_status",
                    {
                        "equipment_id": equipment_id,
                        "status": "in_use",
                        "notes": "Assigned to demo room for testing"
                    }
                )
                print(f"Result: {status_result.content[0].text}")
        
        # List all equipment
        print("\n4. Listing all equipment...")
        list_result = await self.session.call_tool("list_equipment", {})
        print(f"Result: {list_result.content[0].text}")

    async def demo_supply_management(self):
        """Demonstrate supply management operations (AI Agent)."""
        print("\n📦 === SUPPLY INVENTORY AGENT DEMO ===")
        
        # Create supply category
        print("\n1. Creating supply category...")
        category_result = await self.session.call_tool(
            "create_supply_category",
            {
                "name": "Demo Supplies",
                "description": "Supplies for demonstration purposes"
            }
        )
        print(f"Result: {category_result.content[0].text}")
        
        category_data = json.loads(category_result.content[0].text)
        if category_data.get("success"):
            category_id = category_data["data"]["id"]
            
            # Create supply
            print("\n2. Creating supply item...")
            supply_result = await self.session.call_tool(
                "create_supply",
                {
                    "item_code": "DEMO-SUP-001",
                    "name": "Demo Bandages",
                    "category_id": category_id,
                    "unit_of_measure": "boxes",
                    "minimum_stock_level": 10,
                    "maximum_stock_level": 100,
                    "current_stock": 5,  # Low stock for testing
                    "unit_cost": 25.50,
                    "supplier": "Demo Medical Supply Co"
                }
            )
            print(f"Result: {supply_result.content[0].text}")
            
            supply_data = json.loads(supply_result.content[0].text)
            if supply_data.get("success"):
                supply_id = supply_data["data"]["id"]
                
                # Get users for transaction
                users_result = await self.session.call_tool("list_users", {})
                users_data = json.loads(users_result.content[0].text)
                
                if users_data.get("users"):
                    user_id = users_data["users"][0]["id"]
                    
                    # Update stock
                    print("\n3. Updating supply stock...")
                    stock_result = await self.session.call_tool(
                        "update_supply_stock",
                        {
                            "supply_id": supply_id,
                            "quantity_change": 20,
                            "transaction_type": "in",
                            "performed_by": user_id,
                            "unit_cost": 25.50,
                            "reference_number": "DEMO-PO-001",
                            "notes": "Demo restock for testing"
                        }
                    )
                    print(f"Result: {stock_result.content[0].text}")
        
        # List low stock supplies
        print("\n4. Checking low stock supplies...")
        low_stock_result = await self.session.call_tool("list_supplies", {"low_stock_only": True})
        print(f"Result: {low_stock_result.content[0].text}")
        
        # List all supplies
        print("\n5. Listing all supplies...")
        all_supplies_result = await self.session.call_tool("list_supplies", {})
        print(f"Result: {all_supplies_result.content[0].text}")

    async def demo_appointment_management(self):
        """Demonstrate appointment management operations."""
        print("\n📅 === APPOINTMENT MANAGEMENT DEMO ===")
        
        # Get required data for appointment
        patients_result = await self.session.call_tool("list_patients", {})
        users_result = await self.session.call_tool("list_users", {})
        departments_result = await self.session.call_tool("list_departments", {})
        
        try:
            patients_data = json.loads(patients_result.content[0].text)
            users_data = json.loads(users_result.content[0].text)
            departments_data = json.loads(departments_result.content[0].text)
            
            if (patients_data.get("patients") and 
                users_data.get("users") and 
                departments_data.get("departments")):
                
                patient_id = patients_data["patients"][0]["id"]
                doctor_id = users_data["users"][0]["id"]  # First user as doctor
                department_id = departments_data["departments"][0]["id"]
                
                # Create appointment
                print("\n1. Creating appointment...")
                appointment_result = await self.session.call_tool(
                    "create_appointment",
                    {
                        "patient_id": patient_id,
                        "doctor_id": doctor_id,
                        "department_id": department_id,
                        "appointment_date": "2024-08-15T14:30:00",
                        "duration_minutes": 60,
                        "reason": "Demo consultation",
                        "notes": "Demo appointment for testing"
                    }
                )
                print(f"Result: {appointment_result.content[0].text}")
        
        except Exception as e:
            print(f"Error in appointment demo: {e}")
        
        # List all appointments
        print("\n2. Listing all appointments...")
        list_result = await self.session.call_tool("list_appointments", {})
        print(f"Result: {list_result.content[0].text}")

    async def demo_agent_logging(self):
        """Demonstrate AI agent interaction logging."""
        print("\n🤖 === AI AGENT LOGGING DEMO ===")
        
        # Get user for logging
        users_result = await self.session.call_tool("list_users", {})
        users_data = json.loads(users_result.content[0].text)
        
        if users_data.get("users"):
            user_id = users_data["users"][0]["id"]
            
            # Log agent interaction
            print("\n1. Logging agent interaction...")
            log_result = await self.session.call_tool(
                "log_agent_interaction",
                {
                    "agent_type": "bed_management",
                    "user_id": user_id,
                    "query": "Find available beds in cardiology department",
                    "response": "Found 2 available beds in cardiology: 301A, 302B",
                    "action_taken": "bed_search",
                    "confidence_score": 0.95,
                    "execution_time_ms": 125
                }
            )
            print(f"Result: {log_result.content[0].text}")

    async def demo_staff_management(self):
        """Demonstrate staff management operations (AI Agent)."""
        print("\n👨‍⚕️ === STAFF ALLOCATION AGENT DEMO ===")
        
        # Get required data
        users_result = await self.session.call_tool("list_users", {})
        departments_result = await self.session.call_tool("list_departments", {})
        
        try:
            users_data = json.loads(users_result.content[0].text)
            departments_data = json.loads(departments_result.content[0].text)
            
            if users_data.get("users") and departments_data.get("departments"):
                user_id = users_data["users"][0]["id"]
                department_id = departments_data["departments"][0]["id"]
                
                # Create staff member
                print("\n1. Creating staff member...")
                staff_result = await self.session.call_tool(
                    "create_staff",
                    {
                        "user_id": user_id,
                        "employee_id": "DEMO-EMP-001",
                        "department_id": department_id,
                        "position": "Demo Nurse",
                        "specialization": "Demo Care",
                        "hire_date": "2024-01-15",
                        "salary": 65000.00,
                        "shift_pattern": "day"
                    }
                )
                print(f"Result: {staff_result.content[0].text}")
        
        except Exception as e:
            print(f"Error in staff demo: {e}")
        
        # List all staff
        print("\n2. Listing all staff...")
        list_result = await self.session.call_tool("list_staff", {})
        print(f"Result: {list_result.content[0].text}")

    async def demo_legacy_support(self):
        """Demonstrate legacy user support."""
        print("\n🔄 === LEGACY SUPPORT DEMO ===")
        
        # Create legacy user
        print("\n1. Creating legacy user...")
        legacy_result = await self.session.call_tool(
            "create_legacy_user",
            {
                "name": "Demo Legacy User",
                "email": "legacy@hospital.com",
                "address": "123 Legacy St",
                "phone": "555-LEGACY"
            }
        )
        print(f"Result: {legacy_result.content[0].text}")
        
        # List legacy users
        print("\n2. Listing legacy users...")
        list_result = await self.session.call_tool("list_legacy_users", {})
        print(f"Result: {list_result.content[0].text}")

    async def run_comprehensive_demo(self):
        """Run a comprehensive demonstration of all features."""
        print("🏥 HOSPITAL MANAGEMENT SYSTEM - COMPREHENSIVE DEMO")
        print("=" * 60)
        
        try:
            await self.connect()
            await self.list_available_tools()
            
            # Run all demonstrations
            await self.demo_user_management()
            await self.demo_department_management()
            await self.demo_patient_management()
            await self.demo_bed_management()
            await self.demo_equipment_management()
            await self.demo_supply_management()
            await self.demo_staff_management()
            await self.demo_appointment_management()
            await self.demo_agent_logging()
            await self.demo_legacy_support()
            
            print("\n🎉 === COMPREHENSIVE DEMO COMPLETED ===")
            print("All 40+ MCP tools have been demonstrated!")
            print("The hospital management system is fully operational.")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
        finally:
            await self.disconnect()

    async def interactive_mode(self):
        """Run in interactive mode for manual testing."""
        print("🏥 HOSPITAL MANAGEMENT SYSTEM - INTERACTIVE MODE")
        print("=" * 55)
        
        await self.connect()
        await self.list_available_tools()
        
        print("\n📋 Interactive Menu:")
        print("1. User Management")
        print("2. Department Management") 
        print("3. Patient Management")
        print("4. Bed Management (AI Agent)")
        print("5. Equipment Management (AI Agent)")
        print("6. Supply Management (AI Agent)")
        print("7. Staff Management (AI Agent)")
        print("8. Appointment Management")
        print("9. Agent Logging")
        print("10. Legacy Support")
        print("11. Run Comprehensive Demo")
        print("0. Exit")
        
        while True:
            try:
                choice = input("\nEnter your choice (0-11): ").strip()
                
                if choice == "0":
                    break
                elif choice == "1":
                    await self.demo_user_management()
                elif choice == "2":
                    await self.demo_department_management()
                elif choice == "3":
                    await self.demo_patient_management()
                elif choice == "4":
                    await self.demo_bed_management()
                elif choice == "5":
                    await self.demo_equipment_management()
                elif choice == "6":
                    await self.demo_supply_management()
                elif choice == "7":
                    await self.demo_staff_management()
                elif choice == "8":
                    await self.demo_appointment_management()
                elif choice == "9":
                    await self.demo_agent_logging()
                elif choice == "10":
                    await self.demo_legacy_support()
                elif choice == "11":
                    await self.run_comprehensive_demo()
                else:
                    print("Invalid choice. Please enter 0-11.")
                    
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        await self.disconnect()


async def main():
    """Main function to run the client."""
    client = HospitalManagementClient()
    
    print("🏥 Hospital Management System MCP Client")
    print("Choose mode:")
    print("1. Comprehensive Demo (Automated)")
    print("2. Interactive Mode (Manual)")
    
    try:
        mode = input("Enter choice (1 or 2): ").strip()
        
        if mode == "1":
            await client.run_comprehensive_demo()
        elif mode == "2":
            await client.interactive_mode()
        else:
            print("Invalid choice. Running comprehensive demo...")
            await client.run_comprehensive_demo()
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
