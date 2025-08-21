#!/usr/bin/env python3
"""
Deployment PDF Diagnostic Script
This script helps identify PDF generation issues in deployment
"""

import os
import sys
from pathlib import Path
import json

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking Dependencies...")
    dependencies = {
        'reportlab': False,
        'markdown2': False,
        'pathlib': False,
        'database': False
    }
    
    try:
        import reportlab
        dependencies['reportlab'] = True
        print(f"✅ reportlab version: {reportlab.Version}")
    except ImportError as e:
        print(f"❌ reportlab missing: {e}")
    
    try:
        import markdown2
        dependencies['markdown2'] = True
        print(f"✅ markdown2 available")
    except ImportError as e:
        print(f"❌ markdown2 missing: {e}")
    
    try:
        from pathlib import Path
        dependencies['pathlib'] = True
        print(f"✅ pathlib available")
    except ImportError as e:
        print(f"❌ pathlib missing: {e}")
    
    try:
        import database
        dependencies['database'] = True
        print(f"✅ database module available")
    except ImportError as e:
        print(f"❌ database missing: {e}")
    
    return dependencies

def check_file_permissions():
    """Check file permissions for PDF creation"""
    print("\n🔍 Checking File Permissions...")
    
    reports_dir = Path("reports/discharge/downloads")
    
    try:
        # Create directories if they don't exist
        reports_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory created: {reports_dir}")
        
        # Test file creation
        test_file = reports_dir / "test_permissions.txt"
        with open(test_file, 'w') as f:
            f.write("Permission test")
        
        if test_file.exists():
            test_file.unlink()  # Delete test file
            print(f"✅ File creation/deletion permissions OK")
            return True
        else:
            print(f"❌ Cannot create files in {reports_dir}")
            return False
            
    except Exception as e:
        print(f"❌ Permission error: {e}")
        return False

def test_pdf_creation():
    """Test minimal PDF creation"""
    print("\n🔍 Testing PDF Creation...")
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        
        # Create minimal test PDF
        test_file = Path("test_deployment_pdf.pdf")
        doc = SimpleDocTemplate(str(test_file), pagesize=A4)
        styles = getSampleStyleSheet()
        
        story = []
        story.append(Paragraph("DEPLOYMENT PDF TEST", styles['Title']))
        story.append(Paragraph("If you can read this, PDF generation works.", styles['Normal']))
        
        doc.build(story)
        
        if test_file.exists():
            file_size = test_file.stat().st_size
            print(f"✅ Test PDF created: {test_file} ({file_size} bytes)")
            
            # Validate PDF by trying to read it
            with open(test_file, 'rb') as f:
                pdf_header = f.read(10)
                if pdf_header.startswith(b'%PDF'):
                    print(f"✅ PDF header valid: {pdf_header}")
                    is_valid = True
                else:
                    print(f"❌ Invalid PDF header: {pdf_header}")
                    is_valid = False
            
            # Keep the test file for manual inspection
            print(f"📄 Test PDF saved as: {test_file}")
            return is_valid
        else:
            print(f"❌ Test PDF was not created")
            return False
            
    except Exception as e:
        print(f"❌ PDF creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_report_manager():
    """Test the actual ReportManager PDF generation"""
    print("\n🔍 Testing ReportManager...")
    
    try:
        from report_manager import ReportManager
        
        manager = ReportManager()
        print("✅ ReportManager initialized")
        
        # Test with sample content
        sample_content = """# DEPLOYMENT TEST REPORT
## Test Section
This is a test report for deployment validation.

### Patient Information
- Name: Test Patient
- ID: TEST-001
- Status: Testing PDF Generation

### Conclusion
If this PDF renders correctly, the deployment is working.
"""
        
        test_file = Path("test_report_manager.pdf")
        sample_data = {
            "report_number": "TEST-DEPLOY-001",
            "patient_name": "Test Patient",
            "generated_date": "2025-08-21"
        }
        
        success = manager._generate_pdf(sample_content, str(test_file), sample_data)
        
        if success and test_file.exists():
            file_size = test_file.stat().st_size
            print(f"✅ ReportManager PDF created: {test_file} ({file_size} bytes)")
            
            # Validate PDF
            with open(test_file, 'rb') as f:
                pdf_header = f.read(10)
                if pdf_header.startswith(b'%PDF'):
                    print(f"✅ ReportManager PDF is valid")
                    return True
                else:
                    print(f"❌ ReportManager PDF is corrupted")
                    return False
        else:
            print(f"❌ ReportManager PDF generation failed")
            return False
            
    except Exception as e:
        print(f"❌ ReportManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_environment_info():
    """Check environment information"""
    print("\n🔍 Environment Information...")
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Environment variables:")
    
    env_vars = ['PATH', 'PYTHONPATH', 'HOME', 'USER', 'LANG']
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        print(f"  {var}: {value[:100]}{'...' if len(str(value)) > 100 else ''}")

def generate_diagnostic_report():
    """Generate a comprehensive diagnostic report"""
    print("🏥 PDF DEPLOYMENT DIAGNOSTIC REPORT")
    print("=" * 60)
    
    results = {}
    
    # Run all tests
    results['dependencies'] = check_dependencies()
    results['file_permissions'] = check_file_permissions()
    results['basic_pdf'] = test_pdf_creation()
    results['report_manager'] = test_report_manager()
    
    check_environment_info()
    
    print("\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    all_good = True
    
    if not all(results['dependencies'].values()):
        print("❌ DEPENDENCY ISSUES:")
        for dep, status in results['dependencies'].items():
            if not status:
                print(f"   - Missing: {dep}")
        all_good = False
    else:
        print("✅ All dependencies available")
    
    if not results['file_permissions']:
        print("❌ FILE PERMISSION ISSUES")
        all_good = False
    else:
        print("✅ File permissions OK")
    
    if not results['basic_pdf']:
        print("❌ BASIC PDF CREATION FAILED")
        all_good = False
    else:
        print("✅ Basic PDF creation works")
    
    if not results['report_manager']:
        print("❌ REPORT MANAGER PDF CREATION FAILED")
        all_good = False
    else:
        print("✅ ReportManager PDF creation works")
    
    print("\n🎯 RECOMMENDATIONS:")
    if all_good:
        print("✅ All tests passed! PDF generation should work.")
        print("   If you're still seeing issues, the problem might be:")
        print("   1. Network/file serving issues")
        print("   2. Browser PDF viewer problems")
        print("   3. File corruption during transfer")
    else:
        print("❌ Issues found. Fix the problems above and retest.")
        
        if not all(results['dependencies'].values()):
            print("\n📦 To fix dependencies, run:")
            for dep, status in results['dependencies'].items():
                if not status:
                    print(f"   pip install {dep}")
    
    print("\n📄 Test PDF files created:")
    test_files = ['test_deployment_pdf.pdf', 'test_report_manager.pdf']
    for test_file in test_files:
        if Path(test_file).exists():
            size = Path(test_file).stat().st_size
            print(f"   - {test_file} ({size} bytes)")
            print(f"     Try opening this file to test if PDF viewing works")

if __name__ == "__main__":
    generate_diagnostic_report()
