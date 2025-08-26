"""
Complete Patient Assignment Script for Mohamed Nazif
This script assigns bed, staff, equipment, and supplies to the patient using correct table structures
"""

import requests
import json
from datetime import datetime, timedelta
import uuid

# Configuration
BASE_URL = "http://localhost:8000"

# Patient details (known from previous queries)
PATIENT_ID = "c36ddebf-0885-4c90-a035-bc36eaf28480"
PATIENT_NAME = "Mohamed Nazif"

# Assignment data
BED_ID = "302B"  # Will be converted to UUID by backend
STAFF_ASSIGNMENT_TYPE = "primary_nurse"
EQUIPMENT_TYPE = "IV_PUMP"
SUPPLY_TRANSACTION_TYPE = "ALLOCATION"

def make_api_request(endpoint, data):
    """Make API request to MCP server"""
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        print(f"📡 API Request to {endpoint}")
        print(f"   Request data: {json.dumps(data, indent=2)}")
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"   ❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"   💥 Exception: {str(e)}")
        return None

def assign_bed():
    """Assign bed to patient using bed_staff_assignments table"""
    print("\n🏨 ASSIGNING BED TO PATIENT...")
    
    # Use the bed assignment API
    data = {
        "patient_id": PATIENT_ID,
        "bed_id": BED_ID,
        "assignment_type": "patient_admission",
        "notes": f"Bed assignment for {PATIENT_NAME}"
    }
    
    return make_api_request("/api/assign_bed", data)

def assign_staff():
    """Assign staff to patient using staff_assignments table"""
    print("\n👨‍⚕️ ASSIGNING STAFF TO PATIENT...")
    
    # Get available staff first
    staff_result = make_api_request("/api/get_available_staff", {})
    
    if staff_result and staff_result.get('available_staff'):
        # Pick the first available nurse
        available_staff = staff_result['available_staff']
        nurse = None
        doctor = None
        
        for staff in available_staff:
            if 'nurse' in staff.get('position', '').lower():
                nurse = staff
            elif 'doctor' in staff.get('position', '').lower():
                doctor = staff
        
        assignments = []
        
        # Assign nurse
        if nurse:
            nurse_data = {
                "patient_id": PATIENT_ID,
                "staff_id": nurse['id'],
                "assignment_type": "primary_nurse",
                "shift": "day",
                "responsibilities": f"Primary nursing care for {PATIENT_NAME}",
                "notes": f"Nurse assignment for patient {PATIENT_NAME}"
            }
            nurse_result = make_api_request("/api/assign_staff", nurse_data)
            assignments.append(('nurse', nurse_result))
        
        # Assign doctor
        if doctor:
            doctor_data = {
                "patient_id": PATIENT_ID,
                "staff_id": doctor['id'],
                "assignment_type": "attending_physician",
                "shift": "day",
                "responsibilities": f"Medical care for {PATIENT_NAME}",
                "notes": f"Doctor assignment for patient {PATIENT_NAME}"
            }
            doctor_result = make_api_request("/api/assign_staff", doctor_data)
            assignments.append(('doctor', doctor_result))
        
        return assignments
    
    return None

def assign_equipment():
    """Assign equipment to patient using equipment_usage table"""
    print("\n🔧 ASSIGNING EQUIPMENT TO PATIENT...")
    
    # Get available equipment first
    equipment_result = make_api_request("/api/get_available_equipment", {})
    
    if equipment_result and equipment_result.get('available_equipment'):
        available_equipment = equipment_result['available_equipment']
        
        # Pick the first available equipment
        if available_equipment:
            equipment = available_equipment[0]
            
            # Get available staff for the equipment assignment
            staff_result = make_api_request("/api/get_available_staff", {})
            
            if staff_result and staff_result.get('available_staff'):
                staff = staff_result['available_staff'][0]
                
                equipment_data = {
                    "patient_id": PATIENT_ID,
                    "equipment_id": equipment['id'],
                    "staff_id": staff['id'],
                    "bed_id": BED_ID,
                    "purpose": f"Medical equipment for {PATIENT_NAME}",
                    "notes": f"Equipment assignment for patient {PATIENT_NAME}"
                }
                
                return make_api_request("/api/assign_equipment", equipment_data)
    
    return None

def assign_supplies():
    """Allocate supplies from inventory using inventory_transactions table"""
    print("\n📦 ALLOCATING SUPPLIES FOR PATIENT...")
    
    # Get available supplies first
    supplies_result = make_api_request("/api/get_available_supplies", {})
    
    if supplies_result and supplies_result.get('available_supplies'):
        available_supplies = supplies_result['available_supplies']
        
        # Allocate some supplies
        if available_supplies:
            supply = available_supplies[0]
            
            # Get available staff for the transaction
            staff_result = make_api_request("/api/get_available_staff", {})
            
            if staff_result and staff_result.get('available_staff'):
                staff = staff_result['available_staff'][0]
                
                supply_data = {
                    "supply_id": supply['id'],
                    "transaction_type": "ALLOCATION",
                    "quantity": 5,
                    "reference_number": f"PATIENT_{PATIENT_NAME.replace(' ', '_').upper()}",
                    "notes": f"Supply allocation for patient {PATIENT_NAME}",
                    "performed_by": staff['id']
                }
                
                return make_api_request("/api/allocate_supplies", supply_data)
    
    return None

def verify_assignments():
    """Verify all assignments are stored in database"""
    print("\n✅ VERIFYING ASSIGNMENTS IN DATABASE...")
    
    verification_data = {
        "patient_id": PATIENT_ID,
        "patient_name": PATIENT_NAME
    }
    
    return make_api_request("/api/verify_patient_assignments", verification_data)

def main():
    """Execute complete assignment workflow"""
    print("🚀 STARTING COMPLETE PATIENT ASSIGNMENT WORKFLOW")
    print(f"   Patient: {PATIENT_NAME}")
    print(f"   Patient ID: {PATIENT_ID}")
    print("=" * 80)
    
    results = {}
    
    # 1. Assign bed
    results['bed'] = assign_bed()
    
    # 2. Assign staff
    results['staff'] = assign_staff()
    
    # 3. Assign equipment
    results['equipment'] = assign_equipment()
    
    # 4. Assign supplies
    results['supplies'] = assign_supplies()
    
    # 5. Verify all assignments
    results['verification'] = verify_assignments()
    
    print("\n" + "=" * 80)
    print("📋 ASSIGNMENT SUMMARY:")
    
    for assignment_type, result in results.items():
        if result:
            print(f"   ✅ {assignment_type.upper()}: Success")
        else:
            print(f"   ❌ {assignment_type.upper()}: Failed")
    
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    main()
