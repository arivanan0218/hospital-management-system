#!/usr/bin/env python3
"""Test enhanced medical entity extraction."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.medical_document_agent import MedicalDocumentAgent

def test_enhanced_extraction():
    """Test the enhanced medical entity extraction."""
    
    # Sample medical text from Mohamed Nazif's document
    sample_text = """Patient Medical Script
Patient Name: Mohamed Nazif
Date of Birth: 15-Sep-2001
Gender: Male
Date: 12-Aug-2025

Diagnosis:
Patient presents with mild seasonal allergies, likely triggered by pollen exposure. No signs of severe respiratory distress.

Prescription:
1. Loratadine 10mg - 1 tablet daily in the morning.
2. Saline nasal spray - 2 sprays per nostril twice daily.
3. Avoid outdoor activities during high pollen hours.

Follow-up:
Return for review in 2 weeks or sooner if symptoms worsen."""

    # Create agent instance
    agent = MedicalDocumentAgent()
    
    print("🔍 Testing Enhanced Medical Entity Extraction")
    print("=" * 50)
    print(f"📄 Sample Text:\n{sample_text}")
    print("\n" + "=" * 50)
    
    # Test the extraction
    entities = agent._extract_medical_entities(sample_text)
    
    print(f"🎯 Extracted {len(entities)} entities:")
    print("-" * 30)
    
    # Group by entity type
    by_type = {}
    for entity in entities:
        entity_type = entity.get('entity_group', 'unknown')
        if entity_type not in by_type:
            by_type[entity_type] = []
        by_type[entity_type].append(entity)
    
    for entity_type, type_entities in by_type.items():
        print(f"\n📋 {entity_type.upper()} ({len(type_entities)} items):")
        for i, entity in enumerate(type_entities, 1):
            print(f"  {i}. {entity.get('word', '')}")
            if 'dosage' in entity:
                print(f"     Dosage: {entity['dosage']}")
            print(f"     Confidence: {entity.get('score', 0):.2f}")
    
    print("\n" + "=" * 50)
    print(f"✅ Extraction test completed!")
    
    return entities

if __name__ == "__main__":
    test_enhanced_extraction()
