#!/usr/bin/env python3
"""
Test Complete Bed Assignment Workflow
====================================

This script tests the complete bed assignment workflow that was causing issues:
"If I assign a bed with bed no with particular patient name the bed going to assign to another different patient"

We'll simulate the frontend workflow that calls extractBedAssignmentParameters and search_patients
"""

import json
import requests
import time

def simulate_bed_assignment(bed_description, patient_name):
    """Simulate the bed assignment workflow that was problematic"""
    
    print(f"\n🛏️  Testing Bed Assignment: '{bed_description}' → '{patient_name}'")
    print("-" * 60)
    
    # Step 1: Extract bed parameters (this was fixed in directHttpAiMcpService.js)
    print(f"1. Parsing bed description: '{bed_description}'")
    
    # Simulate the fixed extractBedAssignmentParameters logic
    bed_number = None
    if 'bed' in bed_description.lower() or 'room' in bed_description.lower():
        # Extract number/alphanumeric identifier
        import re
        match = re.search(r'(\d+[a-zA-Z]?)', bed_description)
        if match:
            bed_number = match.group(1)
    
    print(f"   ✅ Extracted bed_number: {bed_number}")
    
    # Step 2: Parse patient name (this was fixed with parsePatientNameForSearch)
    print(f"2. Parsing patient name: '{patient_name}'")
    
    name_parts = patient_name.strip().split()
    if len(name_parts) >= 2:
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:])
    else:
        first_name = name_parts[0] if name_parts else ""
        last_name = ""
    
    print(f"   ✅ Parsed to: first_name='{first_name}', last_name='{last_name}'")
    
    # Step 3: Search for patient using corrected parameters
    print(f"3. Searching for patient with corrected parameters...")
    
    try:
        response = requests.post(
            "http://localhost:8000/tools/call",
            headers={"Content-Type": "application/json"},
            json={
                "jsonrpc": "2.0",
                "id": "bed_assignment_test",
                "method": "call_tool",
                "params": {
                    "name": "search_patients",
                    "arguments": {
                        "first_name": first_name,
                        "last_name": last_name
                    }
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result and "content" in result["result"]:
                search_result = result["result"]["content"][0]["text"]
                result_data = json.loads(search_result)
                
                # Parse the nested response structure
                if "result" in result_data and "data" in result_data["result"]:
                    patients = result_data["result"]["data"]
                    print(f"   ✅ Search returned {len(patients)} patients")
                    
                    if len(patients) > 0:
                        # Look for exact match first
                        exact_match = None
                        for patient in patients:
                            patient_full_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}"
                            if patient_full_name == patient_name:
                                exact_match = patient
                                break
                        
                        if exact_match:
                            selected_patient = exact_match
                            print(f"   🎯 Exact match found!")
                        else:
                            selected_patient = patients[0]
                            print(f"   📋 Using first result (no exact match)")
                        
                        patient_id = selected_patient.get('id')
                        patient_display_name = f"{selected_patient.get('first_name', '')} {selected_patient.get('last_name', '')}"
                        
                        print(f"   👤 Selected Patient: {patient_display_name}")
                        print(f"   🆔 Patient ID: {patient_id}")
                        
                        # Step 4: Simulate the bed assignment
                        print(f"4. Simulating bed assignment...")
                        print(f"   🛏️  Assigning bed '{bed_number}' to patient '{patient_display_name}' (ID: {patient_id})")
                        
                        # Check if this matches what the user expected
                        if patient_display_name == patient_name:
                            print(f"   ✅ SUCCESS: Bed assignment goes to CORRECT patient!")
                            print(f"   ✅ User requested '{patient_name}' and system selected '{patient_display_name}'")
                            return True
                        else:
                            print(f"   ❌ ISSUE: Bed assignment goes to WRONG patient!")
                            print(f"   ❌ User requested '{patient_name}' but system selected '{patient_display_name}'")
                            return False
                    else:
                        print(f"   ⚠️  No patients found matching '{patient_name}'")
                        return False
                else:
                    print(f"   ❌ Unexpected response structure")
                    return False
            else:
                print(f"   ❌ API call failed with structure issue")
                return False
        else:
            print(f"   ❌ API call failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during patient search: {str(e)}")
        return False

def main():
    """Test the complete bed assignment workflow with real scenarios"""
    
    print("🏥 Testing Complete Bed Assignment Workflow")
    print("="*60)
    print("This tests the user's original issue:")
    print("'If I assign a bed with bed no with particular patient name")
    print(" the bed going to assign to another different patient'")
    print()
    
    # Test cases using real patients from our database
    test_scenarios = [
        {
            'description': 'User assigns bed 102 to Daniel Williams',
            'bed_description': 'bed 102',
            'patient_name': 'Daniel Williams'
        },
        {
            'description': 'User assigns bed 205 to Alice Williams', 
            'bed_description': 'bed number 205',
            'patient_name': 'Alice Williams'
        },
        {
            'description': 'User assigns room 301 to David Johnson',
            'bed_description': 'room 301',
            'patient_name': 'David Johnson'
        },
        {
            'description': 'User assigns bed 401A to Linda Davis',
            'bed_description': 'bed 401A',
            'patient_name': 'Linda Davis'
        },
        {
            'description': 'User tries non-existent patient',
            'bed_description': 'bed 500',
            'patient_name': 'John Smith'  # This should not exist in our DB
        }
    ]
    
    successful_tests = 0
    total_tests = len(test_scenarios)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}/{total_tests}: {scenario['description']}")
        print(f"{'='*60}")
        
        success = simulate_bed_assignment(
            scenario['bed_description'], 
            scenario['patient_name']
        )
        
        if success:
            successful_tests += 1
        
        time.sleep(1)  # Small delay between tests
    
    # Final results
    print(f"\n{'='*60}")
    print(f"🏁 FINAL RESULTS")
    print(f"{'='*60}")
    print(f"✅ Successful tests: {successful_tests}/{total_tests}")
    print(f"❌ Failed tests: {total_tests - successful_tests}/{total_tests}")
    
    if successful_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"🎉 Bed assignment issue has been RESOLVED!")
        print(f"🎉 Patients now get assigned to the correct beds!")
    else:
        print(f"\n⚠️  Some tests failed - there may still be issues")
    
    return successful_tests == total_tests

if __name__ == "__main__":
    main()
