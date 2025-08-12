#!/usr/bin/env python3
"""Check extracted medical data details."""

import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, MedicalDocument, ExtractedMedicalData

def check_extracted_data():
    """Check what was extracted from uploaded documents."""
    session = SessionLocal()
    try:
        # Get the document for patient P532865 (Mohamed Nazif)
        patient_id = uuid.UUID('2c706b85-a646-4c11-aba4-90050afe1812')
        
        doc = session.query(MedicalDocument).filter(
            MedicalDocument.patient_id == patient_id
        ).first()
        
        if doc:
            print(f"📄 Document: {doc.file_name}")
            print(f"📊 Status: {doc.processing_status}")
            print(f"📝 File Path: {doc.file_path}")
            print(f"📈 Confidence: {doc.confidence_score}")
            
            if doc.extracted_text:
                print(f"\n📖 Extracted Text (first 500 chars):")
                print(f"'{doc.extracted_text[:500]}...'")
            else:
                print("\n❌ No extracted text found")
            
            # Get extracted medical data
            med_data = session.query(ExtractedMedicalData).filter(
                ExtractedMedicalData.document_id == doc.id
            ).all()
            
            print(f"\n💊 Extracted Medical Data ({len(med_data)} entries):")
            for i, data in enumerate(med_data, 1):
                print(f"  {i}. Type: {data.data_type}")
                print(f"     Name: {data.entity_name}")
                print(f"     Value: {data.entity_value}")
                print(f"     Confidence: {data.extraction_confidence}")
                print(f"     Method: {data.extraction_method}")
                print(f"     Doctor: {data.doctor_name}")
                print(f"     Date: {data.date_prescribed}")
                print()
        else:
            print("❌ No document found")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_extracted_data()
