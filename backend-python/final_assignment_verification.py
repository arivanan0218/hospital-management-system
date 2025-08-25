#!/usr/bin/env python3
"""
Database Assignment Verification Script (Final)
Checks assignments for Sarah Johnson with correct table structures
"""

from sqlalchemy import text
from database import SessionLocal

def verify_assignments():
    """Verify assignments in database for Sarah Johnson"""
    print("=" * 70)
    print("DATABASE ASSIGNMENT VERIFICATION FOR SARAH JOHNSON")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # Find Sarah Johnson
        print("FINDING PATIENT...")
        patient_query = text("""
            SELECT id, patient_number, first_name, last_name, email
            FROM patients 
            WHERE first_name = 'Sarah' AND last_name = 'Johnson'
        """)
        
        patient_result = db.execute(patient_query).fetchone()
        
        if not patient_result:
            print("Patient Sarah Johnson not found in database")
            return
            
        patient_id, patient_number, first_name, last_name, email = patient_result
        print(f"Patient found: {first_name} {last_name}")
        print(f"   Patient ID: {patient_id}")
        print(f"   Patient Number: {patient_number}")
        print(f"   Email: {email}")
        print()
        
        # Check Bed Staff Assignments  
        print("CHECKING BED STAFF ASSIGNMENTS...")
        bed_query = text("""
            SELECT bsa.id, bsa.assigned_at, bsa.status, bsa.assignment_type, b.bed_number
            FROM bed_staff_assignments bsa
            JOIN beds b ON bsa.bed_id = b.id
            WHERE bsa.patient_id = :patient_id
            ORDER BY bsa.assigned_at DESC
        """)
        
        bed_results = db.execute(bed_query, {"patient_id": patient_id}).fetchall()
        
        if bed_results:
            for bed_assignment in bed_results:
                bsa_id, assigned_at, status, assignment_type, bed_number = bed_assignment
                print(f"   Bed Staff Assignment Found:")
                print(f"      Assignment ID: {bsa_id}")
                print(f"      Bed Number: {bed_number}")
                print(f"      Assigned At: {assigned_at}")
                print(f"      Status: {status}")
                print(f"      Assignment Type: {assignment_type}")
        else:
            print("   No bed staff assignments found")
        print()
        
        # Check Staff Assignments
        print("CHECKING STAFF ASSIGNMENTS...")
        staff_query = text("""
            SELECT sa.id, sa.start_date, sa.assignment_type, sa.shift, 
                   u.first_name, u.last_name, s.employee_id
            FROM staff_assignments sa
            JOIN staff s ON sa.staff_id = s.id
            JOIN users u ON s.user_id = u.id
            WHERE sa.patient_id = :patient_id
            ORDER BY sa.start_date DESC
        """)
        
        staff_results = db.execute(staff_query, {"patient_id": patient_id}).fetchall()
        
        if staff_results:
            for staff_assignment in staff_results:
                sa_id, start_date, assignment_type, shift, staff_first, staff_last, employee_id = staff_assignment
                print(f"   Staff Assignment Found:")
                print(f"      Assignment ID: {sa_id}")
                print(f"      Staff: {staff_first} {staff_last}")
                print(f"      Employee ID: {employee_id}")
                print(f"      Assignment Type: {assignment_type}")
                print(f"      Start Date: {start_date}")
                print(f"      Shift: {shift}")
        else:
            print("   No staff assignments found")
        print()
        
        # Check Equipment Usage
        print("CHECKING EQUIPMENT USAGE...")
        equipment_query = text("""
            SELECT eu.id, eu.start_time, eu.status, eu.purpose, e.name as equipment_name, 
                   u.first_name, u.last_name, s.employee_id
            FROM equipment_usage eu
            JOIN equipment e ON eu.equipment_id = e.id
            JOIN staff s ON eu.staff_id = s.id
            JOIN users u ON s.user_id = u.id
            WHERE eu.patient_id = :patient_id
            ORDER BY eu.start_time DESC
        """)
        
        equipment_results = db.execute(equipment_query, {"patient_id": patient_id}).fetchall()
        
        if equipment_results:
            for equipment_usage in equipment_results:
                eu_id, start_time, status, purpose, equipment_name, staff_first, staff_last, employee_id = equipment_usage
                print(f"   Equipment Usage Found:")
                print(f"      Usage ID: {eu_id}")
                print(f"      Equipment: {equipment_name}")
                print(f"      Assigned Staff: {staff_first} {staff_last} ({employee_id})")
                print(f"      Start Time: {start_time}")
                print(f"      Status: {status}")
                print(f"      Purpose: {purpose}")
        else:
            print("   No equipment usage found")
        print()
        
        # Check Inventory Transactions
        print("CHECKING INVENTORY TRANSACTIONS...")
        supply_query = text("""
            SELECT it.id, it.quantity, it.transaction_type, it.transaction_date, it.notes, 
                   s.name as supply_name, u.first_name as staff_first, u.last_name as staff_last
            FROM inventory_transactions it
            JOIN supplies s ON it.supply_id = s.id
            LEFT JOIN staff st ON it.performed_by = st.id
            LEFT JOIN users u ON st.user_id = u.id
            WHERE it.notes LIKE '%Sarah Johnson%'
            ORDER BY it.transaction_date DESC
            LIMIT 10
        """)
        
        supply_results = db.execute(supply_query).fetchall()
        
        if supply_results:
            for supply_transaction in supply_results:
                it_id, quantity, transaction_type, transaction_date, notes, supply_name, staff_first, staff_last = supply_transaction
                print(f"   Supply Transaction Found:")
                print(f"      Transaction ID: {it_id}")
                print(f"      Supply: {supply_name}")
                print(f"      Quantity: {quantity}")
                print(f"      Transaction Type: {transaction_type}")
                print(f"      Date: {transaction_date}")
                print(f"      Performed By: {staff_first} {staff_last}" if staff_first else "      Performed By: Unknown")
                print(f"      Notes: {notes}")
        else:
            print("   No inventory transactions found")
        print()
        
        # Summary
        print("=" * 70)
        print("ASSIGNMENT SUMMARY")
        print("=" * 70)
        
        bed_count = len(bed_results) if bed_results else 0
        staff_count = len(staff_results) if staff_results else 0
        equipment_count = len(equipment_results) if equipment_results else 0
        supply_count = len(supply_results) if supply_results else 0
        
        print(f"   Bed Staff Assignments: {bed_count}")
        print(f"   Staff Assignments: {staff_count}")
        print(f"   Equipment Usage Records: {equipment_count}")
        print(f"   Inventory Transactions: {supply_count}")
        print()
        
        total_assignments = bed_count + staff_count + equipment_count + supply_count
        
        if total_assignments > 0:
            print("SUCCESS: ASSIGNMENTS FOUND IN DATABASE!")
            print(f"   Total assignment records: {total_assignments}")
            print()
            print("ASSIGNMENT VERIFICATION RESULTS:")
            if bed_count > 0:
                print("   Bed assignments are stored properly")
            if staff_count > 0:
                print("   Staff assignments are stored properly") 
            if equipment_count > 0:
                print("   Equipment usage is stored properly")
            if supply_count > 0:
                print("   Supply transactions are stored properly")
        else:
            print("WARNING: NO ASSIGNMENTS FOUND IN DATABASE")
            print("   The assignment commands were successful in the API,")
            print("   but no records were found in the database.")
            print("   This suggests assignments may be processed but not stored.")
            
    except Exception as e:
        print(f"Error during verification: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_assignments()
