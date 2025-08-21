#!/usr/bin/env python3
"""Quick test to inspect actual tool responses"""

import requests
import json

BASE_URL = "http://localhost:8000"
TOOLS_ENDPOINT = f"{BASE_URL}/tools/call"

def call_mcp_tool(tool_name, arguments=None):
    if arguments is None:
        arguments = {}
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    try:
        response = requests.post(TOOLS_ENDPOINT, json=payload)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

# Test a few tools to see actual response format
tools_to_test = [
    ("list_supplies", {}),
    ("get_low_stock_supplies", {}),
    ("list_inventory_transactions", {"limit": 5})
]

for tool_name, args in tools_to_test:
    print(f"\n{'='*60}")
    print(f"🔍 TESTING: {tool_name}")
    print(f"Arguments: {args}")
    
    result = call_mcp_tool(tool_name, args)
    print("Response:")
    print(json.dumps(result, indent=2, default=str))
