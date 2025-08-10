#!/usr/bin/env python3
"""
Create sample data for testing foreign key resolution
"""
import requests
import json
import uuid

BASE_URL = "http://127.0.0.1:8000"

def call_tool(tool_name, arguments):
    """Call a tool via HTTP"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    response = requests.post(f"{BASE_URL}/tools/call", json=payload)
    if response.status_code == 200:
        result = response.json()
        if "result" in result:
            # Parse the nested JSON string
            content = result["result"].get("content", [])
            if content and len(content) > 0:
                text_content = content[0].get("text", "{}")
                try:
                    parsed_data = json.loads(text_content)
                    print(f"✅ {tool_name}: Success")
                    return parsed_data
                except json.JSONDecodeError:
                    print(f"❌ {tool_name}: Failed to parse JSON - {text_content[:100]}...")
                    return None
            else:
                print(f"❌ {tool_name}: No content in response")
                return None
        else:
            print(f"❌ {tool_name}: {result}")
            return None
    else:
        print(f"❌ {tool_name}: {response.status_code} - {response.text}")
        return None

def main():
    print("🏥 Creating sample hospital data...")
    
    # Initialize result arrays
    dept_results = []
    room_results = []
    user_results = []
    staff_results = []
    patient_results = []
    
    # 1. Create departments
    print("\n📋 Creating departments...")
    departments = [
        {"name": "Emergency", "description": "Emergency Department", "floor_number": 1},
        {"name": "Cardiology", "description": "Heart and cardiovascular care", "floor_number": 2},
        {"name": "Orthopedics", "description": "Bone and joint care", "floor_number": 3},
        {"name": "Pediatrics", "description": "Children's healthcare", "floor_number": 2},
        {"name": "ICU", "description": "Intensive Care Unit", "floor_number": 4}
    ]
    
    for dept in departments:
        result = call_tool("create_department", dept)
        if result:
            dept_results.append(result)
    
    # 2. Create rooms in each department
    print("\n🏠 Creating rooms...")
    rooms_data = [
        {"room_number": "101", "department_id": None, "room_type": "Emergency Room", "capacity": 1},
        {"room_number": "102", "department_id": None, "room_type": "Emergency Room", "capacity": 1},
        {"room_number": "201", "department_id": None, "room_type": "Cardiac Care", "capacity": 2},
        {"room_number": "301", "department_id": None, "room_type": "Orthopedic Ward", "capacity": 4},
        {"room_number": "302", "department_id": None, "room_type": "Orthopedic Ward", "capacity": 4},
        {"room_number": "401", "department_id": None, "room_type": "ICU", "capacity": 1},
        {"room_number": "402", "department_id": None, "room_type": "ICU", "capacity": 1}
    ]
    
    # First, get department IDs
    dept_list = call_tool("list_departments", {})
    room_results = []
    if dept_list and 'departments' in dept_list:
        departments_by_name = {}
        for dept in dept_list['departments']:
            departments_by_name[dept['name']] = dept['id']
        
        # Assign departments to rooms
        dept_assignments = {
            "101": "Emergency", "102": "Emergency",
            "201": "Cardiology",
            "301": "Orthopedics", "302": "Orthopedics",
            "401": "ICU", "402": "ICU"
        }
        
        for room in rooms_data:
            dept_name = dept_assignments.get(room["room_number"])
            if dept_name and dept_name in departments_by_name:
                room["department_id"] = departments_by_name[dept_name]
                result = call_tool("create_room", room)
                if result:
                    room_results.append(result)
    
    # 3. Create some users (doctors and nurses)
    print("\n👨‍⚕️ Creating users...")
    users = [
        {"username": "dr_smith", "email": "dr.smith@hospital.com", "password_hash": "hashed_password", "role": "Doctor", "first_name": "John", "last_name": "Smith"},
        {"username": "dr_johnson", "email": "dr.johnson@hospital.com", "password_hash": "hashed_password", "role": "Doctor", "first_name": "Sarah", "last_name": "Johnson"},
        {"username": "nurse_brown", "email": "nurse.brown@hospital.com", "password_hash": "hashed_password", "role": "Nurse", "first_name": "Emily", "last_name": "Brown"},
        {"username": "admin_user", "email": "admin@hospital.com", "password_hash": "hashed_password", "role": "Admin", "first_name": "Admin", "last_name": "User"}
    ]
    
    for user in users:
        result = call_tool("create_user", user)
        if result:
            user_results.append(result)
    
    # 4. Create staff members
    print("\n👩‍⚕️ Creating staff...")
    # Get user IDs first
    user_list = call_tool("list_users", {})
    if user_list and 'users' in user_list:
        users_by_username = {}
        for user in user_list['users']:
            users_by_username[user['username']] = user['id']
        
        staff_data = [
            {"user_id": users_by_username.get("dr_smith"), "employee_id": "EMP001", "department_id": departments_by_name.get("Emergency"), "position": "Senior Doctor"},
            {"user_id": users_by_username.get("dr_johnson"), "employee_id": "EMP002", "department_id": departments_by_name.get("Cardiology"), "position": "Cardiologist"},
            {"user_id": users_by_username.get("nurse_brown"), "employee_id": "EMP003", "department_id": departments_by_name.get("Emergency"), "position": "Head Nurse"}
        ]
        
        for staff in staff_data:
            if staff["user_id"] and staff["department_id"]:
                result = call_tool("create_staff", staff)
                if result:
                    staff_results.append(result)
    
    # 5. Create some patients
    print("\n🤒 Creating patients...")
    patients = [
        {"patient_number": "P001", "first_name": "Alice", "last_name": "Wilson", "date_of_birth": "1985-03-15", "phone": "555-0101"},
        {"patient_number": "P002", "first_name": "Bob", "last_name": "Martinez", "date_of_birth": "1990-07-22", "phone": "555-0102"},
        {"patient_number": "P003", "first_name": "Carol", "last_name": "Davis", "date_of_birth": "1978-12-03", "phone": "555-0103"}
    ]
    
    for patient in patients:
        result = call_tool("create_patient", patient)
        if result:
            patient_results.append(result)
    
    print("\n✅ Sample data creation complete!")
    print(f"Created {len(dept_results)} departments, {len(room_results)} rooms, {len(user_results)} users, {len(staff_results)} staff, {len(patient_results)} patients")

if __name__ == "__main__":
    main()
