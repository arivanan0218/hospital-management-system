#!/usr/bin/env python3
"""
Install PDF generation dependencies for the hospital management system.
"""

import subprocess
import sys

def install_pdf_dependencies():
    """Install required dependencies for PDF generation."""
    
    print("📦 Installing PDF Generation Dependencies")
    print("=" * 45)
    
    dependencies = [
        "reportlab>=3.6.0",      # PDF generation
        "markdown2>=2.4.0",      # Markdown to HTML conversion
        "Pillow>=9.0.0",         # Image processing for PDFs
    ]
    
    for package in dependencies:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    print("\n🎉 All PDF dependencies installed successfully!")
    return True

def test_imports():
    """Test that all required imports work."""
    
    print("\n🧪 Testing PDF Dependencies")
    print("=" * 30)
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        print("✅ ReportLab imports successful")
        
        import markdown2
        print("✅ Markdown2 import successful")
        
        from PIL import Image
        print("✅ Pillow (PIL) import successful")
        
        print("\n🎉 All imports working correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    success = install_pdf_dependencies()
    if success:
        success = test_imports()
    
    sys.exit(0 if success else 1)
