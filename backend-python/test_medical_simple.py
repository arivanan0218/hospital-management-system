"""Simple test script for medical document functionality"""

import requests
import json
import base64

# Backend server URL
BASE_URL = "http://localhost:8000"

def test_medical_document_tools():
    """Test the medical document tools"""
    
    print("🧪 Testing Medical Document Tools")
    print("=" * 50)
    
    # Test 1: List available tools
    print("\n1. Testing tools list...")
    try:
        response = requests.get(f"{BASE_URL}/tools/list")
        response_data = response.json()
        
        # Handle JSON-RPC response format
        if 'result' in response_data and 'tools' in response_data['result']:
            tools = response_data['result']['tools']
        elif isinstance(response_data, list):
            tools = response_data
        else:
            print(f"⚠️ Unexpected response format: {response_data}")
            return
        
        medical_tools = [tool for tool in tools if 'medical' in tool.get('name', '').lower()]
        print(f"✅ Found {len(medical_tools)} medical document tools")
        print(f"📋 Total available tools: {len(tools)}")
        
        if medical_tools:
            print("🔧 Medical tools found:")
            for tool in medical_tools:
                print(f"   - {tool.get('name', 'Unknown')}")
    except Exception as e:
        print(f"❌ Error listing tools: {e}")
        return
    
    # Test 2: Create a sample patient first
    print("\n2. Creating a test patient...")
    try:
        patient_payload = {
            "params": {
                "name": "create_patient",
                "arguments": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "date_of_birth": "1990-05-15",
                    "gender": "male",
                    "phone": "+1234567890",
                    "email": "john.doe@example.com"
                }
            }
        }
        
        patient_response = requests.post(f"{BASE_URL}/tools/call", json=patient_payload)
        result = patient_response.json()
        print(f"🔍 Patient creation response: {result}")
        
        # Extract patient ID from MCP response format
        patient_id = None
        if result.get('result') and result['result'].get('content'):
            # Parse the nested JSON response
            content_text = result['result']['content'][0]['text']
            import ast
            parsed_content = ast.literal_eval(content_text)
            if parsed_content.get('success') and parsed_content.get('result', {}).get('data'):
                patient_id = parsed_content['result']['data']['id']
        
        if patient_id:
            print(f"✅ Created test patient with ID: {patient_id}")
        else:
            # Use a sample UUID for testing
            patient_id = "123e4567-e89b-12d3-a456-426614174000"
            print(f"📝 Using sample patient ID for testing: {patient_id}")
        
    except Exception as e:
        print(f"❌ Error creating patient: {e}")
        patient_id = "123e4567-e89b-12d3-a456-426614174000"
        print(f"📝 Using sample patient ID for testing: {patient_id}")
    
    # Test 3: Test medical document upload
    print("\n3. Testing medical document upload...")
    try:
        # Create sample medical text
        sample_text = """
        PRESCRIPTION
        
        Patient: John Doe
        Date: August 11, 2025
        
        Diagnosis: Hypertension
        
        Medications:
        1. Lisinopril 10mg - Take once daily
        2. Hydrochlorothiazide 25mg - Take once daily
        
        Instructions: Monitor blood pressure regularly
        Follow-up in 3 months
        
        Dr. Sarah Smith
        Internal Medicine
        """
        
        # Convert to base64
        sample_data = base64.b64encode(sample_text.encode()).decode()
        
        upload_payload = {
            "params": {
                "name": "upload_medical_document",
                "arguments": {
                    "patient_id": patient_id,
                    "document_type": "prescription",
                    "file_content": sample_data,
                    "file_name": "prescription_sample.txt",
                    "mime_type": "text/plain"
                }
            }
        }
        
        upload_response = requests.post(f"{BASE_URL}/tools/call", json=upload_payload)
        upload_result = upload_response.json()
        print(f"🔍 Upload response: {upload_result}")
        
        # Parse the MCP response format
        document_id = None
        if upload_result.get('result') and upload_result['result'].get('content'):
            content_text = upload_result['result']['content'][0]['text']
            import ast
            parsed_content = ast.literal_eval(content_text)
            if parsed_content.get('success') and parsed_content.get('result', {}).get('success'):
                document_id = parsed_content['result']['document_id']
                print(f"✅ Document uploaded successfully with ID: {document_id}")
            else:
                print(f"⚠️ Document upload failed: {parsed_content}")
        else:
            print(f"⚠️ Document upload failed: {upload_result}")
        
        if document_id:
            # Test 4: Process the document
            print("\n4. Testing document processing...")
            process_payload = {
                "params": {
                    "name": "process_medical_document",
                    "arguments": {
                        "document_id": document_id
                    }
                }
            }
            
            process_response = requests.post(f"{BASE_URL}/tools/call", json=process_payload)
            process_result = process_response.json()
            print(f"🔍 Processing response: {process_result}")
            
            # Parse processing response
            if process_result.get('result') and process_result['result'].get('content'):
                content_text = process_result['result']['content'][0]['text']
                import ast
                parsed_content = ast.literal_eval(content_text)
                if parsed_content.get('success') and parsed_content.get('result', {}).get('success'):
                    print("✅ Document processed successfully")
                    
                    # Test 5: Get patient medical history
                    print("\n5. Testing medical history retrieval...")
                    history_payload = {
                        "params": {
                            "name": "get_patient_medical_history",
                            "arguments": {
                                "patient_id": patient_id
                            }
                        }
                    }
                    
                    history_response = requests.post(f"{BASE_URL}/tools/call", json=history_payload)
                    history_result = history_response.json()
                    print(f"🔍 History response: {history_result}")
                    
                    # Parse history response
                    if history_result.get('result') and history_result['result'].get('content'):
                        content_text = history_result['result']['content'][0]['text']
                        import ast
                        parsed_content = ast.literal_eval(content_text)
                        if parsed_content.get('success') and parsed_content.get('result', {}).get('success'):
                            print("✅ Medical history retrieved successfully")
                            history_data = parsed_content['result']
                            print(f"📋 Found {len(history_data.get('documents', []))} documents")
                            print(f"📋 Found {len(history_data.get('extracted_data', []))} extracted records")
                            
                            print("\n🎉 ALL TESTS PASSED! Medical document system is working correctly!")
                        else:
                            print(f"⚠️ Medical history retrieval failed: {parsed_content}")
                    else:
                        print(f"⚠️ Medical history retrieval failed: {history_result}")
                else:
                    print(f"⚠️ Document processing failed: {parsed_content}")
            else:
                print(f"⚠️ Document processing failed: {process_result}")
        else:
            print("❌ Cannot proceed with processing - upload failed")
            
    except Exception as e:
        print(f"❌ Error in medical document testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_medical_document_tools()
