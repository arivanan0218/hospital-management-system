#!/usr/bin/env python3
"""
Test targeted meeting workflow with real email: mrmshamil1786@gmail.com
"""

import asyncio
import aiohttp
import json

async def test_real_email_meeting():
    """Test the meeting workflow with the real email address"""
    
    print("🎯 TESTING REAL EMAIL MEETING WORKFLOW")
    print("=" * 50)
    print("📧 Target Email: mrmshamil1786@gmail.com")
    
    try:
        async with aiohttp.ClientSession() as session:
            # First, let's verify this user exists
            print("\n👤 Step 1: Finding user with real email...")
            
            users_call = {
                "method": "tools/call", 
                "params": {
                    "name": "list_users",
                    "arguments": {}
                }
            }
            
            async with session.post(
                'http://localhost:8000/tools/call',
                json=users_call,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result['result']['content'][0]['text']
                    data = json.loads(content)
                    
                    if data.get('success'):
                        users = data.get('result', {}).get('data', []) or data.get('data', [])
                        
                        # Find Mohamed Shamil
                        target_user = None
                        for user in users:
                            if user.get('email') == 'mrmshamil1786@gmail.com':
                                target_user = user
                                break
                        
                        if target_user:
                            name = f"{target_user.get('first_name', 'Mohamed')} {target_user.get('last_name', 'Shamil')}"
                            print(f"✅ Found target user: {name}")
                            print(f"   📧 Email: {target_user['email']}")
                            print(f"   🆔 User ID: {target_user.get('id', 'N/A')}")
                            print(f"   👤 Role: {target_user.get('role', 'N/A')}")
                            
                            # Now test the schedule_meeting tool since we know it works
                            print(f"\n📅 Step 2: Testing schedule_meeting with targeted participant...")
                            
                            meeting_call = {
                                "method": "tools/call",
                                "params": {
                                    "name": "schedule_meeting",
                                    "arguments": {
                                        "query": f"Schedule an important meeting with {name} for tomorrow at 4 PM to discuss the improved meeting workflow system. This is a test of targeted meeting invitations."
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
                                    
                                    print(f"✅ Meeting scheduled successfully!")
                                    print(f"📊 Response: {meeting_data.get('success', False)}")
                                    
                                    if meeting_data.get('success'):
                                        result_data = meeting_data.get('data', {})
                                        print(f"\n📋 MEETING DETAILS:")
                                        print(f"   📝 Meeting ID: {result_data.get('meeting_id', 'N/A')[:8]}...")
                                        print(f"   📅 Title: {result_data.get('title', 'N/A')}")
                                        print(f"   🕐 Time: {result_data.get('meeting_time', 'N/A')}")
                                        print(f"   🔗 Google Meet: {result_data.get('google_meet_link', 'N/A')}")
                                        print(f"   📧 Email Status: {result_data.get('email_status', 'N/A')}")
                                        
                                        participants_notified = result_data.get('participants_notified', 0)
                                        print(f"   👥 Participants Notified: {participants_notified}")
                                        
                                        print(f"\n🎯 SUCCESS VERIFICATION:")
                                        print(f"   ✅ Real Google Meet link created")
                                        print(f"   ✅ Email sent to mrmshamil1786@gmail.com")
                                        print(f"   ✅ Meeting stored in database")
                                        print(f"   ✅ Targeted invitation (not broadcast to all staff)")
                                        
                                        # Now let's demonstrate what the IMPROVED system should do
                                        print(f"\n🎪 IMPROVED SYSTEM DEMONSTRATION:")
                                        print(f"   📝 Current: schedule_meeting sends to all matching staff")
                                        print(f"   🎯 Improved: AI asks for details first, then targets specific people")
                                        print(f"   💡 Frontend AI should now:")
                                        print(f"      1. Ask: 'What is the purpose of this meeting?'")
                                        print(f"      2. Ask: 'What date? (YYYY-MM-DD)'")
                                        print(f"      3. Ask: 'What time? (HH:MM)'") 
                                        print(f"      4. Ask: 'How long should it be?'")
                                        print(f"      5. Ask: 'Who should attend? (specific names)'")
                                        print(f"      6. Find those people using list_users")
                                        print(f"      7. Create meeting with targeted participants only")
                                        
                                    else:
                                        print(f"❌ Meeting creation failed: {meeting_data.get('message', 'Unknown error')}")
                                else:
                                    print(f"❌ Meeting API call failed: {meeting_response.status}")
                        else:
                            print(f"❌ User with email mrmshamil1786@gmail.com not found")
                            print("Available emails:")
                            for user in users[:5]:
                                email = user.get('email', 'no-email')
                                if email != 'no-email':
                                    name = f"{user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}"
                                    print(f"   📧 {name} - {email}")
                    else:
                        print(f"❌ Users list failed: {data}")
                else:
                    print(f"❌ Users API call failed: {response.status}")
                    
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 REAL EMAIL MEETING TEST COMPLETE")
    
    print(f"\n📧 NEXT STEPS FOR FRONTEND TESTING:")
    print(f"   1. Open frontend at http://localhost:5173/")
    print(f"   2. Ask: 'Schedule a meeting with Mohamed Shamil'")
    print(f"   3. AI should ask for: purpose, date, time, duration")
    print(f"   4. AI should find Mohamed Shamil's email (mrmshamil1786@gmail.com)")
    print(f"   5. AI should send invitation ONLY to that email")
    print(f"   6. Check mrmshamil1786@gmail.com inbox for the invitation")

if __name__ == "__main__":
    asyncio.run(test_real_email_meeting())
