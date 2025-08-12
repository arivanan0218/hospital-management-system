#!/usr/bin/env python3
"""Test script to check medical documents and history for a patient."""

import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, Patient, MedicalDocument, ExtractedMedicalData

def check_medical_history(patient_number):
    """Check medical documents and history for a patient."""
    session = SessionLocal()
    try:
        # First find the patient
        patient = session.query(Patient).filter(Patient.patient_number == patient_number).first()
        
        if not patient:
            print(f"❌ Patient {patient_number} not found")
            return False
            
        print(f"✅ Found patient: {patient.first_name} {patient.last_name}")
        print(f"   Patient ID: {patient.id}")
        
        # Check medical documents
        documents = session.query(MedicalDocument).filter(
            MedicalDocument.patient_id == patient.id
        ).all()
        
        print(f"\n📄 Medical Documents: {len(documents)}")
        for doc in documents:
            print(f"   - {doc.file_name} ({doc.document_type})")
            print(f"     Status: {doc.processing_status}")
            print(f"     Upload Date: {doc.upload_date}")
            print(f"     Confidence: {doc.confidence_score}")
        
        # Check extracted medical data
        medical_data = session.query(ExtractedMedicalData).filter(
            ExtractedMedicalData.patient_id == patient.id
        ).all()
        
        print(f"\n💊 Extracted Medical Data: {len(medical_data)}")
        for data in medical_data:
            print(f"   - {data.data_type}: {data.entity_name}")
            print(f"     Value: {data.entity_value}")
            print(f"     Doctor: {data.doctor_name}")
            print(f"     Date: {data.date_prescribed}")
            print(f"     Confidence: {data.extraction_confidence}")
        
        return len(documents) > 0 or len(medical_data) > 0
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        session.close()

def test_api_call(patient_id):
    """Test the API call for medical history."""
    import requests
    import json
    
    url = "http://localhost:8000/tools/call"
    payload = {
        "params": {
            "name": "get_patient_medical_history", 
            "arguments": {
                "patient_id": patient_id
            }
        }
    }
    
    try:
        print(f"\n🔍 Testing API call for patient ID: {patient_id}")
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Response: {json.dumps(result, indent=2)}")
            
            if 'result' in result and 'content' in result['result']:
                content = result['result']['content'][0]['text']
                data = json.loads(content)
                print(f"📋 Parsed Data: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"💥 API Test Error: {e}")

if __name__ == "__main__":
    patient_number = "P532865"  # Mohamed Nazif
    
    print(f"🔍 Checking medical history for patient: {patient_number}")
    has_data = check_medical_history(patient_number)
    
    if has_data:
        print("\n✅ Patient has medical data")
    else:
        print("\n❌ Patient has no medical data - this explains why history shows 'No Medical History Available'")
    
    # Also test the API call
    # Get patient ID for API test
    session = SessionLocal()
    try:
        patient = session.query(Patient).filter(Patient.patient_number == patient_number).first()
        if patient:
            test_api_call(str(patient.id))
    finally:
        session.close()
