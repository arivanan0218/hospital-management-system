#!/usr/bin/env python3
"""
Quick verification of supply usage functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_session, PatientSupplyUsage, Patient
from discharge_report_service import PatientDischargeReportGenerator
from datetime import datetime, timedelta

def main():
    session = get_db_session()
    
    try:
        # Find Alice Williams
        patient = session.query(Patient).filter(Patient.first_name == 'Alice').first()
        if not patient:
            print("❌ Patient Alice not found")
            return
            
        print(f"✅ Found patient: {patient.first_name} {patient.last_name}")
        
        # Check supply usage records
        usage_records = session.query(PatientSupplyUsage).filter(
            PatientSupplyUsage.patient_id == patient.id
        ).all()
        
        print(f"📋 Found {len(usage_records)} supply usage records")
        
        for record in usage_records:
            supply_name = record.supply.name if record.supply else 'Unknown'
            print(f"  - {supply_name}: {record.quantity_used} units, ${record.total_cost}")
        
        # Test supply usage summary generation
        generator = PatientDischargeReportGenerator()
        discharge_date = datetime.now()
        admission_date = discharge_date - timedelta(days=3)
        
        print(f"\n🔄 Testing supply summary generation...")
        supply_summary = generator._get_supply_usage_summary(patient.id, admission_date, discharge_date)
        
        print(f"✅ Summary generated:")
        print(f"  - Medications: {len(supply_summary.get('medications', []))}")
        print(f"  - Medical supplies: {len(supply_summary.get('medical_supplies', []))}")
        print(f"  - Total cost: ${supply_summary.get('total_cost', 0)}")
        
        if supply_summary.get('medications'):
            print("\n💊 Medications found:")
            for med in supply_summary['medications']:
                print(f"  - {med.get('item_name', 'Unknown')}: {med.get('dosage', 'N/A')}")
        
        print("\n🎉 Supply usage functionality is working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    main()
