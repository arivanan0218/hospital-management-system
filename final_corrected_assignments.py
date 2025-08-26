"""
FINAL CORRECTED Patient Assignment Script for Mohamed Nazif
This script fixes all the identified issues and completes the assignments
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

def assign_bed_corrected():
    """Assign bed with corrected date format (no 'T')"""
    print("\n🏨 ASSIGNING BED WITH CORRECTED DATE FORMAT...")
    
    # Get available beds
    beds_result = make_mcp_request("list_beds", {"status": "available"}, 1)
    
    if beds_result and beds_result.get("success"):
        beds = beds_result["result"]["data"]
        
        # Find a suitable bed (avoid 401A which is cleaning)
        suitable_bed = None
        for bed in beds:
            if bed.get("bed_number") != "401A":
                suitable_bed = bed
                break
        
        if suitable_bed:
            bed_id = suitable_bed.get("id")
            bed_number = suitable_bed.get("bed_number")
            
            # Use corrected date format (YYYY-MM-DD HH:MM:SS without 'T')
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"   📅 Using date format: {current_time}")
            print(f"   🛏️ Assigning bed: {bed_number}")
            
            assign_result = make_mcp_request("assign_bed_to_patient", {
                "bed_id": bed_id,
                "patient_id": PATIENT_ID,
                "admission_date": current_time
            }, 2)
            
            if assign_result and assign_result.get("success"):
                print(f"   ✅ Bed assignment successful!")
                return {"bed_number": bed_number, "result": assign_result}
            else:
                print(f"   ❌ Bed assignment failed: {assign_result}")
                return None
    
    return None

def assign_equipment_corrected():
    """Assign equipment with corrected UUID and parameters"""
    print("\n🔧 ASSIGNING EQUIPMENT WITH CORRECTED FORMAT...")
    
    # Get available equipment
    equipment_result = make_mcp_request("list_equipment", {}, 3)
    
    if equipment_result and equipment_result.get("success"):
        equipment_list = equipment_result["result"]["data"]
        
        # Find available equipment
        available_equipment = next((e for e in equipment_list if e.get('status') == 'available'), None)
        
        if available_equipment:
            # Get staff for the assignment
            staff_result = make_mcp_request("list_staff", {}, 4)
            
            if staff_result and staff_result.get("success"):
                staff_list = staff_result["result"]["data"]
                staff_member = staff_list[0] if staff_list else None
                
                if staff_member:
                    # Use the UUID id instead of equipment_id
                    equipment_uuid = available_equipment.get("id")  # Use UUID, not equipment_id
                    staff_uuid = staff_member.get("id")
                    
                    print(f"   🔧 Equipment: {available_equipment.get('name')}")
                    print(f"   🆔 Equipment UUID: {equipment_uuid}")
                    print(f"   👤 Staff: {staff_member.get('first_name')} {staff_member.get('last_name')}")
                    print(f"   🆔 Staff UUID: {staff_uuid}")
                    
                    # Try add_equipment_usage instead of add_equipment_usage_simple
                    equipment_assign = make_mcp_request("add_equipment_usage", {
                        "patient_id": PATIENT_ID,
                        "equipment_id": equipment_uuid,  # Use UUID
                        "staff_id": staff_uuid,
                        "purpose": "patient_care",
                        "duration_minutes": 60,
                        "settings": "Standard configuration",
                        "readings": "Normal operation"
                    }, 5)
                    
                    if equipment_assign and equipment_assign.get("success"):
                        print(f"   ✅ Equipment assignment successful!")
                        return {"equipment": available_equipment, "staff": staff_member, "result": equipment_assign}
                    else:
                        print(f"   ❌ Equipment assignment failed: {equipment_assign}")
                        
                        # Try alternative approach with equipment_id instead of UUID
                        print("   🔄 Trying with equipment_id instead of UUID...")
                        equipment_assign2 = make_mcp_request("add_equipment_usage", {
                            "patient_id": PATIENT_ID,
                            "equipment_id": available_equipment.get("equipment_id"),  # Try equipment_id
                            "staff_id": staff_uuid,
                            "purpose": "patient_care",
                            "duration_minutes": 60
                        }, 6)
                        
                        if equipment_assign2 and equipment_assign2.get("success"):
                            print(f"   ✅ Equipment assignment successful with equipment_id!")
                            return {"equipment": available_equipment, "staff": staff_member, "result": equipment_assign2}
                        else:
                            print(f"   ❌ Equipment assignment failed again: {equipment_assign2}")
    
    return None

def allocate_supplies_corrected():
    """Allocate supplies with corrected parameters"""
    print("\n📦 ALLOCATING SUPPLIES WITH CORRECTED PARAMETERS...")
    
    # Get available supplies
    supplies_result = make_mcp_request("list_supplies", {}, 7)
    
    if supplies_result and supplies_result.get("success"):
        supplies_list = supplies_result["result"]["data"]
        
        # Find supplies with stock
        available_supply = next((s for s in supplies_list if s.get('current_stock', 0) > 0), None)
        
        if available_supply:
            # Get staff to perform the transaction
            staff_result = make_mcp_request("list_staff", {}, 8)
            
            if staff_result and staff_result.get("success"):
                staff_list = staff_result["result"]["data"]
                staff_member = staff_list[0] if staff_list else None
                
                if staff_member:
                    supply_id = available_supply.get("id")
                    staff_id = staff_member.get("id")
                    current_stock = available_supply.get('current_stock', 0)
                    allocation_qty = 2
                    
                    print(f"   📦 Supply: {available_supply.get('name')}")
                    print(f"   📊 Current stock: {current_stock}")
                    print(f"   📉 Allocating: {allocation_qty} units")
                    print(f"   👤 Performed by: {staff_member.get('first_name')} {staff_member.get('last_name')}")
                    
                    # Try creating an inventory transaction for allocation
                    # Based on the error, we need: supply_id, quantity_change, transaction_type, performed_by
                    supply_transaction = make_mcp_request("create_inventory_transaction", {
                        "supply_id": supply_id,
                        "transaction_type": "ALLOCATION",
                        "quantity": allocation_qty,
                        "unit_cost": 1.00,
                        "total_cost": allocation_qty * 1.00,
                        "reference_number": f"ALLOC_{PATIENT_NAME.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}",
                        "notes": f"Supply allocation for patient {PATIENT_NAME}",
                        "performed_by": staff_id
                    }, 9)
                    
                    if supply_transaction and supply_transaction.get("success"):
                        print(f"   ✅ Supply allocation successful!")
                        return {"supply": available_supply, "allocated": allocation_qty, "result": supply_transaction}
                    else:
                        print(f"   ❌ Supply allocation failed: {supply_transaction}")
                        
                        # Try alternative approach - direct stock update
                        print("   🔄 Trying direct stock update...")
                        new_stock = max(0, current_stock - allocation_qty)
                        stock_update = make_mcp_request("update_supply_stock", {
                            "supply_id": supply_id,
                            "new_stock": new_stock,
                            "notes": f"Allocated {allocation_qty} units for patient {PATIENT_NAME}"
                        }, 10)
                        
                        if stock_update and stock_update.get("success"):
                            print(f"   ✅ Supply stock updated successfully!")
                            return {"supply": available_supply, "allocated": allocation_qty, "result": stock_update}
                        else:
                            print(f"   ❌ Supply stock update failed: {stock_update}")
    
    return None

def main():
    """Execute corrected assignment workflow"""
    print("🚀 FINAL CORRECTED PATIENT ASSIGNMENT WORKFLOW")
    print(f"   Patient: {PATIENT_NAME}")
    print(f"   Patient ID: {PATIENT_ID}")
    print("=" * 80)
    
    results = {}
    
    # Note: Staff assignment was already successful, so we'll skip it
    print("\n✅ STAFF ASSIGNMENT: Already completed successfully (Mary Brown assigned)")
    results['staff'] = {"status": "previously_completed", "nurse": "Mary Brown"}
    
    # 1. Assign bed with corrected date format
    print("\n1️⃣ BED ASSIGNMENT (CORRECTED)")
    results['bed'] = assign_bed_corrected()
    
    # 2. Assign equipment with corrected UUID format
    print("\n2️⃣ EQUIPMENT ASSIGNMENT (CORRECTED)")
    results['equipment'] = assign_equipment_corrected()
    
    # 3. Allocate supplies with corrected parameters
    print("\n3️⃣ SUPPLY ALLOCATION (CORRECTED)")
    results['supplies'] = allocate_supplies_corrected()
    
    print("\n" + "=" * 80)
    print("📋 FINAL ASSIGNMENT SUMMARY:")
    
    for assignment_type, result in results.items():
        if result:
            print(f"   ✅ {assignment_type.upper()}: Success")
        else:
            print(f"   ❌ {assignment_type.upper()}: Failed")
    
    print("\n🎯 RESOURCE ASSIGNMENTS FOR MOHAMED NAZIF:")
    print(f"   👤 Patient: {PATIENT_NAME} (ID: {PATIENT_ID})")
    print(f"   👩‍⚕️ Nurse: Mary Brown (Previously assigned)")
    
    if results.get('bed'):
        print(f"   🛏️ Bed: {results['bed'].get('bed_number', 'Unknown')}")
    
    if results.get('equipment'):
        equipment_name = results['equipment']['equipment'].get('name', 'Unknown')
        print(f"   🔧 Equipment: {equipment_name}")
    
    if results.get('supplies'):
        supply_name = results['supplies']['supply'].get('name', 'Unknown')
        allocated = results['supplies']['allocated']
        print(f"   📦 Supplies: {supply_name} (Allocated: {allocated} units)")
    
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    main()
