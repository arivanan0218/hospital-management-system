#!/usr/bin/env python3
"""
Check existing users to see email structure
"""

import asyncio
import aiohttp
import json

async def check_user_emails():
    """Check how emails are stored in the system"""
    
    print("🔍 CHECKING USER EMAIL STRUCTURE")
    print("=" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Try list_users instead
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
                        print(f"✅ Found {len(users)} users")
                        
                        print("\n📧 Users with emails:")
                        email_users = []
                        for user in users:
                            email = user.get('email', '')
                            if email and email != 'no-email':
                                name = f"{user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}"
                                print(f"  📧 {name} - {email}")
                                email_users.append({
                                    'name': name,
                                    'email': email,
                                    'id': user.get('id', ''),
                                    'role': user.get('role', 'N/A')
                                })
                        
                        if email_users:
                            print(f"\n🎯 Perfect! Found {len(email_users)} users with valid emails")
                            
                            # Test targeted email to first 2 users
                            target_users = email_users[:2]
                            target_emails = [u['email'] for u in target_users]
                            
                            print(f"\n📧 Testing targeted emails to:")
                            for u in target_users:
                                print(f"  - {u['name']} - {u['email']}")
                            
                            # Send targeted meeting invitation
                            meeting_link = f"https://meet.google.com/xyz-abc-def"
                            
                            email_call = {
                                "method": "tools/call",
                                "params": {
                                    "name": "send_email",
                                    "arguments": {
                                        "to_emails": target_emails,
                                        "subject": "🎯 TARGETED Meeting Invitation: Frontend Test - August 14, 2025",
                                        "message": f"""Dear Team Member,

This is a TEST of the improved meeting workflow!

MEETING DETAILS (collected from user):
- Purpose: Frontend Testing Meeting
- Date: August 14, 2025  
- Time: 3:00 PM
- Duration: 30 minutes
- Location: Online (Google Meet)
- Google Meet Link: {meeting_link}

TARGETED PARTICIPANTS (only these people received this email):
{chr(10).join([f"- {u['name']} ({u['role']})" for u in target_users])}

🎯 SUCCESS: This email was sent ONLY to the {len(target_emails)} specified participants!
(Not to all {len(users)} users in the system)

This demonstrates the improved meeting workflow:
✅ System asks for complete meeting details
✅ System finds specific participants 
✅ System sends emails only to those participants
✅ System includes Google Meet link

Best regards,
Hospital AI - Improved Meeting System"""
                                    }
                                }
                            }
                            
                            async with session.post(
                                'http://localhost:8000/tools/call',
                                json=email_call,
                                headers={'Content-Type': 'application/json'}
                            ) as email_response:
                                if email_response.status == 200:
                                    email_result = await email_response.json()
                                    email_content = email_result['result']['content'][0]['text']
                                    email_data = json.loads(email_content)
                                    
                                    if email_data.get('success'):
                                        print(f"\n✅ TARGETED MEETING INVITATIONS SENT!")
                                        print(f"📊 Status: {email_data.get('message', 'Success')}")
                                        print(f"🎯 Recipients: {len(target_emails)} specific participants")
                                        print(f"🚫 NOT sent to all {len(users)} users")
                                        
                                        print(f"\n📋 MEETING SUMMARY:")
                                        print(f"  📝 Purpose: Frontend Testing Meeting")
                                        print(f"  📅 Date: August 14, 2025")
                                        print(f"  🕐 Time: 3:00 PM")
                                        print(f"  ⏱️ Duration: 30 minutes")
                                        print(f"  👥 Participants: {len(target_emails)} (TARGETED)")
                                        print(f"  🔗 Google Meet: {meeting_link}")
                                        print(f"  📧 Sent to:")
                                        for u in target_users:
                                            print(f"     ✉️ {u['name']} - {u['email']}")
                                    else:
                                        print(f"❌ Email failed: {email_data}")
                                else:
                                    print(f"❌ Email call failed: {email_response.status}")
                        else:
                            print("❌ No users with emails found")
                    else:
                        print(f"❌ Users list failed: {data}")
                else:
                    print(f"❌ Users API call failed: {response.status}")
                    
    except Exception as e:
        print(f"❌ Check failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 EMAIL STRUCTURE CHECK COMPLETE")

if __name__ == "__main__":
    asyncio.run(check_user_emails())
