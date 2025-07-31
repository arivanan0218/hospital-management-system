#!/usr/bin/env python3
"""Test script for the Hospital Management System MCP Server."""

import json
import sys
from pathlib import Path

# Add the current directory to the path so we can import our server
sys.path.insert(0, str(Path(__file__).parent))

from server import (
    create_user, 
    create_random_user, 
    get_user_by_id, 
    list_users, 
    delete_user, 
    update_user,
    load_users,
    save_users
)

def test_basic_functionality():
    """Test basic CRUD operations."""
    print("=== Testing Hospital Management System Server ===\n")
    
    # Test 1: List initial users
    print("1. Testing list_users():")
    result = list_users()
    print(f"   Initial users count: {result['count']}")
    print(f"   Users: {json.dumps(result, indent=2)}\n")
    
    # Test 2: Create a new user
    print("2. Testing create_user():")
    create_result = create_user(
        name="John Doe Test",
        email="john.test@example.com",
        address="123 Test Street, Test City, TS 12345",
        phone="(555) 123-4567"
    )
    print(f"   Create result: {json.dumps(create_result.model_dump(), indent=2)}")
    
    if create_result.success:
        new_user_id = create_result.user_id
        print(f"   New user ID: {new_user_id}\n")
        
        # Test 3: Get user by ID
        print("3. Testing get_user_by_id():")
        user_result = get_user_by_id(new_user_id)
        print(f"   User details: {json.dumps(user_result, indent=2)}\n")
        
        # Test 4: Update user
        print("4. Testing update_user():")
        update_result = update_user(
            user_id=new_user_id,
            name="John Doe Updated",
            email="john.updated@example.com"
        )
        print(f"   Update result: {json.dumps(update_result, indent=2)}\n")
        
        # Test 5: List users again to see the changes
        print("5. Testing list_users() after updates:")
        result = list_users()
        print(f"   Users count: {result['count']}")
        print(f"   Users: {json.dumps(result, indent=2)}\n")
        
        # Test 6: Delete user
        print("6. Testing delete_user():")
        delete_result = delete_user(new_user_id)
        print(f"   Delete result: {json.dumps(delete_result, indent=2)}\n")
    
    # Test 7: Create random user
    print("7. Testing create_random_user():")
    random_result = create_random_user()
    print(f"   Random user result: {json.dumps(random_result.model_dump(), indent=2)}\n")
    
    # Test 8: Final user list
    print("8. Final user list:")
    final_result = list_users()
    print(f"   Final users count: {final_result['count']}")
    print(f"   Users: {json.dumps(final_result, indent=2)}\n")
    
    print("=== Test completed successfully! ===")

if __name__ == "__main__":
    test_basic_functionality()
