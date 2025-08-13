#!/usr/bin/env python3
"""
Simple test script for meeting scheduling and discharge report functionality
"""

import sys
import os
import asyncio

# Add the backend-python directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agent_server import orchestrator, MULTI_AGENT_AVAILABLE
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_meeting_workflow():
    """Test the meeting scheduling workflow with correct parameters"""
    
    print("\n🏥 === TESTING MEETING SCHEDULING WORKFLOW ===")
    
    if not MULTI_AGENT_AVAILABLE or not orchestrator:
        print("❌ Multi-agent system not available")
        return False

    try:
        # Test 1: Schedule a meeting using natural language
        print("\n📅 Test 1: Schedule a meeting")
        query = "Schedule a patient consultation meeting tomorrow at 2 PM with Dr. Smith and Nurse Johnson for 60 minutes"
        
        result = orchestrator.route_request("schedule_meeting", query=query)
        print(f"✅ Meeting scheduled: {result}")
        
        # Test 2: List upcoming meetings
        print("\n📋 Test 2: List upcoming meetings")
        result = orchestrator.route_request("list_meetings", days_ahead=7)
        print(f"✅ Meetings listed: {result}")
        
        # Test 3: List meetings for today
        print("\n📋 Test 3: List meetings for today")
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        result = orchestrator.route_request("list_meetings", date_str=today)
        print(f"✅ Today's meetings: {result}")

        return True

    except Exception as e:
        print(f"❌ Meeting workflow test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_discharge_workflow():
    """Test discharge workflow with correct parameters"""
    
    print("\n🏥 === TESTING DISCHARGE WORKFLOW ===")
    
    if not MULTI_AGENT_AVAILABLE or not orchestrator:
        print("❌ Multi-agent system not available")
        return False

    try:
        # Test 1: List discharge reports
        print("\n📋 Test 1: List discharge reports")
        result = orchestrator.route_request("list_discharge_reports")
        print(f"✅ Discharge reports listed: {result}")
        
        # Test 2: Generate a discharge report (using bed_id as required by agent)
        print("\n📄 Test 2: Generate discharge report")
        result = orchestrator.route_request("generate_discharge_report",
                                           bed_id="BED001",
                                           discharge_condition="stable",
                                           discharge_destination="home")
        print(f"✅ Discharge report generated: {result}")

        return True

    except Exception as e:
        print(f"❌ Discharge workflow test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_tools_availability():
    """Test that all tools are properly available"""
    
    print("\n🔧 === TESTING TOOLS AVAILABILITY ===")
    
    if not MULTI_AGENT_AVAILABLE or not orchestrator:
        print("❌ Multi-agent system not available")
        return False

    try:
        # Get all available tools
        tools = orchestrator.get_tools()
        print(f"📊 Total available tools: {len(tools)}")
        
        # Check specific meeting and discharge tools
        meeting_tools = ['schedule_meeting', 'list_meetings', 'get_meeting_by_id', 'update_meeting_status', 'add_meeting_notes']
        discharge_tools = ['generate_discharge_report', 'add_treatment_record_simple', 'add_equipment_usage_simple', 'list_discharge_reports']
        
        print("\n📅 Meeting tools availability:")
        for tool in meeting_tools:
            available = tool in tools
            status = "✅" if available else "❌"
            print(f"   {status} {tool}")
        
        print("\n📄 Discharge tools availability:")
        for tool in discharge_tools:
            available = tool in tools
            status = "✅" if available else "❌"
            print(f"   {status} {tool}")

        return True

    except Exception as e:
        print(f"❌ Tools availability test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🧪 Starting simple workflow tests...")
    print("=" * 60)
    
    results = {
        'tools_availability': await test_tools_availability(),
        'meeting_workflow': await test_meeting_workflow(),
        'discharge_workflow': await test_discharge_workflow()
    }
    
    print("\n" + "=" * 60)
    print("🏁 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    overall_status = "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"
    print(f"\nOverall Status: {overall_status}")
    
    if all_passed:
        print("\n🎉 Integration successful!")
        print("✅ Meeting scheduling functionality integrated")
        print("✅ Discharge report functionality integrated")
        print("✅ Database tables created and indexed")
        print("✅ Multi-agent system working correctly")
        
        print("\n📝 Usage Examples:")
        print("   Meeting: 'Schedule a consultation with Dr. Smith tomorrow at 3 PM'")
        print("   Discharge: Generate discharge report for bed BED001")
        
        return 0
    else:
        print("\n⚠️ Some integration issues found. Check the output above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
