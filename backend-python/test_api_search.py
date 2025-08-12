#!/usr/bin/env python3
"""Test script to verify patient search API."""

import requests
import json

def test_patient_search(patient_number):
    """Test the patient search API endpoint."""
    url = "http://localhost:8000/tools/call"
    
    payload = {
        "params": {
            "name": "search_patients",
            "arguments": {
                "patient_number": patient_number
            }
        }
    }
    
    try:
        print(f"🔍 Testing patient search for: {patient_number}")
        print(f"📡 Sending request to: {url}")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"🔧 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response: {json.dumps(result, indent=2)}")
            
            # Try to parse the actual data
            if 'result' in result and 'content' in result['result']:
                content = result['result']['content']
                if content and len(content) > 0:
                    text_content = content[0].get('text', '')
                    if text_content:
                        try:
                            data = json.loads(text_content)
                            print(f"📋 Parsed Data: {json.dumps(data, indent=2)}")
                            
                            if 'data' in data and data['data']:
                                patient = data['data'][0]
                                print(f"🏥 Found Patient: {patient.get('first_name')} {patient.get('last_name')} (ID: {patient.get('id')})")
                                return True
                            else:
                                print(f"❌ No patient data found")
                                return False
                        except json.JSONDecodeError as e:
                            print(f"❌ JSON Parse Error: {e}")
                            print(f"📄 Raw Text: {text_content}")
                            return False
        else:
            print(f"❌ HTTP Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

if __name__ == "__main__":
    # Test the specific patient number
    test_patient_search("P532865")
    
    # Also test a few other patient numbers to see the pattern
    print("\n" + "="*50)
    test_patient_search("P574561")  # Alice Johnson from our test
