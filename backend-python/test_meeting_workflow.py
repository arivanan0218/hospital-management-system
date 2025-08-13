"""Test meeting scheduling workflow to debug frontend issues."""

import json
import sys
import asyncio
from datetime import datetime, timedelta

# Test the multi-agent server directly
def test_multi_agent_connection():
    """Test if multi-agent server components are working."""
    print("🧪 Testing Multi-Agent Server Components")
    print("=" * 50)
    
    # Test database availability
    try:
        from database import DATABASE_AVAILABLE, SessionLocal
        print(f"✅ Database Available: {DATABASE_AVAILABLE}")
        if DATABASE_AVAILABLE:
            db = SessionLocal()
            print("✅ Database connection successful")
            db.close()
    except Exception as e:
        print(f"❌ Database Error: {e}")
    
    # Test multi-agent system
    try:
        from agents.orchestrator_agent import OrchestratorAgent
        orchestrator = OrchestratorAgent()
        print(f"✅ Orchestrator initialized with {len(orchestrator.agents)} agents")
        print(f"✅ Total tools available: {len(orchestrator.get_tools())}")
        
        # List available agents
        for agent_name, agent in orchestrator.agents.items():
            print(f"   - {agent_name}: {len(agent.get_tools())} tools")
        
        return orchestrator
    except Exception as e:
        print(f"❌ Multi-agent system error: {e}")
        return None

def test_meeting_scheduling(orchestrator):
    """Test meeting scheduling functionality."""
    print("\n🗓️ Testing Meeting Scheduling")
    print("=" * 50)
    
    if not orchestrator:
        print("❌ No orchestrator available")
        return
    
    # Test 1: List staff first
    print("\n1. Testing list_staff...")
    try:
        result = orchestrator.route_request("list_staff")
        print(f"✅ list_staff result: {json.dumps(result, indent=2)[:200]}...")
    except Exception as e:
        print(f"❌ list_staff error: {e}")
    
    # Test 2: Schedule meeting with the exact query from frontend
    print("\n2. Testing schedule_meeting...")
    test_query = "i need to schedule a meeting with all the staffs today to discuss about 'Tasks Improvements'..by arranging the online meeting and can you send all the staffs confirmation emails.."
    
    try:
        result = orchestrator.route_request("schedule_meeting", query=test_query)
        print(f"✅ schedule_meeting result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ schedule_meeting error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

def test_email_functionality():
    """Test email functionality directly."""
    print("\n📧 Testing Email Functionality")
    print("=" * 50)
    
    try:
        from meeting_scheduler import MeetingSchedulerAgent
        scheduler = MeetingSchedulerAgent()
        print("✅ MeetingSchedulerAgent initialized")
        
        # Check email configuration
        print(f"📧 Email server: {scheduler.email_server}")
        print(f"📧 Email port: {scheduler.email_port}")
        print(f"📧 Email username configured: {'Yes' if scheduler.email_username else 'No'}")
        print(f"📧 Email password configured: {'Yes' if scheduler.email_password else 'No'}")
        
    except Exception as e:
        print(f"❌ Email system error: {e}")

def test_google_meet_integration():
    """Test Google Meet API integration."""
    print("\n🎥 Testing Google Meet Integration")
    print("=" * 50)
    
    try:
        from google_meet_api import GoogleMeetAPIIntegration
        meet_api = GoogleMeetAPIIntegration()
        print("✅ Google Meet API initialized")
        
        # Test creating a meeting
        test_result = meet_api.create_meeting(
            title="Test Meeting",
            start_time=datetime.now() + timedelta(hours=1),
            duration_minutes=60
        )
        print(f"✅ Google Meet test result: {test_result}")
        
    except Exception as e:
        print(f"❌ Google Meet error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

def test_tool_parameters():
    """Test tool parameter structures."""
    print("\n🔧 Testing Tool Parameter Structures")
    print("=" * 50)
    
    # Test what parameters each tool expects
    try:
        from multi_agent_server import mcp
        
        tools = mcp.tools
        print(f"✅ Found {len(tools)} tools in MCP server")
        
        # Check specific tools that were failing
        meeting_tools = ['list_staff', 'schedule_meeting', 'send_email', 'list_users']
        
        for tool_name in meeting_tools:
            if tool_name in tools:
                tool = tools[tool_name]
                print(f"\n🔧 {tool_name}:")
                print(f"   Description: {tool.description}")
                if hasattr(tool, 'input_schema'):
                    print(f"   Parameters: {tool.input_schema}")
                else:
                    print("   Parameters: No schema available")
            else:
                print(f"❌ Tool '{tool_name}' not found in MCP tools")
                
    except Exception as e:
        print(f"❌ Tool parameter test error: {e}")

def main():
    """Run all tests."""
    print("🏥 Hospital Management System - Meeting Workflow Test")
    print("=" * 60)
    
    # Test 1: Multi-agent connection
    orchestrator = test_multi_agent_connection()
    
    # Test 2: Meeting scheduling
    test_meeting_scheduling(orchestrator)
    
    # Test 3: Email functionality
    test_email_functionality()
    
    # Test 4: Google Meet integration
    test_google_meet_integration()
    
    # Test 5: Tool parameters
    test_tool_parameters()
    
    print("\n" + "=" * 60)
    print("🔍 Test Complete - Check results above for issues")

if __name__ == "__main__":
    main()
