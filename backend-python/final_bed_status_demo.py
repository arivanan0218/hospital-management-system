#!/usr/bin/env python3
"""
Final demonstration: Why frontend AI must use get_bed_status_with_time_remaining for bed status queries
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
    return None

def main():
    print("🚨 CRITICAL: Frontend AI Tool Selection Issue")
    print("=" * 60)
    print("User asked: 'check bed 302A status'")
    print()
    
    # Show the WRONG tool (what frontend AI is currently using)
    print("❌ WRONG TOOL: list_beds")
    print("   Result: 'bed 302A not found in list'")
    result1 = call_tool("list_beds")
    if result1 and isinstance(result1, dict) and "data" in result1:
        beds = result1["data"]
        bed_302a = None
        for bed in beds:
            if isinstance(bed, dict) and bed.get('bed_number') == '302A':
                bed_302a = bed
                break
        
        if bed_302a:
            print(f"   Found 302A with basic status: {bed_302a.get('status')}")
            print("   ❌ Missing: No cleaning time remaining!")
        else:
            print("   ❌ Problem: Bed 302A not in the list (likely filtered out)")
    
    print()
    
    # Show the CORRECT tool
    print("✅ CORRECT TOOL: get_bed_status_with_time_remaining")
    result2 = call_tool("get_bed_status_with_time_remaining", {"bed_id": "302A"})
    if result2 and result2.get("success"):
        print("   ✅ SUCCESS - Complete bed information:")
        print(f"      Bed: {result2.get('bed_number')}")
        print(f"      Status: {result2.get('current_status')}")
        print(f"      Process: {result2.get('process_status')}")
        print(f"      Time Remaining: {result2.get('time_remaining_minutes')} minutes")
        print(f"      Progress: {result2.get('progress_percentage'):.1f}%")
        print(f"      Room: {result2.get('room_number')}")
    
    print()
    print("🎯 SOLUTION FOR FRONTEND AI:")
    print("=" * 40)
    print("When user asks 'check bed 302A status', ALWAYS use:")
    print("   get_bed_status_with_time_remaining(bed_id='302A')")
    print()
    print("NEVER use list_beds for individual bed status queries!")

if __name__ == "__main__":
    main()
