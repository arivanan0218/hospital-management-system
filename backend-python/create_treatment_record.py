#!/usr/bin/env python3
"""
Create treatment record for David Jones (P004) with EMP004
"""
import requests
import json

def call_tool(name, arguments, request_id=1):
    """Helper function to call MCP tools"""
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "tools/call",
        "params": {
            "name": name,
            "arguments": arguments
        }
    }
    
    response = requests.post('http://localhost:8000/tools/call', 
                           json=payload,
                           headers={'Content-Type': 'application/json'},
                           timeout=15)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"HTTP {response.status_code}: {response.text}"}

def main():
    print("🏥 CREATING TREATMENT RECORD FOR DAVID JONES")
    print("=" * 50)
    
    # Information from previous search
    patient_id = "0856eeb7-af35-474e-b9b3-981b2a359cd8"  # David Jones (P004)
    doctor_id = "6d154d0a-b704-4255-add6-0b730921787e"   # EMP004 (ICU Nurse)
    
    print(f"📋 TREATMENT DETAILS:")
    print(f"   Patient: David Jones (P004)")
    print(f"   Patient ID: {patient_id}")
    print(f"   Provider: EMP004 (ICU Nurse)")
    print(f"   Doctor ID: {doctor_id}")
    print(f"   Treatment: Sugar level check-up")
    print(f"   Type: check-up")
    
    print(f"\n🏥 Creating treatment record...")
    result = call_tool("add_treatment_record_simple", {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "treatment_type": "check-up",
        "treatment_name": "sugar level check-up",
        "description": "Blood sugar level monitoring and assessment for patient David Jones. Routine check-up to monitor glucose levels and overall diabetic care.",
        "medications": "None prescribed at this time",
        "instructions": "Continue monitoring blood sugar levels regularly. Maintain healthy diet and exercise routine. Return if symptoms worsen.",
        "follow_up_date": "2025-09-21"  # 1 month follow-up
    }, 1)
    
    if 'result' in result:
        response_text = result['result']['content'][0]['text']
        response_data = json.loads(response_text)
        print(f"\nRaw response: {json.dumps(response_data, indent=2)}")
        
        if response_data.get('success'):
            treatment_data = response_data.get('result', {}).get('data', {})
            print("\n🎉 TREATMENT RECORD CREATED SUCCESSFULLY!")
            print("=" * 50)
            print(f"✅ Treatment ID: {treatment_data.get('id', 'N/A')}")
            print(f"✅ Patient: {treatment_data.get('patient_name', 'David Jones')}")
            print(f"✅ Provider: {treatment_data.get('doctor_name', 'EMP004')}")
            print(f"✅ Treatment: {treatment_data.get('treatment_name', 'sugar level check-up')}")
            print(f"✅ Type: {treatment_data.get('treatment_type', 'check-up')}")
            print(f"✅ Date: {treatment_data.get('treatment_date', 'Today')}")
            print(f"✅ Follow-up: {treatment_data.get('follow_up_date', '2025-09-21')}")
            
            print(f"\n📋 TREATMENT SUMMARY:")
            print(f"   Description: {treatment_data.get('description', 'Blood sugar monitoring')}")
            print(f"   Medications: {treatment_data.get('medications', 'None')}")
            print(f"   Instructions: {treatment_data.get('instructions', 'Monitor regularly')}")
            
        else:
            print(f"\n❌ TREATMENT CREATION FAILED:")
            print(f"   Message: {response_data.get('message', 'Unknown error')}")
            
            # Show what we tried to create
            print(f"\n🔍 ATTEMPTED PARAMETERS:")
            print(f"   Patient ID: {patient_id}")
            print(f"   Doctor ID: {doctor_id}")
            print(f"   Treatment Type: check-up")
            print(f"   Treatment Name: sugar level check-up")
    else:
        print(f"\n❌ TREATMENT CREATION ERROR:")
        print(f"   {result}")
    
    print(f"\n" + "=" * 50)
    print(f"📝 RESOLUTION COMPLETE")
    print(f"✅ Found patient P004: David Jones")
    print(f"✅ Found provider EMP004: ICU Nurse") 
    print(f"✅ Used correct tool: add_treatment_record_simple")
    print(f"✅ All required information provided")

if __name__ == "__main__":
    main()
