#!/usr/bin/env python3
"""Example showing proper patient identifier usage."""

from patient_identifier_utils import resolve_patient_identifier, get_patient_uuid_by_number, get_patient_info_by_identifier

def example_correct_usage():
    """Examples of correct patient identifier usage."""
    
    print("🏥 CORRECT PATIENT IDENTIFIER USAGE EXAMPLES")
    print("=" * 60)
    
    # Example 1: User provides patient number, system needs UUID
    print("\n📋 Example 1: Converting Patient Number to UUID for Database Operations")
    user_input = "P1022"  # User entered this
    
    # Get UUID for database operations
    patient_uuid = get_patient_uuid_by_number(user_input)
    if patient_uuid:
        print(f"✅ User input: {user_input}")
        print(f"✅ Database UUID: {patient_uuid}")
        print(f"   → Use this UUID for database queries, foreign keys, etc.")
    
    # Example 2: Flexible search that accepts both formats
    print("\n🔍 Example 2: Flexible Patient Lookup")
    
    test_identifiers = [
        "P1022",  # Patient number
        "efbd2021-3c7d-4b6e-9198-cd20566070d7",  # UUID
        "James Anderson"  # This won't work with current function, but shows the concept
    ]
    
    for identifier in test_identifiers[:2]:  # Test first two
        patient_info = get_patient_info_by_identifier(identifier)
        if patient_info:
            print(f"✅ Input: {identifier}")
            print(f"   Patient: {patient_info['name']} ({patient_info['patient_number']})")
            print(f"   UUID: {patient_info['id']}")
    
    # Example 3: API Endpoint Pattern
    print("\n🔗 Example 3: API Endpoint Usage Pattern")
    
    def get_patient_medical_records(patient_identifier):
        """Example function showing proper identifier handling."""
        # Always resolve to UUID first
        patient_uuid, patient_data = resolve_patient_identifier(patient_identifier)
        
        if not patient_uuid:
            return {"error": f"Patient not found: {patient_identifier}"}
        
        # Now use UUID for database operations
        print(f"   Looking up medical records for UUID: {patient_uuid}")
        print(f"   Patient: {patient_data['name']} ({patient_data['patient_number']})")
        
        return {"success": True, "patient": patient_data}
    
    # Test with patient number
    result1 = get_patient_medical_records("P1022")
    print(f"✅ API call with patient number: {result1['success']}")
    
    # Test with UUID
    result2 = get_patient_medical_records("efbd2021-3c7d-4b6e-9198-cd20566070d7")
    print(f"✅ API call with UUID: {result2['success']}")

def example_common_mistakes():
    """Examples of common mistakes to avoid."""
    
    print("\n\n❌ COMMON MISTAKES TO AVOID")
    print("=" * 40)
    
    print("\n❌ Mistake 1: Using patient number where UUID expected")
    print("   BAD:  patient_uuid = 'P1022'")
    print("   GOOD: patient_uuid = get_patient_uuid_by_number('P1022')")
    
    print("\n❌ Mistake 2: Not validating identifier format")
    print("   BAD:  db.query(Patient).filter(Patient.id == user_input)")
    print("   GOOD: patient_uuid, _ = resolve_patient_identifier(user_input)")
    print("         db.query(Patient).filter(Patient.id == patient_uuid)")
    
    print("\n❌ Mistake 3: Hardcoding UUID strings")
    print("   BAD:  fixed_uuid = 'efbd2021-3c7d-4b6e-9198-cd20566070d7'")
    print("   GOOD: patient_uuid = get_patient_uuid_by_number('P1022')")

if __name__ == "__main__":
    example_correct_usage()
    example_common_mistakes()
    
    print("\n\n🎯 SUMMARY:")
    print("- ✅ Patient P1022 (James Anderson) exists in the database")
    print("- ✅ UUID: efbd2021-3c7d-4b6e-9198-cd20566070d7") 
    print("- ✅ Always convert patient numbers to UUIDs for database operations")
    print("- ✅ Use the utility functions for proper identifier handling")
    print("\n💡 TIP: If you're getting UUID format errors, check where")
    print("   you're using patient numbers instead of UUIDs!")
