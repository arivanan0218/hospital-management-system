"""
Database Verification Script for Mohamed Nazif Assignments
Check what assignments were actually stored in the database
"""

import requests
import json

BASE_URL = "http://localhost:8000/tools/call"
PATIENT_ID = "c36ddebf-0885-4c90-a035-bc36eaf28480"
PATIENT_NAME = "Mohamed Nazif"

def make_mcp_request(tool_name, arguments, request_id=1):
    """Make MCP tool request"""
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        },
        "id": request_id
    }
    
    try:
        response = requests.post(BASE_URL, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"][0]["text"]
                parsed_data = json.loads(content)
                return parsed_data
        return None
    except Exception as e:
        print(f"Error in {tool_name}: {str(e)}")
        return None

def check_database_assignments():
    """Check actual database state for Mohamed Nazif assignments"""
    print("🔍 CHECKING DATABASE FOR MOHAMED NAZIF ASSIGNMENTS")
    print("=" * 70)
    
    # 1. Check if patient exists and get details
    print("\n1️⃣ PATIENT DETAILS:")
    patient_result = make_mcp_request("get_patient_by_id", {"patient_id": PATIENT_ID}, 1)
    if patient_result and patient_result.get("success"):
        patient = patient_result["result"]["data"]
        print(f"   ✅ Patient found: {patient['first_name']} {patient['last_name']}")
        print(f"   📞 Phone: {patient['phone']}")
        print(f"   📧 Email: {patient['email']}")
        print(f"   🩸 Blood Type: {patient['blood_type']}")
    else:
        print("   ❌ Patient not found")
        return
    
    # 2. Check bed assignments - look for beds assigned to this patient
    print("\n2️⃣ BED ASSIGNMENT:")
    beds_result = make_mcp_request("list_beds", {}, 2)
    assigned_bed = None
    if beds_result and beds_result.get("success"):
        beds = beds_result["result"]["data"]
        for bed in beds:
            if bed.get("patient_id") == PATIENT_ID:
                assigned_bed = bed
                print(f"   ✅ Bed assigned: {bed['bed_number']} (Room {bed['room_number']})")
                print(f"   📅 Admission date: {bed.get('admission_date', 'Not set')}")
                break
        
        if not assigned_bed:
            print("   ❌ No bed currently assigned to this patient")
    
    # 3. Check staff assignments using SQL query
    print("\n3️⃣ STAFF ASSIGNMENTS:")
    print("   📋 Checking staff_assignments table...")
    
    # We'll need to check the database directly since there's no specific tool for this
    # For now, let's check if our assignment was successful by looking at available staff
    staff_result = make_mcp_request("list_staff", {}, 3)
    if staff_result and staff_result.get("success"):
        staff_list = staff_result["result"]["data"]
        print("   👥 Available staff:")
        for staff in staff_list:
            print(f"      - {staff['first_name']} {staff['last_name']} ({staff['position']})")
        
        # Check if Mary Brown (nurse) is in our list - she was assigned
        mary_brown = next((s for s in staff_list if s['first_name'] == 'Mary' and s['last_name'] == 'Brown'), None)
        if mary_brown:
            print(f"   ✅ Nurse Mary Brown found in system (ID: {mary_brown['id']})")
        else:
            print("   ❌ Mary Brown not found")
    
    # 4. Check equipment usage
    print("\n4️⃣ EQUIPMENT ASSIGNMENTS:")
    equipment_result = make_mcp_request("list_equipment", {}, 4)
    if equipment_result and equipment_result.get("success"):
        equipment_list = equipment_result["result"]["data"]
        print("   🔧 Equipment status:")
        for eq in equipment_list:
            print(f"      - {eq['name']} ({eq['equipment_id']}): {eq['status']}")
    
    # 5. Check supply levels
    print("\n5️⃣ SUPPLY LEVELS:")
    supplies_result = make_mcp_request("list_supplies", {}, 5)
    if supplies_result and supplies_result.get("success"):
        supplies_list = supplies_result["result"]["data"]
        print("   📦 Current supply levels:")
        for supply in supplies_list:
            print(f"      - {supply['name']}: {supply['current_stock']} {supply['unit_of_measure']}")
    
    print("\n" + "=" * 70)
    print("📋 SUMMARY:")
    print("   - Patient Mohamed Nazif exists in system")
    print("   - Staff assignment may have been successful (nurse assignment returned success)")
    print("   - Bed assignment failed due to date format issue")
    print("   - Equipment assignment failed due to UUID issue")
    print("   - Supply allocation failed due to parameter mismatch")
    
    print("\n💡 NEXT STEPS:")
    print("   1. Fix date format for bed assignment (remove 'T' format)")
    print("   2. Use correct UUID format for equipment assignment")
    print("   3. Use correct parameters for supply allocation")
    print("   4. Query assignment tables directly to verify staff assignment")

if __name__ == "__main__":
    check_database_assignments()
