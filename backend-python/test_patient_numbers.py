"""Test script to create a sample patient and get their patient number"""

import requests
import json

# Backend server URL
BASE_URL = "http://localhost:8000"

def create_test_patient():
    """Create a test patient and return the patient number"""
    
    print("🏥 Creating a test patient...")
    
    try:
        patient_payload = {
            "params": {
                "name": "create_patient",
                "arguments": {
                    "first_name": "Alice",
                    "last_name": "Johnson",
                    "date_of_birth": "1985-03-20",
                    "gender": "female",
                    "phone": "+1987654321",
                    "email": "alice.johnson@example.com"
                }
            }
        }
        
        patient_response = requests.post(f"{BASE_URL}/tools/call", json=patient_payload)
        result = patient_response.json()
        
        # Parse the MCP response format
        if result.get('result') and result['result'].get('content'):
            content_text = result['result']['content'][0]['text']
            import ast
            parsed_content = ast.literal_eval(content_text)
            if parsed_content.get('success') and parsed_content.get('result', {}).get('data'):
                patient_data = parsed_content['result']['data']
                print(f"✅ Patient created successfully!")
                print(f"📋 Patient Details:")
                print(f"   • Name: {patient_data['first_name']} {patient_data['last_name']}")
                print(f"   • Patient Number: {patient_data['patient_number']} 👈 Use this in the frontend!")
                print(f"   • Patient ID (UUID): {patient_data['id']}")
                print(f"   • Email: {patient_data['email']}")
                print(f"   • Phone: {patient_data['phone']}")
                
                return patient_data['patient_number']
            else:
                print(f"⚠️ Patient creation failed: {parsed_content}")
        else:
            print(f"❌ Failed to create patient: {result}")
        
    except Exception as e:
        print(f"❌ Error creating patient: {e}")
        import traceback
        traceback.print_exc()
    
    return None

def search_patient_by_number(patient_number):
    """Test searching for a patient by patient number"""
    
    print(f"\n🔍 Searching for patient with number: {patient_number}")
    
    try:
        search_payload = {
            "params": {
                "name": "search_patients",
                "arguments": {
                    "patient_number": patient_number
                }
            }
        }
        
        search_response = requests.post(f"{BASE_URL}/tools/call", json=search_payload)
        result = search_response.json()
        
        # Parse the MCP response format
        if result.get('result') and result['result'].get('content'):
            content_text = result['result']['content'][0]['text']
            import ast
            parsed_content = ast.literal_eval(content_text)
            if parsed_content.get('success') and parsed_content.get('result', {}).get('data'):
                patients = parsed_content['result']['data']
                if patients:
                    patient = patients[0]  # Get first match
                    print(f"✅ Patient found!")
                    print(f"📋 Search Result:")
                    print(f"   • Name: {patient['first_name']} {patient['last_name']}")
                    print(f"   • Patient Number: {patient['patient_number']}")
                    print(f"   • Patient ID (UUID): {patient['id']}")
                    print(f"   • Email: {patient['email']}")
                    print(f"   • Phone: {patient['phone']}")
                    return patient
                else:
                    print(f"❌ No patients found with number: {patient_number}")
            else:
                print(f"⚠️ Search failed: {parsed_content}")
        else:
            print(f"❌ Failed to search: {result}")
        
    except Exception as e:
        print(f"❌ Error searching patient: {e}")
        import traceback
        traceback.print_exc()
    
    return None

if __name__ == "__main__":
    print("🧪 Testing Patient Number System")
    print("=" * 50)
    
    # Create a test patient
    patient_number = create_test_patient()
    
    if patient_number:
        # Test searching for the patient
        found_patient = search_patient_by_number(patient_number)
        
        if found_patient:
            print(f"\n🎉 SUCCESS! You can now use patient number '{patient_number}' in the frontend!")
            print(f"📋 Steps to test in the frontend:")
            print(f"   1. Open http://localhost:5173/")
            print(f"   2. Go to 'Upload Documents' tab")
            print(f"   3. Enter patient number: {patient_number}")
            print(f"   4. Click 'Verify Patient'")
            print(f"   5. Upload medical documents!")
        else:
            print(f"\n❌ Search test failed for patient number: {patient_number}")
    else:
        print(f"\n❌ Failed to create test patient")
