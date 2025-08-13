#!/usr/bin/env python3
"""Test script to diagnose frontend-backend communication issues"""

import json
import requests
import sys

# Test the actual HTTP endpoint that frontend uses
SERVER_URL = "http://localhost:8000"

def test_create_department():
    """Test creating a department via HTTP API"""
    print("🧪 Testing create_department via HTTP API...")
    
    # This is the exact request format the frontend sends
    request_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",  # This doesn't matter for the /tools/call endpoint
        "params": {
            "name": "create_department",
            "arguments": {
                "name": "Test Department via HTTP",
                "description": "Test department created via HTTP API"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{SERVER_URL}/tools/call",
            headers={"Content-Type": "application/json"},
            json=request_data,
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Raw Response: {json.dumps(result, indent=2)}")
            
            # Check the response format
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"]
                if isinstance(content, list) and len(content) > 0:
                    text_content = content[0].get("text", "")
                    print(f"📝 Text Content: {text_content}")
                    
                    # Try to parse the text content as JSON
                    try:
                        parsed_result = json.loads(text_content)
                        print(f"🎯 Parsed Result: {json.dumps(parsed_result, indent=2)}")
                        
                        if parsed_result.get("success"):
                            print("✅ Department creation successful!")
                            return True
                        else:
                            print(f"❌ Department creation failed: {parsed_result.get('message')}")
                            return False
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse text content as JSON: {e}")
                        print(f"Raw text: {text_content}")
                        return False
                else:
                    print("❌ No content in response")
                    return False
            else:
                print("❌ Unexpected response format")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_list_departments():
    """Test listing departments via HTTP API"""
    print("\n🧪 Testing list_departments via HTTP API...")
    
    request_data = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "list_departments",
            "arguments": {}
        }
    }
    
    try:
        response = requests.post(
            f"{SERVER_URL}/tools/call",
            headers={"Content-Type": "application/json"},
            json=request_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"📝 Raw Response: {json.dumps(result, indent=2)}")
            
            # Extract and parse the actual result
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"]
                if isinstance(content, list) and len(content) > 0:
                    text_content = content[0].get("text", "")
                    try:
                        parsed_result = json.loads(text_content)
                        print(f"🎯 Departments: {json.dumps(parsed_result, indent=2)}")
                        return True
                    except json.JSONDecodeError:
                        print(f"❌ Failed to parse: {text_content}")
                        return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    print("🔍 Testing Frontend-Backend Communication")
    print("=" * 50)
    
    # Test health endpoint first
    try:
        health_response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print(f"❌ Server health check failed: {health_response.status_code}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot reach server: {e}")
        sys.exit(1)
    
    # Test the endpoints
    success_count = 0
    total_tests = 2
    
    if test_create_department():
        success_count += 1
    
    if test_list_departments():
        success_count += 1
    
    print(f"\n📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("✅ All tests passed! Frontend-backend communication should work.")
    else:
        print("❌ Some tests failed. There may be communication issues.")

if __name__ == "__main__":
    main()
