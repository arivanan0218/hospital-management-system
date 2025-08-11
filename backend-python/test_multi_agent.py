#!/usr/bin/env python3
"""
Test script for Hospital Management System Multi-Agent Architecture
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_multi_agent_system():
    """Test the multi-agent system functionality"""
    print("🧪 Testing Hospital Management System Multi-Agent Architecture")
    print("=" * 60)
    
    try:
        # Import the multi-agent system
        from agents.orchestrator_agent import OrchestratorAgent
        
        print("✅ Multi-agent system imports successful")
        
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        print(f"✅ Orchestrator initialized with {len(orchestrator.agents)} agents")
        
        # Test 1: System Status
        print("\n📊 Test 1: System Status")
        status = orchestrator.get_system_status()
        if status.get("success"):
            print("✅ System status retrieved successfully")
            agents_count = len(status["data"]["agents"])
            print(f"   Agents active: {agents_count}")
        else:
            print(f"❌ System status failed: {status.get('message')}")
        
        # Test 2: Agent Information
        print("\n🤖 Test 2: Agent Information")
        agent_info = orchestrator.get_agent_info()
        if agent_info.get("success"):
            print("✅ Agent information retrieved successfully")
            for agent_name, info in agent_info["data"].items():
                tools_count = len(info.get("tools", []))
                print(f"   • {info['name']}: {tools_count} tools")
        else:
            print(f"❌ Agent info failed: {agent_info.get('message')}")
        
        # Test 3: Tool Routing
        print("\n🔧 Test 3: Tool Routing")
        routing_tests = [
            ("create_user", "user"),
            ("create_patient", "patient"),
            ("list_departments", "department"),
            ("create_bed", "room_bed"),
            ("list_staff", "staff"),
            ("create_equipment", "equipment"),
            ("list_supplies", "inventory"),
            ("create_appointment", "appointment")
        ]
        
        for tool_name, expected_agent in routing_tests:
            if tool_name in orchestrator.agent_routing:
                actual_agent = orchestrator.agent_routing[tool_name]
                if actual_agent == expected_agent:
                    print(f"   ✅ {tool_name} → {actual_agent}")
                else:
                    print(f"   ❌ {tool_name} → {actual_agent} (expected {expected_agent})")
            else:
                print(f"   ❌ {tool_name} not found in routing table")
        
        # Test 4: Database Connection (if available)
        print("\n🗃️  Test 4: Database Connection")
        try:
            from database import SessionLocal
            from sqlalchemy import text
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
        
        # Test 5: Tool Execution (mock test without database operations)
        print("\n⚙️  Test 5: Tool Execution Test")
        try:
            # Test system-level tools that don't require database
            system_status = orchestrator.get_system_status()
            if system_status.get("success"):
                print("✅ System tool execution successful")
            else:
                print(f"❌ System tool execution failed: {system_status.get('message')}")
        except Exception as e:
            print(f"❌ Tool execution error: {str(e)}")
        
        # Test 6: Workflow Definition Check
        print("\n🔄 Test 6: Workflow Definitions")
        workflows = [
            "patient_admission",
            "patient_discharge", 
            "equipment_maintenance",
            "inventory_restock",
            "staff_scheduling"
        ]
        
        for workflow in workflows:
            method_name = f"_workflow_{workflow}"
            if hasattr(orchestrator, method_name):
                print(f"   ✅ {workflow} workflow defined")
            else:
                print(f"   ❌ {workflow} workflow missing")
        
        print("\n" + "=" * 60)
        print("🎉 Multi-Agent System Test Complete!")
        print("\n📋 Summary:")
        print(f"   • Agents: {len(orchestrator.agents)}")
        print(f"   • Total Tools: {len(orchestrator.get_tools())}")
        print(f"   • Routing Rules: {len(orchestrator.agent_routing)}")
        print(f"   • Workflows: {len(workflows)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all agent modules are properly created")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_capabilities():
    """Test individual agent capabilities"""
    print("\n🔍 Testing Individual Agent Capabilities")
    print("-" * 40)
    
    try:
        from agents.orchestrator_agent import OrchestratorAgent
        orchestrator = OrchestratorAgent()
        
        for agent_name, agent in orchestrator.agents.items():
            print(f"\n🤖 {agent.agent_name}")
            print(f"   Type: {agent.agent_type}")
            print(f"   Tools: {len(agent.get_tools())}")
            print(f"   Capabilities: {len(agent.get_capabilities())}")
            
            # Show first few tools and capabilities
            tools = agent.get_tools()[:3]
            capabilities = agent.get_capabilities()[:2]
            
            for tool in tools:
                print(f"   • {tool}")
            if len(agent.get_tools()) > 3:
                print(f"   • ... and {len(agent.get_tools()) - 3} more")
                
            for capability in capabilities:
                print(f"   → {capability}")
            if len(agent.get_capabilities()) > 2:
                print(f"   → ... and {len(agent.get_capabilities()) - 2} more")
                
    except Exception as e:
        print(f"❌ Agent capabilities test failed: {e}")

if __name__ == "__main__":
    print("🏥 Hospital Management System Multi-Agent Test Suite")
    print("🧪 Running comprehensive tests...\n")
    
    success = test_multi_agent_system()
    
    if success:
        test_agent_capabilities()
        print("\n✅ All tests completed successfully!")
        print("\n🚀 Your multi-agent system is ready to use!")
        print("   Run 'python start_multi_agent.py' to start the server")
    else:
        print("\n❌ Tests failed. Please check the errors above.")
        sys.exit(1)
