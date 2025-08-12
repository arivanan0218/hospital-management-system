#!/usr/bin/env python3
"""Test patient medical history summary tool."""

import requests
import json

def test_patient_summary():
    """Test the patient medical history summary tool."""
    
    url = "http://localhost:8000/tools/call"
    
    payload = {
        "params": {
            "name": "get_patient_medical_history_summary",
            "arguments": {
                "patient_number": "P532865"
            }
        }
    }
    
    print("🔍 Testing patient medical history summary...")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        content = result['result']['content'][0]['text']
        try:
            data = json.loads(content)
            print(f"✅ Patient summary successful!")
            print(f"📄 Response: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError:
            print(f"📄 Raw response: {content}")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"📄 Response: {response.text}")

if __name__ == "__main__":
    test_patient_summary()
