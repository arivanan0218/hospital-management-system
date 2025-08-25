"""
Database Verification Script for Sarah Johnson's Assignments
"""

from database.connection import get_db_session
from database.models import (
    Patient, Bed, BedAssignment, Staff, StaffAssignment, 
    Equipment, EquipmentUsage, Supply, SupplyTransaction
)
from sqlalchemy import desc
from datetime import datetime, date

def verify_assignments():
    """Verify all assignments for Sarah Johnson in database"""
    print("=" * 60)
    print("🔍 DATABASE VERIFICATION FOR ASSIGNMENTS")
    print("=" * 60)
    
    # Create database session
    db = next(get_db_session())
    
    try:
        # Find Sarah Johnson
        patient = db.query(Patient).filter(
            Patient.first_name == "Sarah",
            Patient.last_name == "Johnson"
        ).first()
        
        if not patient:
            print("❌ Patient Sarah Johnson not found in database")
            return
            
        print(f"✅ Patient found: {patient.first_name} {patient.last_name}")
        print(f"   Patient ID: {patient.id}")
        print(f"   Patient Number: {patient.patient_number}")
        print()
        
        # Check Bed Assignment
        print("🛏️  CHECKING BED ASSIGNMENTS...")
        bed_assignments = db.query(BedAssignment).filter(
            BedAssignment.patient_id == patient.id
        ).all()
        
        if bed_assignments:
            for assignment in bed_assignments:
                bed = db.query(Bed).filter(Bed.id == assignment.bed_id).first()
                print(f"   ✅ Bed Assignment Found:")
                print(f"      Bed: {bed.bed_number if bed else 'Unknown'}")
                print(f"      Assignment Date: {assignment.assignment_date}")
                print(f"      Status: {assignment.status}")
        else:
            print("   ❌ No bed assignments found")
        print()
        
        # Check Staff Assignments
        print("👨‍⚕️ CHECKING STAFF ASSIGNMENTS...")
        staff_assignments = db.query(StaffAssignment).filter(
            StaffAssignment.patient_id == patient.id
        ).all()
        
        if staff_assignments:
            for assignment in staff_assignments:
                staff = db.query(Staff).filter(Staff.id == assignment.staff_id).first()
                print(f"   ✅ Staff Assignment Found:")
                print(f"      Staff: {staff.first_name if staff else 'Unknown'} {staff.last_name if staff else ''}")
                print(f"      Employee ID: {staff.employee_id if staff else 'Unknown'}")
                print(f"      Assignment Date: {assignment.assignment_date}")
                print(f"      Role: {assignment.role}")
        else:
            print("   ❌ No staff assignments found")
        print()
        
        # Check Equipment Usage
        print("🩺 CHECKING EQUIPMENT USAGE...")
        equipment_usage = db.query(EquipmentUsage).filter(
            EquipmentUsage.patient_id == patient.id
        ).all()
        
        if equipment_usage:
            for usage in equipment_usage:
                equipment = db.query(Equipment).filter(Equipment.id == usage.equipment_id).first()
                staff = db.query(Staff).filter(Staff.id == usage.assigned_staff_id).first()
                print(f"   ✅ Equipment Usage Found:")
                print(f"      Equipment: {equipment.name if equipment else 'Unknown'}")
                print(f"      Assigned Staff: {staff.first_name if staff else 'Unknown'}")
                print(f"      Start Time: {usage.start_time}")
                print(f"      Status: {usage.status}")
        else:
            print("   ❌ No equipment usage found")
        print()
        
        # Check Supply Transactions (look for recent transactions)
        print("💊 CHECKING SUPPLY TRANSACTIONS...")
        recent_transactions = db.query(SupplyTransaction).filter(
            SupplyTransaction.notes.like("%Sarah Johnson%")
        ).order_by(desc(SupplyTransaction.transaction_date)).limit(5).all()
        
        if recent_transactions:
            for transaction in recent_transactions:
                supply = db.query(Supply).filter(Supply.id == transaction.supply_id).first()
                print(f"   ✅ Supply Transaction Found:")
                print(f"      Supply: {supply.name if supply else 'Unknown'}")
                print(f"      Quantity Change: {transaction.quantity_change}")
                print(f"      Transaction Type: {transaction.transaction_type}")
                print(f"      Date: {transaction.transaction_date}")
                print(f"      Notes: {transaction.notes}")
        else:
            print("   ❌ No supply transactions found for Sarah Johnson")
        print()
        
        # Summary
        print("=" * 60)
        print("📊 ASSIGNMENT SUMMARY")
        print("=" * 60)
        
        bed_count = len(bed_assignments)
        staff_count = len(staff_assignments)
        equipment_count = len(equipment_usage)
        supply_count = len(recent_transactions)
        
        print(f"   Bed Assignments: {bed_count}")
        print(f"   Staff Assignments: {staff_count}")
        print(f"   Equipment Usage: {equipment_count}")
        print(f"   Supply Transactions: {supply_count}")
        print()
        
        total_assignments = bed_count + staff_count + equipment_count + supply_count
        if total_assignments > 0:
            print("✅ ASSIGNMENTS VERIFIED IN DATABASE!")
            print(f"   Total records found: {total_assignments}")
        else:
            print("❌ NO ASSIGNMENTS FOUND IN DATABASE")
            
    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_assignments()
