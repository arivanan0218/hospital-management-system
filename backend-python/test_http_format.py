"""Test the exact HTTP parameter format that causes issues."""

import requests
import json

def test_parameter_formats():
    """Test different parameter formats to identify the issue."""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Parameter Format Issues")
    print("=" * 50)
    
    # Test 1: Frontend format (what the frontend actually sends)
    print("\n1. Testing Frontend Format...")
    frontend_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "schedule_meeting",
            "arguments": {"query": "test meeting today"}
        }
    }
    
    try:
        response = requests.post(f"{base_url}/tools/call", json=frontend_payload)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ SUCCESS: {json.dumps(result, indent=2)[:200]}...")
        else:
            print(f"   ❌ ERROR: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
    
    # Test 2: Direct format (what might work)
    print("\n2. Testing Direct Format...")
    direct_payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "schedule_meeting",
            "arguments": {"query": "test meeting today"}
        }
    }
    
    try:
        response = requests.post(f"{base_url}/tools/call", json=direct_payload)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ SUCCESS: {json.dumps(result, indent=2)[:200]}...")
        else:
            print(f"   ❌ ERROR: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
    
    # Test 3: Test list_staff (simpler tool)
    print("\n3. Testing list_staff (simpler tool)...")
    list_staff_payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "list_staff",
            "arguments": {}
        }
    }
    
    try:
        response = requests.post(f"{base_url}/tools/call", json=list_staff_payload)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ SUCCESS: {json.dumps(result, indent=2)[:300]}...")
        else:
            print(f"   ❌ ERROR: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
    
    # Test 4: Health check
    print("\n4. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")

if __name__ == "__main__":
    test_parameter_formats()
