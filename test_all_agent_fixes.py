#!/usr/bin/env python3
"""Comprehensive test for all agent field name fixes"""

import json
import requests
import time

API_URL = "http://localhost:8000"

def test_agent_operations():
    """Test all agents with corrected field names"""
    print("🧪 Testing All Agent Operations with Corrected Field Names")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Department Agent (should already work)
    print("\n1. Testing Department Agent...")
    dept_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "create_department",
            "arguments": {
                "name": "Fixed Department Test",
                "description": "Testing after field fixes",
                "floor_number": 5
            }
        }
    }
    results["department"] = test_api_call(dept_data, "Department creation")
    
    # Test 2: Patient Agent (should already work)
    print("\n2. Testing Patient Agent...")
    patient_data = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "create_patient",
            "arguments": {
                "first_name": "Fixed",
                "last_name": "Patient",
                "date_of_birth": "1985-05-15",
                "gender": "Female",
                "phone": "555-9999",
                "email": "fixed.patient@test.com"
            }
        }
    }
    results["patient"] = test_api_call(patient_data, "Patient creation")
    
    # Test 3: Staff Agent (should now work with fixes)
    print("\n3. Testing Staff Agent (Fixed)...")
    # First get a department ID
    dept_id = get_department_id()
    if dept_id:
        staff_data = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "create_staff",
                "arguments": {
                    "first_name": "Dr. Fixed",
                    "last_name": "Doctor",
                    "role": "Doctor",
                    "department_id": dept_id,
                    "phone": "555-7777",
                    "email": "fixed.doctor@hospital.com"
                }
            }
        }
        results["staff"] = test_api_call(staff_data, "Staff creation")
    else:
        results["staff"] = {"success": False, "message": "No department available"}
    
    # Test 4: Room Agent (should now work with fixes)
    print("\n4. Testing Room Agent (Fixed)...")
    if dept_id:
        room_data = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "create_room",
                "arguments": {
                    "room_number": "R101",
                    "department_id": dept_id,
                    "room_type": "private",
                    "floor_number": 1,
                    "capacity": 2
                }
            }
        }
        results["room"] = test_api_call(room_data, "Room creation")
    else:
        results["room"] = {"success": False, "message": "No department available"}
    
    # Test 5: Equipment Category and Equipment
    print("\n5. Testing Equipment Agent...")
    # Create category first
    eq_cat_data = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "create_equipment_category",
            "arguments": {
                "name": "Medical Devices",
                "description": "Essential medical equipment"
            }
        }
    }
    cat_result = test_api_call(eq_cat_data, "Equipment category creation")
    
    if cat_result["success"]:
        category_id = extract_result_id(cat_result)
        equipment_data = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "create_equipment",
                "arguments": {
                    "equipment_id": "EQ001",
                    "name": "MRI Scanner",
                    "category_id": category_id,
                    "model": "MRI-3000",
                    "manufacturer": "MedTech Inc",
                    "status": "available"
                }
            }
        }
        results["equipment"] = test_api_call(equipment_data, "Equipment creation")
    else:
        results["equipment"] = {"success": False, "message": "Equipment category creation failed"}
    
    # Test 6: Supply Category and Supply (Fixed)
    print("\n6. Testing Inventory Agent (Fixed)...")
    supply_cat_data = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "create_supply_category",
            "arguments": {
                "name": "Medical Supplies",
                "description": "Basic medical supplies"
            }
        }
    }
    sup_cat_result = test_api_call(supply_cat_data, "Supply category creation")
    
    if sup_cat_result["success"]:
        supply_category_id = extract_result_id(sup_cat_result)
        supply_data = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "create_supply",
                "arguments": {
                    "item_code": "SUP001",
                    "name": "Surgical Gloves",
                    "category_id": supply_category_id,
                    "unit_of_measure": "box",
                    "current_stock": 100,
                    "minimum_stock_level": 10,
                    "maximum_stock_level": 500,
                    "unit_cost": 15.99,
                    "supplier": "MedSupply Corp"
                }
            }
        }
        results["supply"] = test_api_call(supply_data, "Supply creation")
    else:
        results["supply"] = {"success": False, "message": "Supply category creation failed"}
    
    # Test 7: Appointment Agent (Fixed)
    print("\n7. Testing Appointment Agent (Fixed)...")
    patient_id = get_patient_id()
    doctor_id = get_staff_user_id()
    
    if patient_id and doctor_id and dept_id:
        appointment_data = {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "create_appointment",
                "arguments": {
                    "patient_id": patient_id,
                    "doctor_id": doctor_id,
                    "department_id": dept_id,
                    "appointment_date": "2025-08-20",
                    "appointment_time": "10:00",
                    "reason": "Regular checkup",
                    "duration_minutes": 30
                }
            }
        }
        results["appointment"] = test_api_call(appointment_data, "Appointment creation")
    else:
        results["appointment"] = {"success": False, "message": "Missing patient, doctor, or department"}
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 Test Results Summary:")
    success_count = 0
    total_count = len(results)
    
    for agent, result in results.items():
        status = "✅ PASS" if result.get("success") else "❌ FAIL"
        message = result.get("message", "Unknown error")
        print(f"   {agent.capitalize()}: {status} - {message}")
        if result.get("success"):
            success_count += 1
    
    print(f"\n📊 Overall: {success_count}/{total_count} agents working correctly")
    
    if success_count == total_count:
        print("🎉 All field name mismatches have been fixed!")
    else:
        print("⚠️ Some agents still have issues. Check the error messages above.")

