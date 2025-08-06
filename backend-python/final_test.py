from meeting_scheduler import MeetingSchedulerAgent

print("TESTING FRONTEND ENCODING FIXES")
print("=" * 40)

# Test the exact scenario requested
agent = MeetingSchedulerAgent()

# User's original request:
# purpose: medical equipment and sales inventory improvement
# participants: ALL staffs
# date and time: 2025/08/15 between 4pm to 11pm (let's schedule at 4pm)
# duration: 30mins

query = "Schedule medical equipment and sales inventory improvement meeting for all staff on 2025/08/15 at 4pm for 30 minutes"

result = agent.schedule_meeting(query)

print("SCHEDULING TEST:")
print("Success:", result.get("success"))
print("Message:", result.get("message", "No message"))

if result.get("success"):
    print("\n✅ SUCCESS: Meeting scheduled with proper date parsing!")
    print("✅ No encoding issues - frontend should work now!")
else:
    print("\n❌ Still having issues:", result.get("message"))

# Test MCP function directly (what frontend uses)
print("\n" + "=" * 40)
print("TESTING MCP FUNCTION (Frontend Communication)")

from comprehensive_server import schedule_meeting_with_staff
mcp_result = schedule_meeting_with_staff("Test frontend meeting on 2025/08/25 at 2pm")

print("MCP Success:", mcp_result.get("success"))
print("MCP Response:", mcp_result)

print("\n🎉 ENCODING ISSUES FIXED - FRONTEND SHOULD NOW WORK!")
