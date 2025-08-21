#!/usr/bin/env python3
"""
Find patient P004 and staff EMP004 for treatment record creation
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
    print("🏥 TREATMENT RECORD CREATION - FINDING REQUIRED IDs")
    print("=" * 60)
    
    # 1. Find David Jones patient by patient number P004
    print("\n1. 🔍 Finding patient P004 (David Jones)...")
    result = call_tool("search_patients", {"patient_number": "P004"}, 1)
    
    patient_id = None
    if 'result' in result:
        response_text = result['result']['content'][0]['text']
        response_data = json.loads(response_text)
        if response_data.get('success') and response_data.get('result', {}).get('data'):
            patient_data = response_data['result']['data'][0]
            patient_id = patient_data['id']
            print(f"✅ Found patient P004:")
            print(f"   Patient ID: {patient_id}")
            print(f"   Name: {patient_data['first_name']} {patient_data['last_name']}")
            print(f"   Patient Number: {patient_data['patient_number']}")
        else:
            print(f"❌ Patient P004 not found: {response_data.get('message', 'No data')}")
    else:
        print(f"❌ Patient search error: {result}")
    
    # 2. Find staff member with employee ID EMP004
    print("\n2. 👨‍⚕️ Finding staff member EMP004...")
    result = call_tool("list_staff", {}, 2)
    
    doctor_id = None
    if 'result' in result:
        response_text = result['result']['content'][0]['text']
        response_data = json.loads(response_text)
        if response_data.get('success') and response_data.get('result', {}).get('data'):
            staff_list = response_data['result']['data']
            print(f"Found {len(staff_list)} staff members:")
            
            for staff in staff_list:
                emp_id = staff.get('employee_id', 'N/A')
                position = staff.get('position', 'N/A')
                staff_id = staff.get('id', 'N/A')
                
                if emp_id == 'EMP004':
                    doctor_id = staff_id
                    print(f"✅ FOUND EMP004:")
                    print(f"   Staff ID: {staff_id}")
                    print(f"   Employee ID: {emp_id}")
                    print(f"   Position: {position}")
                    print(f"   User ID: {staff.get('user_id', 'N/A')}")
                else:
                    print(f"   - {emp_id}: {position}")
                    
            if not doctor_id:
                print("❌ EMP004 not found in staff list")
        else:
            print(f"❌ Staff listing failed: {response_data.get('message', 'No data')}")
    else:
        print(f"❌ Staff search error: {result}")
    
    # 3. If we have both IDs, create the treatment record
    if patient_id and doctor_id:
        print("\n3. 🏥 Creating treatment record...")
        result = call_tool("create_treatment", {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "treatment_type": "check-up",
            "treatment_name": "sugar level check-up",
            "description": "Blood sugar level monitoring and assessment for patient David Jones",
            "medications": "None prescribed",
            "instructions": "Monitor blood sugar levels regularly, maintain healthy diet",
            "follow_up_date": "2025-09-21"  # 1 month follow-up
        }, 3)
        
        if 'result' in result:
            response_text = result['result']['content'][0]['text']
            response_data = json.loads(response_text)
            if response_data.get('success'):
                treatment_data = response_data['result']['data']
                print("✅ TREATMENT RECORD CREATED SUCCESSFULLY!")
                print(f"   Treatment ID: {treatment_data.get('id', 'N/A')}")
                print(f"   Patient: {treatment_data.get('patient_name', 'N/A')}")
                print(f"   Doctor: {treatment_data.get('doctor_name', 'N/A')}")
                print(f"   Treatment: {treatment_data.get('treatment_name', 'N/A')}")
                print(f"   Date: {treatment_data.get('treatment_date', 'N/A')}")
            else:
                print(f"❌ Treatment creation failed: {response_data.get('message')}")
        else:
            print(f"❌ Treatment creation error: {result}")
    else:
        print("\n3. ❌ Cannot create treatment record - missing required information")
        print(f"   Patient ID (P004): {patient_id}")
        print(f"   Doctor ID (EMP004): {doctor_id}")
        
        # Show what information we have
        print("\n📋 REQUIRED INFORMATION FOR TREATMENT RECORD:")
        print("✅ Treatment Type: check-up")
        print("✅ Treatment Name: sugar level check-up") 
        print("✅ Description: Blood sugar level monitoring")
        print(f"{'✅' if patient_id else '❌'} Patient ID: {patient_id or 'NOT FOUND'}")
        print(f"{'✅' if doctor_id else '❌'} Doctor ID: {doctor_id or 'NOT FOUND'}")

if __name__ == "__main__":
    main()
