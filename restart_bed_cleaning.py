#!/usr/bin/env python3

import requests
import json

def restart_bed_cleaning():
    """Restart the bed cleaning process for bed 401A"""
    
    # First, start the turnover process
    url = "http://localhost:8000/tools/call"
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "start_bed_turnover_process",
            "arguments": {
                "bed_id": "401A",
                "previous_patient_id": "c8e2c3f1-4b6a-4d8e-9f2e-8a7b6c5d4e3f",
                "discharge_reason": "Discharged"
            }
        },
        "id": 1
    }
    
    try:
        print("🧹 Starting bed turnover process for bed 401A...")
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"📥 Turnover Response: {json.dumps(result, indent=2)}")
            
            # Now check the status again
            check_payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "get_bed_status_with_time_remaining",
                    "arguments": {
                        "bed_id": "401A"
                    }
                },
                "id": 2
            }
            
            print("\n🔍 Checking bed status after turnover...")
            status_response = requests.post(url, json=check_payload, timeout=10)
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                print(f"📥 Status Response: {json.dumps(status_result, indent=2)}")
            else:
                print(f"❌ Status check failed: {status_response.status_code}")
                
        else:
            print(f"❌ Turnover failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    restart_bed_cleaning()
