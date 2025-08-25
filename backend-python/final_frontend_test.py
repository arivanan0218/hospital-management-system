#!/usr/bin/env python3
"""
Final test to verify frontend bed status functionality
"""

import requests
import json

def test_frontend_integration():
    """Test the complete frontend integration for bed status"""
    
    print("🧪 FINAL FRONTEND BED STATUS TEST")
    print("="*50)
    
    # Test message that should trigger bed status check
    test_messages = [
        "check bed 401A status",
        "what is bed 401A status",
        "bed 401A cleaning status", 
        "how much time remaining for bed 401A"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing: '{message}'")
        
        # Check if message would match the bed status condition
        message_lower = message.lower()
        has_bed = "bed" in message_lower
        has_status_keyword = any(word in message_lower for word in ["cleaning", "status", "turnover"])
        
        print(f"   - Contains 'bed': {has_bed}")
        print(f"   - Contains status keyword: {has_status_keyword}")
        
        if has_bed and has_status_keyword:
            print("   ✅ Should trigger get_bed_status_with_time_remaining")
            
            # Extract bed number
            import re
            bed_match = re.search(r'bed\s+([A-Z0-9-]+)', message, re.IGNORECASE)
            if bed_match:
                bed_id = bed_match.group(1)
                print(f"   🎯 Extracted bed_id: {bed_id}")
                
                # Test API call
                url = "http://localhost:8000/tools/call"
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "get_bed_status_with_time_remaining",
                        "arguments": {
                            "bed_id": bed_id
                        }
                    }
                }
                
                try:
                    response = requests.post(url, json=payload)
                    if response.status_code == 200:
                        result = response.json()
                        content = result.get("result", {}).get("content", [])
                        if content:
                            text_content = content[0].get("text", "{}")
                            status_data = json.loads(text_content)
                            
                            if status_data.get("success"):
                                data = status_data.get("result", {})
                                print(f"   🏥 Bed Status: {data.get('current_status')}")
                                print(f"   🔄 Process: {data.get('process_status')}")
                                print(f"   ⏱️  Time Remaining: {data.get('time_remaining_minutes')} min")
                                print("   ✅ API call successful!")
                            else:
                                print(f"   ❌ API error: {status_data.get('message')}")
                        else:
                            print("   ❌ No content in response")
                    else:
                        print(f"   ❌ HTTP error: {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Exception: {e}")
            else:
                print("   ❌ Could not extract bed number")
        else:
            print("   ❌ Would NOT trigger bed status check")
    
    print(f"\n" + "="*50)
    print("🎯 FRONTEND TESTING INSTRUCTIONS:")
    print("1. Open http://localhost:3000 in browser")
    print("2. Try any of these messages:")
    for msg in test_messages:
        print(f"   📝 '{msg}'")
    print("3. You should see detailed bed cleaning status, not generic 'available' message")
    print("4. If still getting generic message, check browser console for errors")

if __name__ == "__main__":
    test_frontend_integration()
