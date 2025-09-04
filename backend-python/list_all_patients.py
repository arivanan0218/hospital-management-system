"""
List all patients to see what's in the database
"""

import requests
import json

def list_all_patients():
    """List all patients in the database"""
    
    print("📋 LISTING ALL PATIENTS")
    print("=" * 30)
    
    base_url = "http://127.0.0.1:8000/tools/call"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "list_patients",
            "arguments": {}
        }
    }
    
    try:
        response = requests.post(base_url, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            content = result.get("result", {}).get("content", [])
            if content:
                response_text = content[0].get("text", "{}")
                data = json.loads(response_text)
                
                if data.get("success"):
                    patients = data.get("patients", [])
                    print(f"✅ Found {len(patients)} total patients:")
                    
                    for i, patient in enumerate(patients[-10:], 1):  # Show last 10 patients
                        print(f"\n{i}. {patient.get('first_name', '')} {patient.get('last_name', '')}")
                        print(f"   Patient Number: {patient.get('patient_number', 'NONE')}")
                        print(f"   Patient ID: {patient.get('id', 'NONE')}")
                        print(f"   Status: {patient.get('status', 'NONE')}")
                        print(f"   Created: {patient.get('created_at', 'NONE')}")
                        
                        # Check if this is one of our test patients
                        if patient.get('first_name') in ['StaffTest', 'FullDebug']:
                            print(f"   🎯 This is a test patient!")
                    
                    if len(patients) > 10:
                        print(f"\n... and {len(patients) - 10} more patients (showing last 10)")
                else:
                    print(f"❌ List failed: {data.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    list_all_patients()
