#!/usr/bin/env python3
"""
Test the complete discharge report PDF generation and download system.
"""

import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add the backend-python directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_discharge_report_pdf_system():
    """Test the complete discharge report PDF system."""
    
    print("🧪 Testing Discharge Report PDF System")
    print("=" * 50)
    
    try:
        # Import required modules
        from multi_agent_server import (
            generate_discharge_report, 
            download_discharge_report,
            list_available_discharge_reports,
            get_discharge_report_storage_stats
        )
        
        print("✅ Successfully imported discharge report tools")
        
        # Test 1: Check storage stats
        print("\n📊 Test 1: Check storage statistics")
        stats_result = get_discharge_report_storage_stats()
        if stats_result.get('success'):
            stats = stats_result.get('stats', {})
            print(f"   Current reports: {stats.get('current_reports', 0)}")
            print(f"   Archived reports: {stats.get('archived_reports', 0)}")
            print(f"   Total size: {stats.get('total_size_mb', 0):.2f} MB")
        else:
            print(f"   ❌ Failed to get stats: {stats_result.get('error', 'Unknown error')}")
        
        # Test 2: List available reports
        print("\n📋 Test 2: List available reports")
        reports_result = list_available_discharge_reports(status="current", limit=10)
        if reports_result.get('success'):
            reports = reports_result.get('data', [])
            print(f"   Found {len(reports)} current reports")
            for report in reports[:3]:  # Show first 3
                print(f"   - {report.get('report_number')} | Patient: {report.get('patient_name')} | Generated: {report.get('generated_at', '')[:19]}")
        else:
            print(f"   ❌ Failed to list reports: {reports_result.get('error', 'Unknown error')}")
        
        # Test 3: Try to generate a new discharge report (if we have sample data)
        print("\n📄 Test 3: Generate sample discharge report")
        try:
            # First, let's check if we have any beds with patients
            from database import SessionLocal, Bed, Patient, User
            session = SessionLocal()
            beds_with_patients = session.query(Bed).filter(Bed.patient_id.isnot(None)).limit(1).all()
            
            if beds_with_patients:
                bed = beds_with_patients[0]
                print(f"   Using bed: {bed.bed_number} (ID: {bed.id})")
                
                # Generate discharge report
                discharge_result = generate_discharge_report(
                    bed_id=str(bed.id),
                    discharge_condition="stable",
                    discharge_destination="home"
                )
                
                if discharge_result.get('success'):
                    report_number = discharge_result.get('report_number')
                    print(f"   ✅ Generated report: {report_number}")
                    
                    # Test 4: Download the report as PDF
                    print(f"\n📥 Test 4: Download report {report_number} as PDF")
                    download_result = download_discharge_report(
                        report_number=report_number,
                        download_format="pdf"
                    )
                    
                    if download_result.get('success'):
                        download_path = download_result.get('download_path')
                        file_size = download_result.get('file_size', 0)
                        print(f"   ✅ PDF generated: {download_path}")
                        print(f"   File size: {file_size:,} bytes")
                        
                        # Check if file exists
                        if os.path.exists(download_path):
                            print(f"   ✅ File exists and is {os.path.getsize(download_path):,} bytes")
                        else:
                            print(f"   ❌ File not found at {download_path}")
                    else:
                        print(f"   ❌ PDF download failed: {download_result.get('error', 'Unknown error')}")
                        print(f"   Message: {download_result.get('message', '')}")
                        
                    # Test 5: Download as markdown
                    print(f"\n📄 Test 5: Download report {report_number} as Markdown")
                    markdown_result = download_discharge_report(
                        report_number=report_number,
                        download_format="markdown"
                    )
                    
                    if markdown_result.get('success'):
                        print(f"   ✅ Markdown file: {markdown_result.get('download_path')}")
                        print(f"   Size: {markdown_result.get('size', 0):,} bytes")
                    else:
                        print(f"   ❌ Markdown download failed: {markdown_result.get('error', 'Unknown error')}")
                
                else:
                    print(f"   ❌ Report generation failed: {discharge_result.get('message', 'Unknown error')}")
            else:
                print("   ℹ️  No beds with patients found - creating sample scenario")
                
                # Create sample data for testing
                from prepare_sample_data import create_complete_sample_scenario
                scenario_result = create_complete_sample_scenario()
                
                if scenario_result.get('success'):
                    print("   ✅ Sample scenario created")
                    # Try again with the new data
                    beds_with_patients = session.query(Bed).filter(Bed.patient_id.isnot(None)).limit(1).all()
                    if beds_with_patients:
                        bed = beds_with_patients[0]
                        discharge_result = generate_discharge_report(
                            bed_id=str(bed.id),
                            discharge_condition="stable",
                            discharge_destination="home"
                        )
                        print(f"   Generated report with sample data: {discharge_result.get('success', False)}")
                else:
                    print(f"   ❌ Failed to create sample scenario: {scenario_result.get('message', '')}")
            
            session.close()
            
        except Exception as e:
            print(f"   ❌ Error during report generation test: {str(e)}")
        
        print("\n🎉 Discharge Report PDF System Test Complete")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure all required modules are available")
        return False
    except Exception as e:
        print(f"❌ System test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_discharge_report_pdf_system()
    sys.exit(0 if success else 1)
