#!/usr/bin/env python3
"""
Setup test data to reproduce discharge workflow issues
"""

import requests
import json
import time

def call_tool(name, arguments=None):
    """Call a tool via HTTP API"""
    if arguments is None:
        arguments = {}
    
    # Use the correct MCP format
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
            # Handle nested response format
            content = result["result"]
            if isinstance(content, dict) and "content" in content:
                # Extract the actual result from nested format
                content_list = content["content"]
                if isinstance(content_list, list) and len(content_list) > 0:
                    text_content = content_list[0].get("text", "")
                    try:
                        # Parse the JSON string inside
                        actual_result = json.loads(text_content)
                        # Return the nested result
                        if "result" in actual_result:
                            return actual_result["result"]
                        else:
                            return actual_result
                    except json.JSONDecodeError:
                        return {"error": "Failed to parse response", "raw": text_content}
            return content
        elif "error" in result:
            print(f"❌ Error calling {name}: {result['error']}")
            return None
    else:
        print(f"❌ HTTP Error {response.status_code} calling {name}")
        return None

def main():
    print("🏥 SETTING UP TEST DATA TO REPRODUCE DISCHARGE ISSUE")
    print("=" * 60)
    
    # Step 1: Create a test patient
    print("\n1️⃣ CREATING TEST PATIENT...")
    patient_result = call_tool("create_patient", {
        "first_name": "Test",
        "last_name": "Patient",
        "date_of_birth": "1985-05-15",
        "phone": "555-0123",
        "emergency_contact": "Jane Doe",
        "emergency_phone": "555-0124"
    })
    
    if patient_result and patient_result.get("success"):
        # Extract patient info from nested data structure
        patient_data = patient_result.get("data", {})
        patient_id = patient_data.get("id")
        patient_number = patient_data.get("patient_number")
        print(f"✅ Created patient: {patient_number} (ID: {patient_id})")
        
        # Step 2: Get bed ID and assign bed
        print(f"\n2️⃣ FINDING AND ASSIGNING BED...")
        
        # First get bed by number to get its ID
        bed_info = call_tool("get_bed_by_number", {"bed_number": "302A"})
        if bed_info and bed_info.get("data"):
            bed_data = bed_info.get("data", {})
            bed_id = bed_data.get("id")
            bed_status = bed_data.get("status")
            print(f"   Found bed 302A with ID: {bed_id}, Status: {bed_status}")
            
            # Now assign the bed
            bed_result = call_tool("assign_bed_to_patient", {
                "bed_id": bed_id,
                "patient_id": patient_id
            })
        else:
            print(f"   ❌ Could not find bed 302A: {bed_info}")
            bed_result = None
        
        if bed_result and bed_result.get("success"):
            print(f"✅ Assigned bed 302A to patient")
            
            # Step 3: Check bed status before discharge
            print(f"\n3️⃣ CHECKING BED STATUS BEFORE DISCHARGE...")
            bed_status = call_tool("get_bed_status_with_time_remaining", {"bed_id": "302A"})
            if bed_status:
                print(f"   Bed status: {bed_status.get('current_status', 'unknown')}")
                print(f"   Process status: {bed_status.get('process_status', 'none')}")
            
            # Step 4: Discharge the patient
            print(f"\n4️⃣ DISCHARGING PATIENT...")
            discharge_result = call_tool("discharge_patient_complete", {
                "patient_id": patient_id,
                "discharge_condition": "stable",
                "discharge_destination": "home"
            })
            
            if discharge_result and discharge_result.get("success"):
                print(f"✅ Patient discharged successfully")
                report_number = discharge_result.get("report_number")
                if report_number:
                    print(f"📋 Discharge report: {report_number}")
                
                # Step 5: Check bed status after discharge
                print(f"\n5️⃣ CHECKING BED STATUS AFTER DISCHARGE...")
                time.sleep(2)  # Wait a moment for processing
                
                bed_status_after = call_tool("get_bed_status_with_time_remaining", {"bed_id": "302A"})
                if bed_status_after:
                    status = bed_status_after.get('current_status', 'unknown')
                    process = bed_status_after.get('process_status', 'none')
                    time_remaining = bed_status_after.get('time_remaining_minutes', 0)
                    
                    print(f"   Bed status: {status}")
                    print(f"   Process status: {process}")
                    if time_remaining > 0:
                        print(f"   Time remaining: {time_remaining} minutes")
                    
                    # Check for the reported issue
                    if status == "occupied":
                        print(f"   ⚠️  CONFIRMED ISSUE: Bed shows 'occupied' after discharge!")
                    elif status == "cleaning":
                        print(f"   ✅ Good: Bed shows 'cleaning' status")
                    elif process == "none":
                        print(f"   ⚠️  ISSUE: No cleaning process initiated")
                
                # Step 6: Check patient list to see if discharged patient still shows
                print(f"\n6️⃣ CHECKING PATIENT LIST...")
                patients_result = call_tool("list_patients")
                if patients_result:
                    if isinstance(patients_result, dict):
                        patients = patients_result.get('patients', []) or patients_result.get('data', [])
                    elif isinstance(patients_result, list):
                        patients = patients_result
                    else:
                        patients = []
                    
                    discharged_in_list = False
                    for patient in patients:
                        if isinstance(patient, dict):
                            p_id = patient.get('id')
                            p_status = patient.get('status')
                            p_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}"
                            
                            if p_id == patient_id:
                                print(f"   Found test patient: {p_name} - Status: {p_status}")
                                if p_status == "discharged":
                                    print(f"   ✅ Patient correctly marked as discharged")
                                else:
                                    print(f"   ⚠️  ISSUE: Patient status is '{p_status}', not 'discharged'")
                                
                                if p_status == "discharged":
                                    print(f"   ⚠️  CONFIRMED ISSUE: Discharged patient still in active list!")
                                    discharged_in_list = True
                    
                    if not discharged_in_list:
                        print(f"   ✅ Good: Discharged patient not in active list")
                
                # Step 7: Show summary of issues found
                print(f"\n7️⃣ ISSUE SUMMARY:")
                print(f"   🔍 Bed 302A status after discharge: {bed_status_after.get('current_status', 'unknown') if bed_status_after else 'N/A'}")
                print(f"   🔍 Cleaning process active: {'Yes' if bed_status_after and bed_status_after.get('process_status') in ['cleaning', 'initiated'] else 'No'}")
                print(f"   🔍 Discharged patient in list: {'Yes' if discharged_in_list else 'No'}")
                
            else:
                print(f"❌ Failed to discharge patient: {discharge_result}")
        else:
            print(f"❌ Failed to assign bed: {bed_result}")
    else:
        print(f"❌ Failed to create patient: {patient_result}")
    
    print(f"\n✅ TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
