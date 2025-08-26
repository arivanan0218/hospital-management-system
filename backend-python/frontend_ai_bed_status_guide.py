#!/usr/bin/env python3
"""
Create a comprehensive guide for frontend AI to use the correct bed status tool
"""

import requests
import json

def call_tool(name, arguments=None):
    """Call a tool via HTTP API"""
    if arguments is None:
        arguments = {}
    
    payload = {
        "method": "tools/call",
        "id": 1,
        "jsonrpc": "2.0",
        "params": {
            "name": name,
            "arguments": arguments
        }
    }
    
    response = requests.post('http://localhost:8000/tools/call', json=payload)
    
    if response.status_code == 200:
        result = response.json()
        if "result" in result:
            content = result["result"]
            if isinstance(content, dict) and "content" in content:
                content_list = content["content"]
                if isinstance(content_list, list) and len(content_list) > 0:
                    text_content = content_list[0].get("text", "")
                    try:
                        actual_result = json.loads(text_content)
                        if "result" in actual_result:
                            return actual_result["result"]
                        else:
                            return actual_result
                    except json.JSONDecodeError:
                        return {"error": "Failed to parse response", "raw": text_content}
            return content
        elif "error" in result:
            print(f"❌ Error calling {name}: {result['error']}")
            return None
    else:
        print(f"❌ HTTP Error {response.status_code} calling {name}")
        return None

def main():
    print("🏥 BED STATUS TOOL COMPARISON GUIDE")
    print("=" * 60)
    print("This guide shows the difference between bed status tools")
    print("and helps the frontend AI choose the correct one.")
    
    # Test bed 302A which should be in cleaning state
    bed_id = "302A"
    
    print(f"\n🛏️  TESTING BED {bed_id} STATUS:")
    print("=" * 40)
    
    # Method 1: Using check_bed_status (PREFERRED for individual bed status)
    print("\n1️⃣ USING check_bed_status (RECOMMENDED for discharge status)")
    print("   Use case: Check a specific bed's status after patient discharge")
    print("   Command: check_bed_status")
    
    result1 = call_tool("check_bed_status", {"bed_id": bed_id})
    if result1:
        print(f"   ✅ Result:")
        print(f"      Bed: {result1.get('bed_number', 'Unknown')}")
        print(f"      Status: {result1.get('current_status', 'Unknown')}")
        print(f"      Process: {result1.get('process_status', 'Unknown')}")
        print(f"      Time Remaining: {result1.get('time_remaining_minutes', 0)} minutes")
        print(f"      Progress: {result1.get('progress_percentage', 0):.1f}%")
    
    # Method 2: Using get_bed_status_with_time_remaining (DIRECT)
    print("\n2️⃣ USING get_bed_status_with_time_remaining (DIRECT)")
    print("   Use case: Same as above, but longer tool name")
    print("   Command: get_bed_status_with_time_remaining")
    
    result2 = call_tool("get_bed_status_with_time_remaining", {"bed_id": bed_id})
    if result2:
        print(f"   ✅ Result:")
        print(f"      Bed: {result2.get('bed_number', 'Unknown')}")
        print(f"      Status: {result2.get('current_status', 'Unknown')}")
        print(f"      Process: {result2.get('process_status', 'Unknown')}")
        print(f"      Time Remaining: {result2.get('time_remaining_minutes', 0)} minutes")
        print(f"      Progress: {result2.get('progress_percentage', 0):.1f}%")
    
    # Method 3: Using list_beds (WRONG CHOICE for individual bed status)
    print("\n3️⃣ USING list_beds (❌ WRONG for checking individual bed)")
    print("   Use case: List multiple beds - NOT for checking one bed's status")
    print("   Command: list_beds")
    
    result3 = call_tool("list_beds")
    if result3 and isinstance(result3, dict) and "data" in result3:
        beds = result3["data"]
        print(f"   📋 Lists {len(beds)} beds (too much information!)")
        
        # Find our specific bed in the list
        target_bed = None
        for bed in beds:
            if isinstance(bed, dict) and bed.get('bed_number') == bed_id:
                target_bed = bed
                break
        
        if target_bed:
            print(f"   Found {bed_id}: {target_bed.get('status', 'Unknown')} status")
            print(f"   ❌ Problem: No cleaning time remaining info!")
            print(f"   ❌ Problem: Returns ALL beds, not just the one requested")
    
    print(f"\n📋 FRONTEND AI GUIDANCE:")
    print("=" * 40)
    print("✅ FOR CHECKING BED STATUS AFTER DISCHARGE:")
    print("   Use: 'check_bed_status' with bed_id parameter")
    print("   Example: check_bed_status(bed_id='302A')")
    print("   Returns: Detailed status with cleaning time remaining")
    print("")
    print("❌ DON'T USE 'list_beds' for individual bed status:")
    print("   Problem: Returns ALL beds (unnecessary data)")
    print("   Problem: No cleaning time remaining information")
    print("   Problem: Less efficient for single bed queries")
    print("")
    print("✅ ALTERNATIVE:")
    print("   Use: 'get_bed_status_with_time_remaining' with bed_id parameter")
    print("   Same result as check_bed_status")
    
    print(f"\n🎯 RECOMMENDATION FOR FRONTEND AI:")
    print("When user asks to 'check bed status after discharge' or")
    print("'check bed 302A status', always use 'check_bed_status' tool")
    print("with the bed number as the bed_id parameter.")

if __name__ == "__main__":
    main()
