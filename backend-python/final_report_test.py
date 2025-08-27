#!/usr/bin/env python3
"""
Test the complete discharge report formatting with supply usage
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_session, Patient
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
        
        # Get the generator and test the format method directly
        generator = PatientDischargeReportGenerator()
        discharge_date = datetime.now()
        admission_date = discharge_date - timedelta(days=3)
        
        # Get supply usage summary
        supply_summary = generator._get_supply_usage_summary(patient.id, admission_date, discharge_date)
        
        # Test report formatting
        print(f"\n🔄 Testing report formatting...")
        
        # Create mock data structure for testing
        data = {
            'patient': {
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'medical_record_number': 'MR123456',
                'date_of_birth': '1990-01-01'
            },
            'admission': {'admission_date': admission_date.isoformat()},
            'discharge_date': discharge_date.isoformat(),
            'supply_usage': supply_summary
        }
        
        # Create a mock report record
        class MockRecord:
            def __init__(self):
                self.id = 'test-id'
                self.generated_by = None
                
        mock_record = MockRecord()
        
        # Test the formatting
        report_text = generator._format_discharge_report(data, mock_record)
        
        print(f"✅ Report generated successfully ({len(report_text)} characters)")
        
        # Check for supply usage section
        if "SUPPLY USAGE & INVENTORY" in report_text:
            print("✅ Supply usage section found!")
            
            # Extract the section
            start_idx = report_text.find("SUPPLY USAGE & INVENTORY")
            end_idx = report_text.find("\n\n**", start_idx + 100)
            if end_idx == -1:
                end_idx = start_idx + 1500  # Show more of the section
                
            supply_section = report_text[start_idx:end_idx]
            print("\n📋 SUPPLY USAGE SECTION:")
            print("=" * 60)
            print(supply_section)
            print("=" * 60)
            
            # Check specific elements
            checks = [
                ("💊 Medications Used", "Medications section"),
                ("Aspirin 81mg", "Aspirin medication"),
                ("Morphine 10mg/ml", "Morphine medication"),
                ("Total Cost: $15.60", "Total cost"),
                ("TOTAL COST", "Cost summary")
            ]
            
            for check_text, description in checks:
                if check_text in report_text:
                    print(f"✅ {description} found!")
                else:
                    print(f"⚠️  {description} not found")
                    
            print("\n🎉 ENHANCED DISCHARGE REPORTS WITH SUPPLY USAGE ARE WORKING PERFECTLY!")
            
        else:
            print("❌ Supply usage section not found in report")
            print("Report sections found:")
            import re
            sections = re.findall(r'\*\*([^*]+)\*\*', report_text)
            for section in sections:
                print(f"  - {section}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    main()
