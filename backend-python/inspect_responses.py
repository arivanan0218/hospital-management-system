#!/usr/bin/env python3
"""
Script to inspect actual responses from equipment tools
"""

import requests
import json

def make_request(tool_name, params):
    """Make a request and show full response"""
    payload = {
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": params
        }
    }
    
    try:
        response = requests.post("http://localhost:8000/tools/call", json=payload, timeout=30)
        print(f"\n🔧 Testing {tool_name}")
        print(f"📤 Request: {json.dumps(payload, indent=2)}")
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# Test create_equipment_category
make_request("create_equipment_category", {
    "name": "Test Category",
    "description": "A test equipment category"
})

# Test list_equipment_categories
make_request("list_equipment_categories", {})

# Test create_equipment
make_request("create_equipment", {
    "equipment_id": "EQ-TEST-001",
    "name": "Test Equipment",
    "category_id": "cat-001",
    "model": "Test Model"
})

# Test list_equipment
make_request("list_equipment", {})
