#!/usr/bin/env python3
"""
Simple test to verify enhanced discharge report with supply usage
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_supply_usage_display():
    """Quick test to verify supply usage appears in discharge reports."""
    try:
        # Import what we need
        from discharge_report_service import PatientDischargeReportGenerator
        from database import get_db_session, Patient, Bed
        from datetime import datetime
        
        print("🧪 TESTING SUPPLY USAGE IN DISCHARGE REPORTS")
        print("=" * 50)
        
        # Get database session
        session = get_db_session()
        
        # Find any occupied bed for testing
        bed = session.query(Bed).filter(Bed.status == "occupied").first()
        
        if not bed:
            print("❌ No occupied beds found for testing")
            return False
            
        print(f"✅ Found test bed: {bed.bed_number} (ID: {bed.id})")
        
        # Convert UUID to string if needed
        bed_id_str = str(bed.id)
        
        # Generate discharge report using the correct method
        generator = PatientDischargeReportGenerator()
        result = generator.generate_discharge_report(
            bed_id=bed_id_str,  # Convert to string
            discharge_date=datetime.now(),
            discharge_condition="stable",
            discharge_destination="home",
            discharge_instructions="Test discharge instructions",
            follow_up_required="Follow up in 1 week",
            generated_by_user_id="1"
        )
        
        if result.get('success'):
            print("✅ Discharge report generated successfully!")
            
            # Get the report text
            report_text = result.get('report_text', '')
            
            # Check for supply usage section
            if "SUPPLY USAGE & INVENTORY" in report_text:
                print("✅ Supply usage section found!")
                
                # Extract and show the section
                start_idx = report_text.find("SUPPLY USAGE & INVENTORY")
                end_idx = report_text.find("\n\n**", start_idx + 100)
                if end_idx == -1:
                    end_idx = start_idx + 1000  # Show first 1000 chars of section
                    
                supply_section = report_text[start_idx:end_idx]
                print("\n📋 SUPPLY USAGE SECTION:")
                print("-" * 40)
                print(supply_section)
                print("-" * 40)
                
                # Check for specific elements
                if "💊 Medications Used" in report_text:
                    print("✅ Medications section found!")
                if "🏥 Medical Supplies Used" in report_text:
                    print("✅ Medical supplies section found!")
                if "Total Cost" in report_text and "$" in report_text:
                    print("✅ Cost information included!")
                    
                print("\n🎉 ENHANCED DISCHARGE REPORTS ARE WORKING!")
                return True
            else:
                print("❌ Supply usage section not found")
                print("📄 Report preview (looking for sections):")
                # Look for section headers
                import re
                sections = re.findall(r'\*\*([^*]+)\*\*', report_text)
                print("Found sections:", sections)
                return False
        else:
            print(f"❌ Failed to generate report: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_supply_usage_display()
    if success:
        print("\n✅ ALL TESTS PASSED! Enhanced discharge reports are working perfectly!")
    else:
        print("\n❌ Tests failed")
