"""Test script for medical document functionality"""

import requests
import json
import base64

# Backend server URL
BASE_URL = "http://localhost:8000"

def test_medical_document_tools():
    """Test the medical document MCP tools"""
    
    print("🧪 Testing Medical Document Tools")
    print("=" * 50)
    
    # Test 1: List available tools
    print("\n1. Testing tools list...")
    try:
        response = requests.get(f"{BASE_URL}/tools/list")
        response_data = response.json()
        
        # Handle the response format
        if isinstance(response_data, list):
            tools = response_data
        elif isinstance(response_data, dict) and 'tools' in response_data:
            tools = response_data['tools']
        else:
            tools = []
            print(f"⚠️ Unexpected response format: {response_data}")
        
        medical_tools = [tool for tool in tools if isinstance(tool, dict) and 'medical' in tool.get('name', '').lower()]
        print(f"✅ Found {len(medical_tools)} medical document tools")
        print(f"📋 Total available tools: {len(tools)}")
        
        # Print medical tool names for debugging
        if medical_tools:
            print("🔧 Medical tools found:")
            for tool in medical_tools:
                print(f"   - {tool.get('name', 'Unknown')}")
    except Exception as e:
        print(f"❌ Error listing tools: {e}")
    
    # Test 2: Create a sample patient first
    print("\n2. Creating a test patient...")
    try:
        patient_response = requests.post(f"{BASE_URL}/mcp", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
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
        })
        
        result = patient_response.json()
        if result.get('result') and result['result'].get('content'):
            patient_data = json.loads(result['result']['content'][0]['text'])
            if patient_data.get('success'):
                patient_id = patient_data['data']['id']
                print(f"✅ Created test patient with ID: {patient_id}")
            else:
                print(f"⚠️ Patient creation response: {patient_data.get('message')}")
                # Use a sample UUID for testing
                patient_id = "123e4567-e89b-12d3-a456-426614174000"
                print(f"📝 Using sample patient ID: {patient_id}")
        else:
            print(f"❌ Error creating patient: {result}")
            return
            
    except Exception as e:
        print(f"❌ Error creating patient: {e}")
        return
    
    # Test 3: Create sample medical document text
    print("\n3. Testing medical document upload...")
    try:
        # Create sample medical text
        sample_text = """
        PRESCRIPTION
        
        Patient: John Doe
        Date: August 11, 2025
        
        Medications:
        - Amoxicillin 500mg - Take 3 times daily for 7 days
        - Ibuprofen 200mg - Take as needed for pain
        
        Diagnosis: Upper respiratory infection
        
        Dr. Smith
        Internal Medicine
        """
        
        # Convert to base64
        text_bytes = sample_text.encode('utf-8')
        base64_content = base64.b64encode(text_bytes).decode('utf-8')
        
        upload_response = requests.post(f"{BASE_URL}/mcp", json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "upload_medical_document",
                "arguments": {
                    "patient_id": patient_id,
                    "file_content": base64_content,
                    "file_name": "prescription_sample.txt",
                    "document_type": "prescription",
                    "mime_type": "text/plain"
                }
            }
        })
        
        upload_result = upload_response.json()
        if upload_result.get('result') and upload_result['result'].get('content'):
            upload_data = json.loads(upload_result['result']['content'][0]['text'])
            if upload_data.get('success'):
                document_id = upload_data['document_id']
                print(f"✅ Uploaded document with ID: {document_id}")
                
                # Test 4: Process the document
                print("\n4. Testing document processing...")
                process_response = requests.post(f"{BASE_URL}/mcp", json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "process_medical_document",
                        "arguments": {
                            "document_id": document_id
                        }
                    }
                })
                
                process_result = process_response.json()
                if process_result.get('result') and process_result['result'].get('content'):
                    process_data = json.loads(process_result['result']['content'][0]['text'])
                    if process_data.get('success'):
                        print(f"✅ Document processed successfully!")
                        print(f"   - Extracted {process_data.get('entities_count', 0)} entities")
                        print(f"   - Confidence score: {process_data.get('confidence_score', 0):.2f}")
                    else:
                        print(f"❌ Error processing document: {process_data.get('message')}")
                else:
                    print(f"❌ Error processing document: {process_result}")
                
                # Test 5: Get patient medical history
                print("\n5. Testing medical history retrieval...")
                history_response = requests.post(f"{BASE_URL}/mcp", json={
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "get_patient_medical_history",
                        "arguments": {
                            "patient_id": patient_id
                        }
                    }
                })
                
                history_result = history_response.json()
                if history_result.get('result') and history_result['result'].get('content'):
                    history_data = json.loads(history_result['result']['content'][0]['text'])
                    if history_data.get('success'):
                        print(f"✅ Retrieved medical history!")
                        print(f"   - Total documents: {history_data.get('total_documents', 0)}")
                        history = history_data.get('medical_history', {})
                        for category, items in history.items():
                            if isinstance(items, list) and len(items) > 0:
                                print(f"   - {category.title()}: {len(items)} items")
                    else:
                        print(f"❌ Error getting medical history: {history_data.get('message')}")
                else:
                    print(f"❌ Error getting medical history: {history_result}")
                    
            else:
                print(f"❌ Error uploading document: {upload_data.get('message')}")
        else:
            print(f"❌ Error uploading document: {upload_result}")
            
    except Exception as e:
        print(f"❌ Error testing document upload: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Medical Document Testing Complete!")

if __name__ == "__main__":
    test_medical_document_tools()
