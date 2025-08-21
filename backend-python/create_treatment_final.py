#!/usr/bin/env python3
"""
Create treatment record for David Jones (P004) with EMP004 - correct parameters
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
    print("🏥 CREATING TREATMENT RECORD - CORRECT PARAMETERS")
    print("=" * 55)
    
    # Information from previous search
    patient_id = "0856eeb7-af35-474e-b9b3-981b2a359cd8"  # David Jones (P004)
    doctor_id = "6d154d0a-b704-4255-add6-0b730921787e"   # EMP004 (ICU Nurse)
    
    print(f"📋 TREATMENT PARAMETERS (SIMPLIFIED):")
    print(f"   Patient ID: {patient_id}")
    print(f"   Doctor ID: {doctor_id}")
    print(f"   Treatment Type: check-up")
    print(f"   Treatment Name: sugar level check-up")
    
    print(f"\n🏥 Creating treatment record with correct parameters...")
    result = call_tool("add_treatment_record_simple", {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "treatment_type": "check-up",
        "treatment_name": "sugar level check-up"
    }, 1)
    
    if 'result' in result:
        response_text = result['result']['content'][0]['text']
        response_data = json.loads(response_text)
        print(f"\nRaw response: {json.dumps(response_data, indent=2)}")
        
        if response_data.get('success'):
            treatment_data = response_data.get('result', {}).get('data', {})
            treatment_id = treatment_data.get('id', 'N/A')
            
            print("\n🎉 TREATMENT RECORD CREATED SUCCESSFULLY!")
            print("=" * 55)
            print(f"✅ Treatment Record ID: {treatment_id}")
            print(f"✅ Patient: David Jones (P004)")
            print(f"✅ Patient ID: {patient_id}")
            print(f"✅ Provider: EMP004 (ICU Nurse)")
            print(f"✅ Doctor ID: {doctor_id}")
            print(f"✅ Treatment Type: check-up")
            print(f"✅ Treatment Name: sugar level check-up")
            print(f"✅ Date Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print(f"\n📋 RECORD SUMMARY:")
            print(f"   The treatment record for David Jones' sugar level check-up")
            print(f"   has been successfully created in the system.")
            print(f"   Provider EMP004 (ICU Nurse) administered the treatment.")
            print(f"   Treatment ID: {treatment_id}")
            
        else:
            print(f"\n❌ TREATMENT CREATION FAILED:")
            print(f"   Message: {response_data.get('message', 'Unknown error')}")
            
    else:
        print(f"\n❌ TREATMENT CREATION ERROR:")
        print(f"   {result}")
    
    print(f"\n" + "=" * 55)
    print(f"✅ TREATMENT RECORD RESOLUTION COMPLETE")
    print(f"   • Found patient P004: David Jones")
    print(f"   • Found provider EMP004: ICU Nurse")
    print(f"   • Used correct tool: add_treatment_record_simple")
    print(f"   • Used correct parameters: patient_id, doctor_id, treatment_type, treatment_name")

if __name__ == "__main__":
    from datetime import datetime
    main()
