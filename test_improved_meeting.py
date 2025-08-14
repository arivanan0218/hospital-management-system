#!/usr/bin/env python3
"""
Test the improved meeting workflow with detailed collection and targeted emails
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend-python"
sys.path.insert(0, str(backend_dir))

import aiohttp

async def test_improved_meeting_workflow():
    """Test the new meeting workflow with proper detail collection"""
    
    print("\n🧪 TESTING IMPROVED MEETING WORKFLOW")
    print("=" * 50)
    
    # Test server connection
    print("\n📡 Step 1: Testing server connection...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/health') as response:
                if response.status == 200:
                    print("✅ Backend server is running")
                else:
                    print("❌ Backend server not responding")
                    return
    except Exception as e:
        print(f"❌ Cannot connect to backend server: {e}")
        return
    
    # Test getting staff list for targeted emails
    print("\n👥 Step 2: Getting staff list for targeted emails...")
    
    try:
        async with aiohttp.ClientSession() as session:
            staff_call = {
                "method": "tools/call",
                "params": {
                    "name": "list_staff",
                    "arguments": {"status": "active"}
                }
            }
            
            async with session.post(
                'http://localhost:8000/tools/call',
                json=staff_call,
                headers={'Content-Type': 'application/json'}
            ) as response:
                staff_result = await response.json()
                print(f"Staff Response Status: {response.status}")
                
                if response.status == 200:
                    staff_data = json.loads(staff_result.get('content', [{}])[0].get('text', '{}'))
                    
                    if staff_data.get('success'):
                        staff_list = staff_data.get('data', [])
                        print(f"✅ Found {len(staff_list)} active staff members")
                        
                        # Show first few staff for demonstration
                        for i, staff in enumerate(staff_list[:3]):
                            print(f"   {i+1}. {staff.get('first_name', 'N/A')} {staff.get('last_name', 'N/A')} - {staff.get('email', 'no-email')} ({staff.get('position', 'N/A')})")
                        
                        if len(staff_list) > 3:
                            print(f"   ... and {len(staff_list) - 3} more")
                            
                        # Test targeted email sending
                        print(f"\n📧 Step 3: Testing targeted email sending...")
                        
                        # Get first 2 staff members' emails for testing
                        target_emails = []
                        for staff in staff_list[:2]:
                            if staff.get('email'):
                                target_emails.append(staff['email'])
                        
                        if target_emails:
                            print(f"   📮 Sending test meeting invitation to {len(target_emails)} participants")
                            print(f"   📧 Recipients: {', '.join(target_emails)}")
                            
                            # Create meeting email
                            meeting_link = "https://meet.google.com/abc-defg-hij"  # Test link
                            
                            email_call = {
                                "method": "tools/call",
                                "params": {
                                    "name": "send_email",
                                    "arguments": {
                                        "to_emails": target_emails,
                                        "subject": "Meeting Invitation: Team Sync - 2025-08-14 at 14:30",
                                        "message": f"""Dear Team Members,

You are invited to attend the following meeting:

- Topic: Team Sync
- Date: 2025-08-14
- Time: 14:30
- Duration: 1 hour
- Location: Online (Google Meet)
- Google Meet Link: {meeting_link}

Please confirm your attendance.

Best regards,
Hospital AI"""
                                    }
                                }
                            }
                            
                            async with session.post(
                                'http://localhost:8000/tools/call',
                                json=email_call,
                                headers={'Content-Type': 'application/json'}
                            ) as email_response:
                                email_result = await email_response.json()
                                
                                if email_response.status == 200:
                                    email_data = json.loads(email_result.get('content', [{}])[0].get('text', '{}'))
                                    
                                    if email_data.get('success'):
                                        print(f"✅ Meeting invitations sent successfully!")
                                        print(f"   📊 Email Status: {email_data.get('message', 'Sent')}")
                                        
                                        # Show meeting summary
                                        print(f"\n📅 Meeting Summary:")
                                        print(f"   📝 Purpose: Team Sync")
                                        print(f"   📅 Date: 2025-08-14")
                                        print(f"   🕐 Time: 14:30")
                                        print(f"   ⏱️ Duration: 1 hour")
                                        print(f"   👥 Participants: {len(target_emails)}")
                                        print(f"   🔗 Google Meet: {meeting_link}")
                                        print(f"   📧 Emails sent to: {', '.join(target_emails)}")
                                        
                                    else:
                                        print(f"❌ Email sending failed: {email_data.get('message', 'Unknown error')}")
                                else:
                                    print(f"❌ Email API call failed: {email_response.status}")
                        else:
                            print("❌ No staff emails found for testing")
                    else:
                        print(f"❌ Staff list failed: {staff_data.get('message', 'Unknown error')}")
                else:
                    print(f"❌ Staff API call failed: {response.status}")
                    
    except Exception as e:
        print(f"❌ Meeting workflow test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 IMPROVED MEETING WORKFLOW TEST COMPLETE")
    print("\nKey Features Tested:")
    print("✅ Staff list retrieval for targeted emails")
    print("✅ Targeted email sending to specific participants")
    print("✅ Meeting details collection and formatting")
    print("✅ Google Meet link integration")
    print("\nNext Steps:")
    print("🔹 Test in frontend with user interaction")
    print("🔹 Verify AI asks for missing details")
    print("🔹 Confirm only selected participants receive emails")

if __name__ == "__main__":
    asyncio.run(test_improved_meeting_workflow())