def test_api_call(request_data, operation_name):
    """Helper function to test API calls"""
    try:
        response = requests.post(
            f"{API_URL}/tools/call",
            headers={"Content-Type": "application/json"},
            json=request_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result and "content" in result["result"]:
                text_content = result["result"]["content"][0]["text"]
                parsed_result = json.loads(text_content)
                
                if parsed_result.get("success") and parsed_result.get("result", {}).get("success"):
                    print(f"   ✅ {operation_name} successful")
                    return {"success": True, "message": "Operation successful", "data": parsed_result}
                else:
                    error_msg = parsed_result.get("message") or parsed_result.get("result", {}).get("message", "Unknown error")
                    print(f"   ❌ {operation_name} failed: {error_msg}")
                    return {"success": False, "message": error_msg}
            else:
                print(f"   ❌ {operation_name} failed: Invalid response format")
                return {"success": False, "message": "Invalid response format"}
        else:
            print(f"   ❌ {operation_name} failed: HTTP {response.status_code}")
            return {"success": False, "message": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"   ❌ {operation_name} failed: {str(e)}")
        return {"success": False, "message": str(e)}

def get_department_id():
    """Get a department ID for testing"""
    try:
        response = requests.post(
            f"{API_URL}/tools/call",
            headers={"Content-Type": "application/json"},
            json={
                "jsonrpc": "2.0",
                "id": 999,
                "method": "tools/call",
                "params": {"name": "list_departments", "arguments": {}}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            text_content = result["result"]["content"][0]["text"]
            parsed_result = json.loads(text_content)
            
            if parsed_result.get("success") and parsed_result.get("result", {}).get("data"):
                departments = parsed_result["result"]["data"]
                if departments:
                    return departments[0]["id"]
        return None
    except:
        return None

def get_patient_id():
    """Get a patient ID for testing"""
    try:
        response = requests.post(
            f"{API_URL}/tools/call",
            headers={"Content-Type": "application/json"},
            json={
                "jsonrpc": "2.0",
                "id": 998,
                "method": "tools/call",
                "params": {"name": "list_patients", "arguments": {}}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            text_content = result["result"]["content"][0]["text"]
            parsed_result = json.loads(text_content)
            
            if parsed_result.get("success") and parsed_result.get("result", {}).get("data"):
                patients = parsed_result["result"]["data"]
                if patients:
                    return patients[0]["id"]
        return None
    except:
        return None

def get_staff_user_id():
    """Get a user ID from staff for testing"""
    try:
        response = requests.post(
            f"{API_URL}/tools/call",
            headers={"Content-Type": "application/json"},
            json={
                "jsonrpc": "2.0",
                "id": 997,
                "method": "tools/call",
                "params": {"name": "list_staff", "arguments": {}}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            text_content = result["result"]["content"][0]["text"]
            parsed_result = json.loads(text_content)
            
            if parsed_result.get("success") and parsed_result.get("result", {}).get("data"):
                staff = parsed_result["result"]["data"]
                if staff:
                    return staff[0]["user_id"]
        return None
    except:
        return None

def extract_result_id(result):
    """Extract ID from API result"""
    try:
        return result["data"]["result"]["data"]["id"]
    except:
        return None

def main():
    print("🔍 Comprehensive Agent Field Name Fix Verification")
    print("Testing all agents after fixing database field mismatches")
    print("=" * 70)
    
    # Test server connection
    try:
        health_response = requests.get(f"{API_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server not responding")
            return
    except Exception as e:
        print(f"❌ Cannot reach server: {e}")
        return
    
    # Run comprehensive tests
    test_agent_operations()

if __name__ == "__main__":
    main()
