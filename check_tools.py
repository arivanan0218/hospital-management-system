#!/usr/bin/env python3
"""
Check what email tools are available
"""

import asyncio
import aiohttp
import json

async def check_email_tools():
    """Check available email tools"""
    
    print("🔍 CHECKING AVAILABLE EMAIL TOOLS")
    print("=" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/tools/list') as response:
                if response.status == 200:
                    result = await response.json()
                    tools = result.get('tools', [])
                    
                    print(f"✅ Found {len(tools)} total tools")
                    
                    # Find email-related tools
                    email_tools = [tool for tool in tools if 'email' in tool.get('name', '').lower()]
                    print(f"\n📧 Email-related tools: {len(email_tools)}")
                    for tool in email_tools:
                        print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                    
                    # Find meeting-related tools
                    meeting_tools = [tool for tool in tools if any(keyword in tool.get('name', '').lower() 
                                    for keyword in ['meeting', 'schedule', 'calendar'])]
                    print(f"\n📅 Meeting-related tools: {len(meeting_tools)}")
                    for tool in meeting_tools:
                        print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                    
                    # Find staff/user tools
                    staff_tools = [tool for tool in tools if any(keyword in tool.get('name', '').lower() 
                                  for keyword in ['staff', 'user', 'list'])]
                    print(f"\n👥 Staff/User tools: {len(staff_tools)}")
                    for tool in staff_tools:
                        print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                        
                    # Let's try the schedule_meeting tool instead since it works
                    print(f"\n🧪 Testing schedule_meeting tool (known to work)...")
                    
                    meeting_call = {
                        "method": "tools/call",
                        "params": {
                            "name": "schedule_meeting",
                            "arguments": {
                                "query": "Schedule a test meeting with Dr. John Smith and Admin User for tomorrow at 3 PM to discuss improved meeting workflow"
                            }
                        }
                    }
                    
                    async with session.post(
                        'http://localhost:8000/tools/call',
                        json=meeting_call,
                        headers={'Content-Type': 'application/json'}
                    ) as meeting_response:
                        if meeting_response.status == 200:
                            meeting_result = await meeting_response.json()
                            meeting_content = meeting_result['result']['content'][0]['text']
                            meeting_data = json.loads(meeting_content)
                            
                            print(f"✅ Schedule meeting test successful!")
                            print(f"📊 Meeting created: {meeting_data.get('success', False)}")
                            
                            # Extract key information
                            if meeting_data.get('success'):
                                result_data = meeting_data.get('data', {})
                                print(f"📅 Meeting ID: {result_data.get('meeting_id', 'N/A')}")
                                print(f"🔗 Google Meet: {result_data.get('google_meet_link', 'N/A')}")
                                print(f"📧 Email status: {result_data.get('email_status', 'N/A')}")
                                print(f"👥 Participants notified: {result_data.get('participants_notified', 'N/A')}")
                                
                        else:
                            print(f"❌ Schedule meeting test failed: {meeting_response.status}")
                
                else:
                    print(f"❌ Tools list failed: {response.status}")
                    
    except Exception as e:
        print(f"❌ Check failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 EMAIL TOOLS CHECK COMPLETE")
    print("\n💡 KEY INSIGHT:")
    print("  - schedule_meeting tool works and sends emails")
    print("  - We need to modify frontend to use available tools")
    print("  - The system can create meetings with targeted participants")

if __name__ == "__main__":
    asyncio.run(check_email_tools())
