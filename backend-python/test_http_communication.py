"""Test the HTTP endpoints that the frontend uses."""

import json
import requests

def test_frontend_backend_communication():
    """Test the same workflow through HTTP endpoints like the frontend does."""
    print("🌐 Testing Frontend-Backend HTTP Communication")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: List tools
    print("\n2. Testing tools/list endpoint...")
    try:
        response = requests.get(f"{base_url}/tools/list")
        print(f"✅ Tools list status: {response.status_code}")
        data = response.json()
        if 'result' in data and 'tools' in data['result']:
            tools = data['result']['tools']
            print(f"   Found {len(tools)} tools")
            
            # Check for meeting-related tools
            meeting_tools = [tool for tool in tools if 'meeting' in tool['name'].lower() or 'schedule' in tool['name'].lower()]
            print(f"   Meeting-related tools: {[t['name'] for t in meeting_tools]}")
        else:
            print(f"   Response: {json.dumps(data, indent=2)[:300]}...")
    except Exception as e:
        print(f"❌ Tools list failed: {e}")
        return False
    
    # Test 3: Call list_staff tool (like frontend does)
    print("\n3. Testing list_staff tool call...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "list_staff",
                "arguments": {}
            }
        }
        
        response = requests.post(f"{base_url}/tools/call", json=payload)
        print(f"✅ list_staff status: {response.status_code}")
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)[:300]}...")
        
    except Exception as e:
        print(f"❌ list_staff call failed: {e}")
    
    # Test 4: Call schedule_meeting tool (like frontend does)
    print("\n4. Testing schedule_meeting tool call...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "schedule_meeting",
                "arguments": {
                    "query": "i need to schedule a meeting with all the staffs today to discuss about 'Tasks Improvements'..by arranging the online meeting and can you send all the staffs confirmation emails.."
                }
            }
        }
        
        response = requests.post(f"{base_url}/tools/call", json=payload)
        print(f"✅ schedule_meeting status: {response.status_code}")
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)[:500]}...")
        
    except Exception as e:
        print(f"❌ schedule_meeting call failed: {e}")
    
    # Test 5: Check if server is using correct format
    print("\n5. Testing parameter format issues...")
    try:
        # Test with different parameter formats that might cause "unexpected keyword argument"
        test_formats = [
            {"query": "test meeting"},
            {"name": "test", "arguments": {"query": "test meeting"}},
            {"args": {"query": "test meeting"}},
        ]
        
        for i, params in enumerate(test_formats):
            payload = {
                "jsonrpc": "2.0",
                "id": f"test_{i}",
                "method": "tools/call",
                "params": {
                    "name": "schedule_meeting",
                    "arguments": params
                }
            }
            
            response = requests.post(f"{base_url}/tools/call", json=payload)
            print(f"   Format {i}: Status {response.status_code}")
            if response.status_code != 200:
                print(f"     Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Parameter format test failed: {e}")

if __name__ == "__main__":
    test_frontend_backend_communication()
