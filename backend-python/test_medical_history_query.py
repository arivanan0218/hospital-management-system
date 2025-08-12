#!/usr/bin/env python3
"""Test medical history query through chatbot interface."""

import requests
import json

def test_medical_history_query():
    """Test the medical history query that should be routed properly."""
    
    url = "http://localhost:8000/tools/call"
    
    # Test 1: Direct medical history query
    print("🔍 Test 1: Direct medical history query")
    payload1 = {
        "params": {
            "name": "get_patient_medical_history",
            "arguments": {
                "patient_id": "2c706b85-a646-4c11-aba4-90050afe1812"  # Mohamed Nazif's ID
            }
        }
    }
    
    response1 = requests.post(url, json=payload1)
    if response1.status_code == 200:
        result1 = response1.json()
        content1 = result1['result']['content'][0]['text']
        data1 = json.loads(content1)
        print(f"✅ Direct query successful!")
        print(f"📋 Total documents: {data1['result']['total_documents']}")
        print(f"💊 Medications: {len(data1['result']['medical_history']['medications'])}")
        print(f"🏥 Conditions: {len(data1['result']['medical_history']['conditions'])}")
        print(f"📋 Instructions: {len(data1['result']['medical_history']['instructions'])}")
    else:
        print(f"❌ Direct query failed: {response1.status_code}")
    
    print("\n" + "="*50)
    
    # Test 2: Route request through orchestrator (simulating chatbot query)
    print("🔍 Test 2: Route request through orchestrator")
    payload2 = {
        "params": {
            "name": "route_request",
            "arguments": {
                "query": "get medical history for patient Mohamed Nazif with patient number P532865",
                "patient_number": "P532865"
            }
        }
    }
    
    response2 = requests.post(url, json=payload2)
    if response2.status_code == 200:
        result2 = response2.json()
        content2 = result2['result']['content'][0]['text']
        try:
            data2 = json.loads(content2)
            print(f"✅ Orchestrator routing successful!")
            print(f"📄 Response: {json.dumps(data2, indent=2)[:500]}...")
        except json.JSONDecodeError:
            print(f"📄 Raw response: {content2[:500]}...")
    else:
        print(f"❌ Orchestrator query failed: {response2.status_code}")
    
    print("\n" + "="*50)
    
    # Test 3: Test the new patient medical history tool
    print("🔍 Test 3: Patient agent medical history tool")
    payload3 = {
        "params": {
            "name": "get_patient_medical_details",
            "arguments": {
                "patient_number": "P532865"
            }
        }
    }
    
    response3 = requests.post(url, json=payload3)
    if response3.status_code == 200:
        result3 = response3.json()
        content3 = result3['result']['content'][0]['text']
        try:
            data3 = json.loads(content3)
            print(f"✅ Patient medical details successful!")
            print(f"📄 Response: {json.dumps(data3, indent=2)}")
        except json.JSONDecodeError:
            print(f"📄 Raw response: {content3}")
    else:
        print(f"❌ Patient medical details failed: {response3.status_code}")

if __name__ == "__main__":
    test_medical_history_query()
