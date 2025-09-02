#!/usr/bin/env python3
"""
Find David Wilson's bed assignment
"""

import sys
sys.path.append('./backend-python')

from database import SessionLocal, Bed, Patient

def find_david_wilson_bed():
    """Find which bed David Wilson is assigned to"""
    
    print("🔍 Finding David Wilson's Bed Assignment...")
    
    db = SessionLocal()
    
    try:
        # Find David Wilson
        david = db.query(Patient).filter(
            Patient.first_name == "David",
            Patient.last_name == "Wilson"
        ).first()
        
        if not david:
            print("❌ David Wilson not found!")
            return
        
        print(f"✅ Found David Wilson: {david.id}")
        
        # Find his bed assignment
        bed = db.query(Bed).filter(Bed.patient_id == david.id).first()
        
        if bed:
            print(f"🛏️ David Wilson is assigned to:")
            print(f"  Bed Number: {bed.bed_number}")
            print(f"  Bed ID: {bed.id}")
            print(f"  Room: {bed.room.room_number if bed.room else 'Unknown'}")
            print(f"  Department: {bed.room.department.name if bed.room and bed.room.department else 'Unknown'}")
            
            # Also check if there are multiple bed assignments
            all_beds = db.query(Bed).filter(Bed.patient_id == david.id).all()
            if len(all_beds) > 1:
                print(f"\n⚠️ Multiple bed assignments found ({len(all_beds)}):")
                for b in all_beds:
                    print(f"  - Bed {b.bed_number} (ID: {b.id})")
        else:
            print("❌ David Wilson is not assigned to any bed!")
            
            # Check if he has any bed assignments
            beds = db.query(Bed).filter(Bed.patient_id == david.id).all()
            print(f"📊 Total bed assignments for David: {len(beds)}")
            
            # Check if there are multiple assignments
            if len(beds) > 1:
                print("⚠️ Multiple bed assignments found:")
                for b in beds:
                    print(f"  - Bed {b.bed_number} (ID: {b.id})")
        
    except Exception as e:
        print(f"❌ Error finding David Wilson's bed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    find_david_wilson_bed()
