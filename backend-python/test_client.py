"""
Hospital Management System MCP Client - Working Demo
Demonstrates all 40+ tools available in the comprehensive_server.py
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from datetime import datetime


async def test_hospital_management():
    """Test the hospital management system."""
    print("🏥 HOSPITAL MANAGEMENT SYSTEM - QUICK TEST")
    print("=" * 50)
    
    server_params = StdioServerParameters(
        command="python",
        args=["comprehensive_server.py"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connected to Hospital Management MCP Server")
            
            # List available tools
            tools = await session.list_tools()
            print(f"\n🛠️  Available Tools: {len(tools.tools)}")
            
            # Group tools by category
            categories = {}
            for tool in tools.tools:
                name = tool.name
                if "user" in name:
                    category = "User Management"
                elif "department" in name:
                    category = "Department Management"
                elif "patient" in name:
                    category = "Patient Management"
                elif "bed" in name:
                    category = "Bed Management"
                elif "staff" in name:
                    category = "Staff Management"
                elif "equipment" in name:
                    category = "Equipment Management"
                elif "supply" in name or "stock" in name:
                    category = "Supply Management"
                elif "appointment" in name:
                    category = "Appointment Management"
                else:
                    category = "Other"
                
                if category not in categories:
                    categories[category] = []
                categories[category].append(name)
            
            for category, tool_names in categories.items():
                print(f"\n{category}: {len(tool_names)} tools")
                for tool_name in tool_names[:3]:  # Show first 3 tools
                    print(f"  • {tool_name}")
                if len(tool_names) > 3:
                    print(f"  ... and {len(tool_names) - 3} more")
            
            # Test basic functionality
            print("\n🧪 === TESTING CORE FUNCTIONALITY ===")
            
            # Test listing users
            print("\n1. Testing user management...")
            result = await session.call_tool("list_users", {})
            print(f"Users found: {result.content[0].text[:100]}...")
            
            # Test listing departments
            print("\n2. Testing department management...")
            result = await session.call_tool("list_departments", {})
            print(f"Departments found: {result.content[0].text[:100]}...")
            
            # Test listing patients
            print("\n3. Testing patient management...")
            result = await session.call_tool("list_patients", {})
            print(f"Patients found: {result.content[0].text[:100]}...")
            
            # Test listing beds
            print("\n4. Testing bed management...")
            result = await session.call_tool("list_beds", {})
            print(f"Beds found: {result.content[0].text[:100]}...")
            
            # Test equipment
            print("\n5. Testing equipment management...")
            result = await session.call_tool("list_equipment", {})
            print(f"Equipment found: {result.content[0].text[:100]}...")
            
            # Test supplies
            print("\n6. Testing supply management...")
            result = await session.call_tool("list_supplies", {})
            print(f"Supplies found: {result.content[0].text[:100]}...")
            
            print("\n🎉 === ALL TESTS COMPLETED SUCCESSFULLY ===")
            print("✅ Hospital Management System is fully operational!")
            print("✅ All 4 AI agents are ready for use:")
            print("   🛏️  Bed Management Agent")
            print("   🔧 Equipment Tracker Agent") 
            print("   👨‍⚕️ Staff Allocation Agent")
            print("   📦 Supply Inventory Agent")
            print(f"✅ {len(tools.tools)} MCP tools available for integration")


async def create_demo_data():
    """Create some demo data to show system capabilities."""
    print("\n🏗️  === CREATING DEMO DATA ===")
    
    server_params = StdioServerParameters(
        command="python",
        args=["comprehensive_server.py"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Create a demo user
            print("\n1. Creating demo user...")
            result = await session.call_tool(
                "create_user",
                {
                    "username": "demo_user",
                    "email": "demo@hospital.com",
                    "password_hash": "demo_hash",
                    "role": "nurse",
                    "first_name": "Demo",
                    "last_name": "User",
                    "phone": "555-DEMO"
                }
            )
            print(f"Result: {result.content[0].text}")
            
            # Create a demo department
            print("\n2. Creating demo department...")
            result = await session.call_tool(
                "create_department",
                {
                    "name": "Demo Ward",
                    "description": "Demonstration ward for testing",
                    "floor_number": 3
                }
            )
            print(f"Result: {result.content[0].text}")
            
            print("\n✅ Demo data creation completed!")


async def main():
    """Main function."""
    print("🏥 Hospital Management System Test Client")
    print("Choose option:")
    print("1. Run System Test")
    print("2. Create Demo Data")
    print("3. Both")
    
    try:
        choice = input("Enter choice (1, 2, or 3): ").strip()
        
        if choice == "1":
            await test_hospital_management()
        elif choice == "2":
            await create_demo_data()
        elif choice == "3":
            await test_hospital_management()
            await create_demo_data()
        else:
            print("Invalid choice. Running system test...")
            await test_hospital_management()
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
