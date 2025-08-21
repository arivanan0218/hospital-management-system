#!/usr/bin/env python3
"""
Direct database verification of treatment record
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database import SessionLocal, TreatmentRecord
    import uuid
    
    def verify_treatment_in_db():
        print("🗄️ DIRECT DATABASE VERIFICATION")
        print("=" * 40)
        
        treatment_id = "d3639f34-0278-4498-bc6a-89ede8a8ab9d"
        patient_id = "0856eeb7-af35-474e-b9b3-981b2a359cd8"
        
        print(f"Checking for treatment ID: {treatment_id}")
        
        db = SessionLocal()
        try:
            # Query for the specific treatment record
            treatment = db.query(TreatmentRecord).filter(
                TreatmentRecord.id == uuid.UUID(treatment_id)
            ).first()
            
            if treatment:
                print(f"✅ TREATMENT RECORD FOUND IN DATABASE!")
                print(f"   ID: {treatment.id}")
                print(f"   Patient ID: {treatment.patient_id}")
                print(f"   Doctor ID: {treatment.doctor_id}")
                print(f"   Treatment Type: {treatment.treatment_type}")
                print(f"   Treatment Name: {treatment.treatment_name}")
                print(f"   Start Date: {treatment.start_date}")
                print(f"   Created At: {treatment.created_at}")
                print(f"   Status: VERIFIED - Record exists in database")
            else:
                print(f"❌ Treatment record NOT found in database")
                
                # Check if there are any treatment records for this patient
                patient_treatments = db.query(TreatmentRecord).filter(
                    TreatmentRecord.patient_id == uuid.UUID(patient_id)
                ).all()
                
                print(f"\n📋 All treatment records for patient {patient_id}:")
                if patient_treatments:
                    for tr in patient_treatments:
                        print(f"   - ID: {tr.id}")
                        print(f"     Name: {tr.treatment_name}")
                        print(f"     Type: {tr.treatment_type}")
                        print(f"     Date: {tr.start_date}")
                else:
                    print(f"   No treatment records found for this patient")
            
            # Also check total count of treatment records
            total_treatments = db.query(TreatmentRecord).count()
            print(f"\n📊 Total treatment records in database: {total_treatments}")
            
        except Exception as e:
            print(f"❌ Database query error: {e}")
        finally:
            db.close()
    
    if __name__ == "__main__":
        verify_treatment_in_db()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Falling back to tool-based verification...")
    
    import requests
    import json
    
    def call_tool(name, arguments):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
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
    
    print("🔍 FALLBACK: Using tool-based verification")
    print("=" * 40)
    
    # Try to create another test treatment to see if it works
    print("Testing treatment record creation again...")
    
    result = call_tool("add_treatment_record_simple", {
        "patient_id": "0856eeb7-af35-474e-b9b3-981b2a359cd8",
        "doctor_id": "d0bb0ff3-b0a9-46ff-a125-59f43c1704f5",
        "treatment_type": "follow-up",
        "treatment_name": "blood pressure check"
    })
    
    if 'result' in result:
        response_text = result['result']['content'][0]['text']
        response_data = json.loads(response_text)
        
        if response_data.get('success'):
            new_treatment_id = response_data['result']['data']['id']
            print(f"✅ New treatment record created: {new_treatment_id}")
            print("✅ Database is accepting treatment records")
        else:
            print(f"❌ Treatment creation failed: {response_data.get('message')}")
    else:
        print(f"❌ Tool call failed: {result}")
