"""
Comprehensive test to verify the complete workflow issue
"""

import requests
import json
import time

def comprehensive_workflow_test():
    """Test the complete workflow and identify where it breaks"""
    
    print("🧪 COMPREHENSIVE WORKFLOW TEST")
    print("=" * 45)
    
    base_url = "http://127.0.0.1:8000/tools/call"
    
    # Step 1: Create patient through LangGraph
    print("📝 STEP 1: Creating patient through LangGraph")
    
    patient_data = {
        "first_name": "Workflow",
        "last_name": "Test",
        "date_of_birth": "1992-03-10",
        "gender": "male",
        "phone": "555-1234",
        "blood_type": "AB+",
        "allergies": "None",
        "emergency_contact_name": "Emergency Person",
        "emergency_contact_phone": "555-5678"
    }
    
    langraph_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "execute_langraph_patient_admission",
            "arguments": {
                "patient_data": patient_data
            }
        }
    }
    
    patient_id = None
    patient_number = None
    
    try:
        response = requests.post(base_url, json=langraph_payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            content = result.get("result", {}).get("content", [])
            if content:
                response_text = content[0].get("text", "{}")
                data = json.loads(response_text)
                
                if data.get("success") and data.get("result", {}).get("success"):
                    result_data = data["result"]
                    patient_id = result_data.get("patient_id")
                    staff_assignments = result_data.get("staff_assignments", [])
                    
                    print(f"✅ LangGraph creation successful")
                    print(f"   Patient ID: {patient_id}")
                    print(f"   Staff assignments: {len(staff_assignments)}")
                    
                    for assignment in staff_assignments:
                        print(f"     • {assignment.get('role')}: {assignment.get('name')} (ID: {assignment.get('assignment_id')})")
                else:
                    print(f"❌ LangGraph failed: {data}")
                    return
        
        # Step 2: Wait and check if patient appears in list
        print(f"\n⏳ STEP 2: Waiting 2 seconds then checking patient list")
        time.sleep(2)
        
        list_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "list_patients",
                "arguments": {}
            }
        }
        
        response = requests.post(base_url, json=list_payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            content = result.get("result", {}).get("content", [])
            if content:
                response_text = content[0].get("text", "{}")
                data = json.loads(response_text)
                
                if data.get("success"):
                    patients = data.get("patients", [])
                    print(f"📋 Found {len(patients)} patients in list")
                    
                    found_patient = None
                    for patient in patients:
                        if patient.get('id') == patient_id:
                            found_patient = patient
                            patient_number = patient.get('patient_number')
                            print(f"✅ Found our patient in list:")
                            print(f"   Name: {patient.get('first_name')} {patient.get('last_name')}")
                            print(f"   Patient Number: {patient_number}")
                            break
                    
                    if not found_patient:
                        print(f"❌ Our patient (ID: {patient_id}) not found in patient list!")
                        print("   This indicates a database transaction/isolation issue")
                        return
                else:
                    print(f"❌ List patients failed: {data.get('message')}")
                    return
        
        # Step 3: Try discharge using patient_number
        print(f"\n🏥 STEP 3: Discharging using patient_number: {patient_number}")
        
        discharge_payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "discharge_patient_complete",
                "arguments": {
                    "patient_number": patient_number,
                    "discharge_condition": "excellent",
                    "discharge_destination": "home"
                }
            }
        }
        
        response = requests.post(base_url, json=discharge_payload, timeout=20)
        if response.status_code == 200:
            result = response.json()
            content = result.get("result", {}).get("content", [])
            if content:
                response_text = content[0].get("text", "{}")
                discharge_data = json.loads(response_text)
                
                if discharge_data.get("success"):
                    discharge_result = discharge_data.get("result", {})
                    print(f"✅ Discharge by patient_number successful!")
                    
                    # Check staff assignments in report
                    discharge_report = discharge_result.get("discharge_report", {})
                    raw_data = discharge_report.get("raw_data", {})
                    staff_summary = raw_data.get("staff_summary", [])
                    
                    print(f"👥 Staff assignments in discharge report: {len(staff_summary)}")
                    
                    if staff_summary:
                        print("✅ SUCCESS: Staff assignments found in discharge report!")
                        for staff in staff_summary:
                            print(f"   • {staff.get('staff_name')}: {staff.get('assignment_type')}")
                    else:
                        print("❌ No staff assignments in discharge report")
                else:
                    print(f"❌ Discharge by patient_number failed: {discharge_data.get('message')}")
                    
                    # Try discharge using patient_id as fallback
                    print(f"\n🔄 STEP 4: Trying discharge using patient_id as fallback")
                    
                    discharge_payload["params"]["arguments"] = {
                        "patient_id": patient_id,
                        "discharge_condition": "excellent",
                        "discharge_destination": "home"
                    }
                    
                    response = requests.post(base_url, json=discharge_payload, timeout=20)
                    if response.status_code == 200:
                        result = response.json()
                        content = result.get("result", {}).get("content", [])
                        if content:
                            response_text = content[0].get("text", "{}")
                            discharge_data = json.loads(response_text)
                            
                            if discharge_data.get("success"):
                                discharge_result = discharge_data.get("result", {})
                                print(f"✅ Discharge by patient_id successful!")
                                
                                # Check staff assignments
                                discharge_report = discharge_result.get("discharge_report", {})
                                raw_data = discharge_report.get("raw_data", {})
                                staff_summary = raw_data.get("staff_summary", [])
                                
                                print(f"👥 Staff assignments in discharge report: {len(staff_summary)}")
                                
                                if staff_summary:
                                    print("✅ SUCCESS: Staff assignments found using patient_id!")
                                    for staff in staff_summary:
                                        print(f"   • {staff.get('staff_name')}: {staff.get('assignment_type')}")
                                    
                                    print(f"\n🎉 CONCLUSION:")
                                    print(f"   ✅ LangGraph creates staff assignments correctly")
                                    print(f"   ✅ Staff assignments appear in discharge reports")
                                    print(f"   ⚠️  Patient_number lookup might have issues in some cases")
                                    print(f"   ✅ Patient_id lookup works reliably")
                                else:
                                    print("❌ Still no staff assignments using patient_id")
                            else:
                                print(f"❌ Discharge by patient_id also failed")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    comprehensive_workflow_test()
