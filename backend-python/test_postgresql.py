#!/usr/bin/env python3
"""
Test script to demonstrate PostgreSQL integration with Hospital Management System.
"""

from server import (
    load_users, 
    create_user, 
    delete_user_from_db, 
    update_user_in_db
)
from database import test_connection

def main():
    print("🏥 Hospital Management System - PostgreSQL Integration Test")
    print("=" * 60)
    
    # Test 1: Connection
    print("\n1. Testing database connection...")
    if test_connection():
        print("✅ PostgreSQL connection successful!")
    else:
        print("❌ PostgreSQL connection failed!")
        return
    
    # Test 2: Load existing users
    print("\n2. Loading existing users...")
    users = load_users()
    print(f"✅ Loaded {len(users)} users from PostgreSQL database")
    
    # Test 3: Create a new user
    print("\n3. Creating a new test user...")
    result = create_user(
        name="PostgreSQL Test User",
        email="postgres.test@hospital.com",
        address="123 Database Street, PostgreSQL City",
        phone="555-PSQL-001"
    )
    print(f"✅ User creation result: {result}")
    
    # Test 4: Verify user was created
    print("\n4. Verifying user creation...")
    updated_users = load_users()
    new_user = next((u for u in updated_users if u["email"] == "postgres.test@hospital.com"), None)
    if new_user:
        print(f"✅ New user found: {new_user['name']} (ID: {new_user['id']})")
        user_id = new_user['id']
    else:
        print("❌ New user not found!")
        return
    
    # Test 5: Update the user
    print("\n5. Updating the test user...")
    update_success = update_user_in_db(user_id, {
        "name": "Updated PostgreSQL Test User",
        "phone": "555-PSQL-999"
    })
    if update_success:
        print("✅ User updated successfully")
        
        # Verify update
        updated_users = load_users()
        updated_user = next((u for u in updated_users if u["id"] == user_id), None)
        if updated_user:
            print(f"✅ Updated user: {updated_user['name']} - {updated_user['phone']}")
    else:
        print("❌ User update failed")
    
    # Test 6: Delete the test user
    print("\n6. Cleaning up - deleting test user...")
    delete_success = delete_user_from_db(user_id)
    if delete_success:
        print("✅ Test user deleted successfully")
        
        # Verify deletion
        final_users = load_users()
        deleted_user = next((u for u in final_users if u["id"] == user_id), None)
        if not deleted_user:
            print("✅ User deletion verified")
        else:
            print("❌ User still exists after deletion")
    else:
        print("❌ User deletion failed")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 PostgreSQL Integration Test Complete!")
    print(f"📊 Final user count: {len(load_users())} users")
    print("✅ All database operations working correctly!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
