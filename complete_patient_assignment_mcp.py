"""
Complete Patient Assignment Script for Mohamed Nazif - MCP Version
This script assigns bed, staff, equipment, and supplies using the correct MCP tool calling format
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/tools/call"

# Patient details (known from previous queries)
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
        print(f"📡 MCP Tool Call: {tool_name}")
        print(f"   Arguments: {json.dumps(arguments, indent=2)}")
        
        response = requests.post(BASE_URL, json=payload, timeout=10)
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {json.dumps(result, indent=2)}")
            
            # Extract the actual tool result
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"][0]["text"]
                parsed_data = json.loads(content)
                return parsed_data
            return result
        else:
            print(f"   ❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"   💥 Exception: {str(e)}")
        return None

def assign_bed():
    """Assign bed to patient"""
    print("\n🏨 ASSIGNING BED TO PATIENT...")
    
    # First get available beds to find one we can assign
    beds_result = make_mcp_request("list_beds", {"status": "available"}, 1)
    
    if beds_result and beds_result.get("success") and beds_result.get("result", {}).get("data"):
        beds = beds_result["result"]["data"]
        
        # Filter out bed 401A (which is cleaning) and find a suitable bed
        suitable_bed = None
        for bed in beds:
            if bed.get("bed_number") != "401A":
                suitable_bed = bed
                break
        
        if suitable_bed:
            bed_id = suitable_bed.get("id")
            bed_number = suitable_bed.get("bed_number")
            
            # Assign the bed
            current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            assign_result = make_mcp_request("assign_bed_to_patient", {
                "bed_id": bed_id,
                "patient_id": PATIENT_ID,
                "admission_date": current_time
            }, 2)
            
            return {"bed_number": bed_number, "result": assign_result}
    
    return None

def assign_staff():
    """Assign staff to patient"""
    print("\n👨‍⚕️ ASSIGNING STAFF TO PATIENT...")
    
    # Get available staff
    staff_result = make_mcp_request("list_staff", {}, 3)
    
    if staff_result and staff_result.get("success") and staff_result.get("result", {}).get("data"):
        staff_list = staff_result["result"]["data"]
        
        assignments = []
        
        # Find and assign a doctor
        doctor = next((s for s in staff_list if 'doctor' in s.get('position', '').lower()), None)
        if doctor:
            doctor_assign = make_mcp_request("assign_staff_to_patient_simple", {
                "staff_id": doctor.get("id"),
                "patient_id": PATIENT_ID,
                "assignment_type": "primary_care"
            }, 4)
            assignments.append({"type": "doctor", "staff": doctor, "result": doctor_assign})
        
        # Find and assign a nurse
        nurse = next((s for s in staff_list if 'nurse' in s.get('position', '').lower()), None)
        if nurse:
            nurse_assign = make_mcp_request("assign_staff_to_patient_simple", {
                "staff_id": nurse.get("id"),
                "patient_id": PATIENT_ID,
                "assignment_type": "nursing_care"
            }, 5)
            assignments.append({"type": "nurse", "staff": nurse, "result": nurse_assign})
        
        return assignments
    
    return None

def assign_equipment():
    """Assign equipment to patient"""
    print("\n🔧 ASSIGNING EQUIPMENT TO PATIENT...")
    
    # Get available equipment
    equipment_result = make_mcp_request("list_equipment", {}, 6)
    
    if equipment_result and equipment_result.get("success") and equipment_result.get("result", {}).get("data"):
        equipment_list = equipment_result["result"]["data"]
        
        # Find available equipment
        available_equipment = next((e for e in equipment_list if e.get('status') == 'available'), None)
        
        if available_equipment:
            # Get a staff member for the equipment assignment
            staff_result = make_mcp_request("list_staff", {}, 7)
            
            if staff_result and staff_result.get("success"):
                staff_list = staff_result["result"]["data"]
                staff_member = staff_list[0] if staff_list else None
                
                if staff_member:
                    equipment_assign = make_mcp_request("add_equipment_usage_simple", {
                        "equipment_id": available_equipment.get("equipment_id"),
                        "patient_id": PATIENT_ID,
                        "staff_id": staff_member.get("id"),
                        "purpose": "patient_care",
                        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }, 8)
                    
                    return {"equipment": available_equipment, "staff": staff_member, "result": equipment_assign}
    
    return None

def assign_supplies():
    """Allocate supplies for patient"""
    print("\n📦 ALLOCATING SUPPLIES FOR PATIENT...")
    
    # Get available supplies
    supplies_result = make_mcp_request("list_supplies", {}, 9)
    
    if supplies_result and supplies_result.get("success") and supplies_result.get("result", {}).get("data"):
        supplies_list = supplies_result["result"]["data"]
        
        # Find supplies with stock
        available_supply = next((s for s in supplies_list if s.get('current_stock', 0) > 0), None)
        
        if available_supply:
            # Update supply stock (allocate some for the patient)
            supply_assign = make_mcp_request("update_supply_stock", {
                "item_code": available_supply.get("item_code"),
                "new_stock": max(0, available_supply.get('current_stock', 0) - 2),  # Allocate 2 units
                "notes": f"Allocated 2 units for patient {PATIENT_NAME}"
            }, 10)
            
            return {"supply": available_supply, "allocated": 2, "result": supply_assign}
    
    return None

def verify_assignments():
    """Verify assignments by checking patient details"""
    print("\n✅ VERIFYING PATIENT ASSIGNMENTS...")
    
    # Get patient details to see current assignments
    patient_result = make_mcp_request("get_patient_by_id", {"patient_id": PATIENT_ID}, 11)
    
    return patient_result

def main():
    """Execute complete assignment workflow"""
    print("🚀 STARTING COMPLETE PATIENT ASSIGNMENT WORKFLOW")
    print(f"   Patient: {PATIENT_NAME}")
    print(f"   Patient ID: {PATIENT_ID}")
    print("=" * 80)
    
    results = {}
    
    # 1. Assign bed
    print("\n1️⃣ BED ASSIGNMENT")
    results['bed'] = assign_bed()
    
    # 2. Assign staff
    print("\n2️⃣ STAFF ASSIGNMENT")
    results['staff'] = assign_staff()
    
    # 3. Assign equipment
    print("\n3️⃣ EQUIPMENT ASSIGNMENT")
    results['equipment'] = assign_equipment()
    
    # 4. Assign supplies
    print("\n4️⃣ SUPPLY ALLOCATION")
    results['supplies'] = assign_supplies()
    
    # 5. Verify all assignments
    print("\n5️⃣ VERIFICATION")
    results['verification'] = verify_assignments()
    
    print("\n" + "=" * 80)
    print("📋 ASSIGNMENT SUMMARY:")
    
    for assignment_type, result in results.items():
        if result:
            print(f"   ✅ {assignment_type.upper()}: Success")
        else:
            print(f"   ❌ {assignment_type.upper()}: Failed")
    
    print("=" * 80)
    
    # Show assignment details
    if results.get('bed'):
        print(f"\n🏨 BED: {results['bed'].get('bed_number', 'Unknown')}")
    
    if results.get('staff'):
        print(f"\n👨‍⚕️ STAFF:")
        for assignment in results['staff']:
            staff_name = f"{assignment['staff'].get('first_name', '')} {assignment['staff'].get('last_name', '')}"
            print(f"   - {assignment['type'].title()}: {staff_name}")
    
    if results.get('equipment'):
        equipment_name = results['equipment']['equipment'].get('name', 'Unknown')
        print(f"\n🔧 EQUIPMENT: {equipment_name}")
    
    if results.get('supplies'):
        supply_name = results['supplies']['supply'].get('name', 'Unknown')
        allocated = results['supplies']['allocated']
        print(f"\n📦 SUPPLIES: {supply_name} (Allocated: {allocated} units)")
    
    return results

if __name__ == "__main__":
    main()
