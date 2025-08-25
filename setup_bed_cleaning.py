#!/usr/bin/env python3

import requests
import json

def setup_bed_cleaning():
    """Setup bed 401A for cleaning demonstration"""
    
    url = "http://localhost:8000/tools/call"
    
    # First, get the actual bed UUID for bed 401A
    bed_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_bed_by_number",
            "arguments": {
                "bed_number": "401A"
            }
        },
        "id": 1
    }
    
    try:
        print("🔍 Getting bed 401A details...")
        bed_response = requests.post(url, json=bed_payload, timeout=10)
        
        if bed_response.status_code == 200:
            bed_result = bed_response.json()
            print(f"📥 Bed Response: {json.dumps(bed_result, indent=2)}")
            
            # Parse the nested JSON response
            if "result" in bed_result and "content" in bed_result["result"]:
                content = bed_result["result"]["content"][0]["text"]
                bed_data = json.loads(content)
                
                if bed_data.get("success") and "result" in bed_data:
                    bed_info = bed_data["result"]
                    if "data" in bed_info:
                        bed_details = bed_info["data"]
                        bed_uuid = bed_details.get("id")
                        print(f"✅ Found bed UUID: {bed_uuid}")
                    else:
                        bed_uuid = bed_info.get("id")
                        print(f"✅ Found bed UUID: {bed_uuid}")
                    
                    # Now start cleaning process with the correct bed UUID
                    if bed_uuid:
                        # Update bed status to cleaning
                        update_payload = {
                            "jsonrpc": "2.0",
                            "method": "tools/call", 
                            "params": {
                                "name": "update_bed_status",
                                "arguments": {
                                    "bed_id": bed_uuid,
                                    "new_status": "cleaning"
                                }
                            },
                            "id": 2
                        }
                        
                        print("\n🧹 Setting bed to cleaning status...")
                        update_response = requests.post(url, json=update_payload, timeout=10)
                        
                        if update_response.status_code == 200:
                            update_result = update_response.json()
                            print(f"📥 Update Response: {json.dumps(update_result, indent=2)}")
                        
                        # Check final status
                        check_payload = {
                            "jsonrpc": "2.0",
                            "method": "tools/call",
                            "params": {
                                "name": "get_bed_status_with_time_remaining",
                                "arguments": {
                                    "bed_id": "401A"
                                }
                            },
                            "id": 3
                        }
                        
                        print("\n🔍 Checking final bed status...")
                        status_response = requests.post(url, json=check_payload, timeout=10)
                        
                        if status_response.status_code == 200:
                            status_result = status_response.json()
                            print(f"📥 Final Status: {json.dumps(status_result, indent=2)}")
                        
                else:
                    print("❌ Failed to get bed details")
            else:
                print("❌ Invalid response format")
                
        else:
            print(f"❌ Failed to get bed: {bed_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    setup_bed_cleaning()
