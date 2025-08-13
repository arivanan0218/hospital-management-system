#!/usr/bin/env python3
"""Test script to simulate frontend user actions"""

import json
import requests
import time

SERVER_URL = "http://localhost:5173"  # Frontend URL
API_URL = "http://localhost:8000"     # Backend API URL

def test_frontend_backend_integration():
    """Test the complete frontend-backend integration"""
    print("🧪 Testing Frontend-Backend Integration")
    print("=" * 50)
    
    # Test 1: Create a patient (this is what users reported as failing)
    print("\n1. Testing Patient Creation...")
    patient_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "create_patient",
            "arguments": {
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1990-01-15",
                "gender": "Male",
                "phone": "555-1234",
                "email": "john.doe@email.com",
                "address": "123 Main St, City, State"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{API_URL}/tools/call",
            headers={"Content-Type": "application/json"},
            json=patient_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result and "content" in result["result"]:
                text_content = result["result"]["content"][0]["text"]
                parsed_result = json.loads(text_content)
                
                if parsed_result.get("success") and parsed_result.get("result", {}).get("success"):
                    patient_info = parsed_result["result"]["data"]
                    print(f"✅ Patient created successfully!")
                    print(f"   Patient ID: {patient_info['id']}")
                    print(f"   Patient Number: {patient_info['patient_number']}")
                    print(f"   Name: {patient_info['first_name']} {patient_info['last_name']}")
                else:
                    print(f"❌ Patient creation failed: {parsed_result}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Patient creation failed: {e}")
    
    # Test 2: Create a staff member 
    print("\n2. Testing Staff Creation...")
    staff_data = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "create_staff",
            "arguments": {
                "first_name": "Dr. Jane",
                "last_name": "Smith",
                "role": "Doctor",
                "department_id": "31da92cd-ed47-449f-ba13-5ff7fb5aa722",  # Using existing department
                "phone": "555-5678",
                "email": "jane.smith@hospital.com",
                "employee_id": "EMP001"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{API_URL}/tools/call",
            headers={"Content-Type": "application/json"},
            json=staff_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result and "content" in result["result"]:
                text_content = result["result"]["content"][0]["text"]
                parsed_result = json.loads(text_content)
                
                if parsed_result.get("success") and parsed_result.get("result", {}).get("success"):
                    staff_info = parsed_result["result"]["data"]
                    print(f"✅ Staff created successfully!")
                    print(f"   Staff ID: {staff_info['id']}")
                    print(f"   Employee ID: {staff_info['employee_id']}")
                    print(f"   Name: {staff_info['first_name']} {staff_info['last_name']}")
                else:
                    print(f"❌ Staff creation failed: {parsed_result}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Staff creation failed: {e}")
    
    # Test 3: List all data to verify persistence
    print("\n3. Testing Data Retrieval...")
    
    # List patients
    try:
        response = requests.post(
            f"{API_URL}/tools/call",
            headers={"Content-Type": "application/json"},
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "list_patients", "arguments": {}}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            text_content = result["result"]["content"][0]["text"]
            parsed_result = json.loads(text_content)
            
            if parsed_result.get("success"):
                patients = parsed_result["result"]["data"]
                print(f"✅ Found {len(patients)} patients in database")
                for patient in patients[-2:]:  # Show last 2 patients
                    print(f"   - {patient['first_name']} {patient['last_name']} ({patient['patient_number']})")
            else:
                print(f"❌ Failed to list patients: {parsed_result}")
                
    except Exception as e:
        print(f"❌ Failed to list patients: {e}")
    
    # List staff
    try:
        response = requests.post(
            f"{API_URL}/tools/call",
            headers={"Content-Type": "application/json"},
            json={
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "list_staff", "arguments": {}}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            text_content = result["result"]["content"][0]["text"]
            parsed_result = json.loads(text_content)
            
            if parsed_result.get("success"):
                staff = parsed_result["result"]["data"]
                print(f"✅ Found {len(staff)} staff members in database")
                for member in staff[-2:]:  # Show last 2 staff
                    print(f"   - {member['first_name']} {member['last_name']} ({member['role']})")
            else:
                print(f"❌ Failed to list staff: {parsed_result}")
                
    except Exception as e:
        print(f"❌ Failed to list staff: {e}")

def main():
    print("🔍 Testing Complete Hospital Management System Integration")
    print("Testing the same operations that users would perform in the frontend")
    print("=" * 70)
    
    # First verify both servers are running
    try:
        # Check backend
        backend_health = requests.get(f"{API_URL}/health", timeout=5)
        if backend_health.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server not responding")
            return
            
        # Check frontend
        frontend_health = requests.get(f"{SERVER_URL}/", timeout=5)
        if frontend_health.status_code == 200:
            print("✅ Frontend server is running")
        else:
            print("❌ Frontend server not responding")
            return
            
    except Exception as e:
        print(f"❌ Server connectivity issue: {e}")
        return
    
    # Run the integration tests
    test_frontend_backend_integration()
    
    print("\n" + "=" * 70)
    print("🎯 Integration Test Complete!")
    print("If all tests passed, the POST functions are working correctly.")
    print("If users report issues, they might be in the frontend UI handling.")

if __name__ == "__main__":
    main()
