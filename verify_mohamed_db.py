#!/usr/bin/env python3

import psycopg2
import json

def verify_mohamed_assignments_in_database():
    """Verify Mohamed Nazif's assignments directly in the database"""
    
    try:
        # Database connection
        conn = psycopg2.connect(
            host="localhost",
            database="hospital_management",
            user="postgres",
            password="1234"
        )
        cursor = conn.cursor()
        
        print("🔍 Verifying Mohamed Nazif assignments in database...")
        
        # Find Mohamed Nazif
        cursor.execute("""
            SELECT id, patient_number, first_name, last_name, phone, email, status
            FROM patients 
            WHERE first_name LIKE '%Mohamed%' AND last_name LIKE '%Nazif%'
        """)
        
        patient_result = cursor.fetchone()
        if not patient_result:
            print("❌ Mohamed Nazif not found in database")
            return False
            
        patient_id, patient_number, first_name, last_name, phone, email, status = patient_result
        print(f"✅ Found patient: {first_name} {last_name}")
        print(f"   📍 ID: {patient_id}")
        print(f"   📋 Number: {patient_number}")
        print(f"   📞 Phone: {phone}")
        print(f"   📧 Email: {email}")
        print(f"   🏥 Status: {status}")
        
        # Check bed assignment
        print(f"\n🛏️ Checking bed assignments for {first_name} {last_name}...")
        cursor.execute("""
            SELECT b.bed_number, b.status, r.room_number, b.admission_date, b.discharge_date
            FROM beds b
            LEFT JOIN rooms r ON b.room_id = r.id
            WHERE b.patient_id = %s
        """, (patient_id,))
        
        bed_assignments = cursor.fetchall()
        if bed_assignments:
            for bed_number, bed_status, room_number, admission_date, discharge_date in bed_assignments:
                print(f"   🛏️ Bed: {bed_number} in Room {room_number}")
                print(f"   📊 Status: {bed_status}")
                print(f"   📅 Admitted: {admission_date}")
                print(f"   📅 Discharge: {discharge_date}")
        else:
            print("   ❌ No bed assignments found")
        
        # Check staff assignments
        print(f"\n👩‍⚕️ Checking staff assignments for {first_name} {last_name}...")
        cursor.execute("""
            SELECT s.employee_id, s.first_name, s.last_name, s.position, spa.assignment_type, spa.assigned_date
            FROM staff_patient_assignments spa
            JOIN staff s ON spa.staff_id = s.employee_id
            WHERE spa.patient_id = %s
        """, (patient_id,))
        
        staff_assignments = cursor.fetchall()
        if staff_assignments:
            for emp_id, staff_first, staff_last, position, assignment_type, assigned_date in staff_assignments:
                print(f"   👨‍⚕️ Staff: {staff_first} {staff_last} ({emp_id})")
                print(f"   💼 Position: {position}")
                print(f"   🔗 Assignment: {assignment_type}")
                print(f"   📅 Date: {assigned_date}")
        else:
            print("   ❌ No staff assignments found")
        
        # Check equipment usage
        print(f"\n🏥 Checking equipment assignments for {first_name} {last_name}...")
        cursor.execute("""
            SELECT e.equipment_id, e.name, e.category, eu.purpose, eu.start_time, eu.end_time, eu.status
            FROM equipment_usage eu
            JOIN equipment e ON eu.equipment_id = e.equipment_id
            WHERE eu.patient_id = %s
        """, (patient_id,))
        
        equipment_assignments = cursor.fetchall()
        if equipment_assignments:
            for eq_id, eq_name, category, purpose, start_time, end_time, eq_status in equipment_assignments:
                print(f"   🏥 Equipment: {eq_name} ({eq_id})")
                print(f"   📂 Category: {category}")
                print(f"   🎯 Purpose: {purpose}")
                print(f"   ⏰ Started: {start_time}")
                print(f"   ⏰ Ended: {end_time}")
                print(f"   📊 Status: {eq_status}")
        else:
            print("   ❌ No equipment assignments found")
        
        # Check supply transactions
        print(f"\n📦 Checking supply assignments for {first_name} {last_name}...")
        cursor.execute("""
            SELECT s.item_code, s.name, s.category, it.quantity_change, it.transaction_type, 
                   it.transaction_date, it.notes
            FROM inventory_transactions it
            JOIN supplies s ON it.supply_id = s.item_code
            WHERE it.notes LIKE %s
        """, (f"%{first_name}%{last_name}%",))
        
        supply_assignments = cursor.fetchall()
        if supply_assignments:
            for item_code, supply_name, category, qty_change, trans_type, trans_date, notes in supply_assignments:
                print(f"   📦 Supply: {supply_name} ({item_code})")
                print(f"   📂 Category: {category}")
                print(f"   📊 Quantity: {qty_change}")
                print(f"   🔄 Type: {trans_type}")
                print(f"   📅 Date: {trans_date}")
                print(f"   📝 Notes: {notes}")
        else:
            print("   ❌ No supply assignments found")
        
        # Summary
        assignment_count = len(bed_assignments) + len(staff_assignments) + len(equipment_assignments) + len(supply_assignments)
        print(f"\n📋 Assignment Summary:")
        print(f"   🛏️ Beds: {len(bed_assignments)}")
        print(f"   👩‍⚕️ Staff: {len(staff_assignments)}")
        print(f"   🏥 Equipment: {len(equipment_assignments)}")
        print(f"   📦 Supplies: {len(supply_assignments)}")
        print(f"   📊 Total: {assignment_count}")
        
        if assignment_count > 0:
            print(f"\n✅ {assignment_count} assignments found in database!")
        else:
            print(f"\n❌ No assignments found in database")
        
        cursor.close()
        conn.close()
        
        return assignment_count > 0
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    verify_mohamed_assignments_in_database()
