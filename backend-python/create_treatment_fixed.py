#!/usr/bin/env python3
"""
Create treatment record with CORRECT doctor user ID
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
    print("🏥 CREATING TREATMENT RECORD - FIXED DOCTOR ID")
    print("=" * 50)
    
    # Corrected IDs based on foreign key constraint analysis
    patient_id = "0856eeb7-af35-474e-b9b3-981b2a359cd8"    # David Jones (P004)
    doctor_user_id = "d0bb0ff3-b0a9-46ff-a125-59f43c1704f5"  # EMP004's USER ID (not staff ID)
    
    print(f"📋 CORRECTED PARAMETERS:")
    print(f"   Patient ID: {patient_id}")
    print(f"   Doctor User ID: {doctor_user_id} (EMP004's user_id)")
    print(f"   Treatment Type: check-up")
    print(f"   Treatment Name: sugar level check-up")
    
    print(f"\n🔧 EXPLANATION:")
    print(f"   The treatment_records table expects doctor_id to be a user_id")
    print(f"   from the users table, not a staff_id from the staff table.")
    print(f"   EMP004's staff_id: 6d154d0a-b704-4255-add6-0b730921787e")
    print(f"   EMP004's user_id:  d0bb0ff3-b0a9-46ff-a125-59f43c1704f5 ← Using this")
    
    print(f"\n🏥 Creating treatment record...")
    result = call_tool("add_treatment_record_simple", {
        "patient_id": patient_id,
        "doctor_id": doctor_user_id,  # Use user_id, not staff_id
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
            print("=" * 50)
            print(f"✅ Treatment Record ID: {treatment_id}")
            print(f"✅ Patient: David Jones (P004)")
            print(f"✅ Provider: EMP004 (ICU Nurse)")
            print(f"✅ Treatment: sugar level check-up")
            print(f"✅ Type: check-up")
            print(f"✅ Status: Created successfully")
            
            print(f"\n📋 SUCCESS SUMMARY:")
            print(f"   ✅ Resolved patient P004 to correct patient_id")
            print(f"   ✅ Resolved EMP004 to correct user_id (not staff_id)")
            print(f"   ✅ Used correct tool parameters")
            print(f"   ✅ Treatment record created in database")
            
        else:
            print(f"\n❌ TREATMENT CREATION STILL FAILED:")
            print(f"   Message: {response_data.get('message', 'Unknown error')}")
            
    else:
        print(f"\n❌ TREATMENT CREATION ERROR:")
        print(f"   {result}")

if __name__ == "__main__":
    main()
