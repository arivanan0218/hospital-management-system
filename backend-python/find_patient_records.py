"""
Find the actual patient and their supply/equipment records
"""

import requests
import json

def find_actual_patient_records():
    """Find patients and their records"""
    
    print("🔍 FINDING ACTUAL PATIENT RECORDS")
    print("=" * 40)
    
    base_url = "http://127.0.0.1:8000/tools/call"
    
    # Step 1: List all patients to see what we have
    print("📋 Step 1: Listing all patients")
    
    list_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "list_patients",
            "arguments": {}
        }
    }
    
    try:
        response = requests.post(base_url, json=list_payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            content = result.get("result", {}).get("content", [])
            if content:
                response_text = content[0].get("text", "{}")
                data = json.loads(response_text)
                
                if data.get("success"):
                    patients = data.get("patients", [])
                    print(f"✅ Found {len(patients)} patients:")
                    
                    target_patient = None
                    for i, patient in enumerate(patients[-5:], 1):  # Show last 5
                        patient_number = patient.get('patient_number', 'No Number')
                        print(f"   {i}. {patient.get('first_name', '')} {patient.get('last_name', '')} ({patient_number})")
                        print(f"      ID: {patient.get('id')}")
                        print(f"      Status: {patient.get('status', 'Unknown')}")
                        
                        # Look for a patient that might be the one we want
                        if patient.get('first_name') in ['Mohamed', 'Nazif', 'TestStaff', 'FullDebug', 'Workflow'] or patient_number in ['P1025']:
                            target_patient = patient
                            print(f"      🎯 This might be our target patient!")
                        print()
                    
                    if not target_patient and patients:
                        # Use the most recent patient
                        target_patient = patients[-1]
                        print(f"🎯 Using most recent patient: {target_patient.get('first_name')} {target_patient.get('last_name')} ({target_patient.get('patient_number')})")
                    
                    if target_patient:
                        patient_id = target_patient.get('id')
                        patient_number = target_patient.get('patient_number')
                        
                        # Step 2: Check supply usage for this patient
                        print(f"\n💊 Step 2: Checking supply usage")
                        
                        supply_payload = {
                            "jsonrpc": "2.0",
                            "id": 2,
                            "method": "tools/call",
                            "params": {
                                "name": "list_patient_supply_usage",
                                "arguments": {}
                            }
                        }
                        
                        response = requests.post(base_url, json=supply_payload, timeout=10)
                        if response.status_code == 200:
                            result = response.json()
                            content = result.get("result", {}).get("content", [])
                            if content:
                                response_text = content[0].get("text", "{}")
                                data = json.loads(response_text)
                                
                                if data.get("success"):
                                    usage_records = data.get("usage_records", [])
                                    print(f"📋 Total supply usage records: {len(usage_records)}")
                                    
                                    # Show all records to see what we have
                                    for record in usage_records[-10:]:  # Show last 10
                                        print(f"   • Patient: {record.get('patient_number', 'Unknown')}")
                                        print(f"     Supply: {record.get('supply_name', 'Unknown')} (Code: {record.get('supply_item_code', 'Unknown')})")
                                        print(f"     Quantity: {record.get('quantity_used', 'Unknown')}")
                                        print(f"     Date: {record.get('date_of_usage', 'Unknown')}")
                                        print(f"     Staff: {record.get('employee_id', 'Unknown')}")
                                        print(f"     Notes: {record.get('notes', 'None')}")
                                        print()
                                
                        # Step 3: Check equipment usage
                        print(f"\n🔧 Step 3: Checking equipment usage")
                        
                        equipment_payload = {
                            "jsonrpc": "2.0",
                            "id": 3,
                            "method": "tools/call",
                            "params": {
                                "name": "list_equipment_usage",
                                "arguments": {}
                            }
                        }
                        
                        response = requests.post(base_url, json=equipment_payload, timeout=10)
                        if response.status_code == 200:
                            result = response.json()
                            content = result.get("result", {}).get("content", [])
                            if content:
                                response_text = content[0].get("text", "{}")
                                data = json.loads(response_text)
                                
                                if data.get("success"):
                                    usage_records = data.get("equipment_usage", [])
                                    print(f"📋 Total equipment usage records: {len(usage_records)}")
                                    
                                    # Show all records to see what we have
                                    for record in usage_records[-10:]:  # Show last 10
                                        patient_info = record.get('patient_number', record.get('patient_id', 'Unknown'))
                                        print(f"   • Patient: {patient_info}")
                                        print(f"     Equipment: {record.get('equipment_name', 'Unknown')} (ID: {record.get('equipment_id', 'Unknown')})")
                                        print(f"     Purpose: {record.get('purpose', 'Unknown')}")
                                        print(f"     Start: {record.get('start_time', 'Unknown')}")
                                        print(f"     End: {record.get('end_time', 'Unknown')}")
                                        print(f"     Used by: {record.get('used_by_name', record.get('staff_name', 'Unknown'))}")
                                        print()
                        
                        # Step 4: Test discharge report for this patient
                        print(f"\n📄 Step 4: Testing discharge report for {patient_number}")
                        
                        discharge_payload = {
                            "jsonrpc": "2.0",
                            "id": 4,
                            "method": "tools/call",
                            "params": {
                                "name": "discharge_patient_complete",
                                "arguments": {
                                    "patient_id": patient_id,  # Use patient_id to avoid lookup issues
                                    "discharge_condition": "stable",
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
                                    discharge_report = discharge_result.get("discharge_report", {})
                                    raw_data = discharge_report.get("raw_data", {})
                                    
                                    print(f"✅ Discharge report generated successfully")
                                    
                                    # Analyze what's in the report
                                    equipment_summary = raw_data.get("equipment_summary", [])
                                    medications = raw_data.get("medications", [])
                                    treatment_summary = raw_data.get("treatment_summary", [])
                                    
                                    print(f"\n📊 DISCHARGE REPORT ANALYSIS:")
                                    print(f"   🔧 Equipment records in report: {len(equipment_summary)}")
                                    print(f"   💊 Medication records in report: {len(medications)}")
                                    print(f"   🏥 Treatment records in report: {len(treatment_summary)}")
                                    
                                    # Check the formatted report for our specific items
                                    formatted_report = discharge_report.get("formatted_report", "")
                                    
                                    print(f"\n🔍 SEARCHING FOR SPECIFIC ITEMS:")
                                    if "SUP001" in formatted_report or "Aspirin" in formatted_report.lower():
                                        print(f"   ✅ Aspirin/SUP001 found in report!")
                                    else:
                                        print(f"   ❌ Aspirin/SUP001 NOT found in report")
                                    
                                    if "EQ001" in formatted_report or "ECG" in formatted_report:
                                        print(f"   ✅ ECG/EQ001 found in report!")
                                    else:
                                        print(f"   ❌ ECG/EQ001 NOT found in report")
                                    
                                    # Show equipment section if it exists
                                    if "## EQUIPMENT USED" in formatted_report:
                                        equipment_start = formatted_report.find("## EQUIPMENT USED")
                                        equipment_end = formatted_report.find("\n---\n", equipment_start + 1)
                                        if equipment_end == -1:
                                            equipment_end = len(formatted_report)
                                        equipment_section = formatted_report[equipment_start:equipment_end]
                                        print(f"\n📋 EQUIPMENT SECTION IN REPORT:")
                                        print(equipment_section)
                                else:
                                    print(f"❌ Discharge failed: {discharge_data.get('message')}")
                    else:
                        print("❌ No patients found to test with")
                else:
                    print(f"❌ List patients failed: {data.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_actual_patient_records()
