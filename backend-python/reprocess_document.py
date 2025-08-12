#!/usr/bin/env python3
"""Reprocess existing medical documents with enhanced extraction."""

import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, MedicalDocument, ExtractedMedicalData
from agents.medical_document_agent import MedicalDocumentAgent

def reprocess_document(document_id):
    """Reprocess a document with enhanced extraction."""
    session = SessionLocal()
    agent = MedicalDocumentAgent()
    
    try:
        # Get the document
        document = session.query(MedicalDocument).filter(
            MedicalDocument.id == uuid.UUID(document_id)
        ).first()
        
        if not document:
            print(f"❌ Document {document_id} not found")
            return False
        
        print(f"📄 Reprocessing document: {document.file_name}")
        print(f"📊 Current status: {document.processing_status}")
        
        # Delete existing extracted data
        old_data = session.query(ExtractedMedicalData).filter(
            ExtractedMedicalData.document_id == document.id
        ).all()
        
        print(f"🗑️ Removing {len(old_data)} old extracted entries")
        for data in old_data:
            session.delete(data)
        session.commit()
        
        # Get the extracted text
        if not document.extracted_text:
            print("❌ No extracted text found in document")
            return False
        
        print(f"📖 Document has {len(document.extracted_text)} characters of text")
        
        # Re-extract entities with enhanced method
        medical_entities = agent._extract_medical_entities(document.extracted_text)
        print(f"🎯 Extracted {len(medical_entities)} new entities")
        
        # Store new extracted entities
        for entity in medical_entities:
            # Extract additional fields
            entity_value = entity.get('dosage', entity.get('value'))
            doctor_name = entity.get('doctor')
            
            extracted_data = ExtractedMedicalData(
                document_id=document.id,
                patient_id=document.patient_id,
                data_type=entity.get('entity_group', 'unknown').lower(),
                entity_name=entity.get('word', ''),
                entity_value=entity_value,
                doctor_name=doctor_name,
                extraction_confidence=float(entity.get('score', 0.0)),
                extraction_method='AI_PARSING_ENHANCED'
            )
            session.add(extracted_data)
        
        # Update confidence score
        if medical_entities:
            avg_confidence = sum(e.get('score', 0) for e in medical_entities) / len(medical_entities)
            document.confidence_score = float(avg_confidence)
        
        session.commit()
        print(f"✅ Reprocessing completed successfully!")
        
        # Show summary of new data
        print(f"\n📋 New Extracted Data Summary:")
        by_type = {}
        for entity in medical_entities:
            entity_type = entity.get('entity_group', 'unknown')
            if entity_type not in by_type:
                by_type[entity_type] = []
            by_type[entity_type].append(entity)
        
        for entity_type, type_entities in by_type.items():
            print(f"  {entity_type}: {len(type_entities)} items")
            for entity in type_entities[:3]:  # Show first 3
                name = entity.get('word', '')[:50]
                dosage = entity.get('dosage', '')
                print(f"    - {name}" + (f" ({dosage})" if dosage else ""))
        
        return True
        
    except Exception as e:
        print(f"❌ Error reprocessing document: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    # Reprocess Mohamed Nazif's document
    document_id = "f8ca6416-8de0-4f80-9262-53d4a3a891d0"  # From our earlier check
    reprocess_document(document_id)
