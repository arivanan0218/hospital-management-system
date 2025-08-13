#!/usr/bin/env python3
"""Deep field name analysis - Check ALL agent fields against database schema"""

import re
import os
from pathlib import Path

# Database field mapping from schema analysis
DATABASE_SCHEMA = {
    "User": {
        "table": "users",
        "fields": [
            "id", "username", "email", "password_hash", "role", 
            "first_name", "last_name", "phone", "is_active", 
            "created_at", "updated_at"
        ]
    },
    "Department": {
        "table": "departments", 
        "fields": [
            "id", "name", "description", "head_doctor_id", 
            "floor_number", "phone", "email", "created_at", "updated_at"
        ]
    },
    "Patient": {
        "table": "patients",
        "fields": [
            "id", "patient_number", "first_name", "last_name", 
            "date_of_birth", "gender", "phone", "email", "address",
            "emergency_contact_name", "emergency_contact_phone", 
            "blood_type", "allergies", "medical_history", 
            "created_at", "updated_at"
        ]
    },
    "Room": {
        "table": "rooms",
        "fields": [
            "id", "room_number", "department_id", "room_type", 
            "floor_number", "capacity", "created_at", "updated_at"
        ]
    },
    "Bed": {
        "table": "beds",
        "fields": [
            "id", "bed_number", "room_id", "bed_type", "status", 
            "patient_id", "admission_date", "discharge_date", 
            "notes", "created_at", "updated_at"
        ]
    },
    "Staff": {
        "table": "staff",
        "fields": [
            "id", "user_id", "employee_id", "department_id", 
            "position", "specialization", "license_number", 
            "hire_date", "salary", "shift_pattern", "status", 
            "created_at", "updated_at"
        ]
    },
    "Equipment": {
        "table": "equipment",
        "fields": [
            "id", "equipment_id", "name", "category_id", "model", 
            "manufacturer", "serial_number", "purchase_date", 
            "warranty_expiry", "location", "department_id", "status", 
            "last_maintenance", "next_maintenance", "cost", "notes", 
            "created_at", "updated_at"
        ]
    },
    "EquipmentCategory": {
        "table": "equipment_categories",
        "fields": [
            "id", "name", "description", "created_at"
        ]
    },
    "Supply": {
        "table": "supplies",
        "fields": [
            "id", "item_code", "name", "category_id", "description", 
            "unit_of_measure", "minimum_stock_level", "maximum_stock_level", 
            "current_stock", "unit_cost", "supplier", "expiry_date", 
            "location", "created_at", "updated_at"
        ]
    },
    "SupplyCategory": {
        "table": "supply_categories",
        "fields": [
            "id", "name", "description", "created_at"
        ]
    },
    "Appointment": {
        "table": "appointments",
        "fields": [
            "id", "patient_id", "doctor_id", "department_id", 
            "appointment_date", "duration_minutes", "status", 
            "reason", "notes", "created_at", "updated_at"
        ]
    },
    "MedicalDocument": {
        "table": "medical_documents",
        "fields": [
            "id", "patient_id", "document_type", "file_name", 
            "file_path", "file_size", "mime_type", "upload_date", 
            "extracted_text", "processing_status", "extracted_metadata", 
            "confidence_score", "created_at", "updated_at"
        ]
    }
}

def analyze_agent_file(agent_file):
    """Analyze a single agent file for field usage"""
    print(f"\n📄 Analyzing: {agent_file.name}")
    print("-" * 50)
    
    with open(agent_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    issues = []
    
    # Find all create_* methods
    create_methods = re.findall(r'def (create_\w+)\(([^)]+)\)', content)
    
    for method_name, params in create_methods:
        print(f"\n🔍 Method: {method_name}")
        
        # Extract model name from method (e.g., create_patient -> Patient)
        model_name = method_name.replace('create_', '').replace('_', '').title()
        if model_name.endswith('s'):
            model_name = model_name[:-1]  # Remove plural
        
        # Handle special cases
        model_mapping = {
            'Equipmentcategory': 'EquipmentCategory',
            'Supplycategory': 'SupplyCategory',
            'Staff': 'Staff',
            'Equipment': 'Equipment'
        }
        
        if model_name in model_mapping:
            model_name = model_mapping[model_name]
        elif model_name + 'Category' in DATABASE_SCHEMA:
            model_name = model_name + 'Category'
        
        print(f"   Target Model: {model_name}")
        
        if model_name not in DATABASE_SCHEMA:
            print(f"   ⚠️  Unknown model: {model_name}")
            continue
        
        # Find the actual model instantiation
        model_pattern = rf'{model_name}\s*\(\s*([^)]+)\)'
        model_matches = re.findall(model_pattern, content)
        
        if not model_matches:
            # Try lowercase version
            model_pattern = rf'{model_name.lower()}\s*\(\s*([^)]+)\)'
            model_matches = re.findall(model_pattern, content)
        
        if model_matches:
            model_fields_str = model_matches[0]
            # Extract field assignments
            field_assignments = re.findall(r'(\w+)\s*=', model_fields_str)
            
            print(f"   Fields used: {field_assignments}")
            
            # Check against database schema
            db_fields = DATABASE_SCHEMA[model_name]["fields"]
            
            for field in field_assignments:
                if field not in db_fields:
                    issue = f"❌ {agent_file.name}::{method_name} - Field '{field}' not in {model_name} model"
                    issues.append(issue)
                    print(f"   {issue}")
                else:
                    print(f"   ✅ {field} - OK")
        
        # Also check method parameters against expected fields
        param_list = [p.strip().split(':')[0].strip() for p in params.split(',') if ':' in p]
        print(f"   Method params: {param_list}")
        
        # Check for common parameter issues
        for param in param_list:
            if param == 'purpose' and model_name == 'Appointment':
                issue = f"❌ {agent_file.name}::{method_name} - Parameter 'purpose' should be 'reason'"
                issues.append(issue)
                print(f"   {issue}")
            elif param == 'appointment_time' and model_name == 'Appointment':
                issue = f"❌ {agent_file.name}::{method_name} - Parameter 'appointment_time' - should combine with appointment_date"
                issues.append(issue)
                print(f"   {issue}")
            elif param in ['minimum_stock', 'maximum_stock'] and model_name == 'Supply':
                issue = f"❌ {agent_file.name}::{method_name} - Parameter '{param}' should be '{param}_level'"
                issues.append(issue)
                print(f"   {issue}")
            elif param == 'unit_price' and model_name == 'Supply':
                issue = f"❌ {agent_file.name}::{method_name} - Parameter 'unit_price' should be 'unit_cost'"
                issues.append(issue)
                print(f"   {issue}")
    
    return issues

def main():
    """Main analysis function"""
    print("🔍 DEEP FIELD NAME ANALYSIS")
    print("Checking ALL agent fields against database schema")
    print("=" * 60)
    
    # Get all agent files
    agents_dir = Path("backend-python/agents")
    agent_files = [f for f in agents_dir.glob("*_agent.py") if f.name != "base_agent.py"]
    
    all_issues = []
    
    for agent_file in sorted(agent_files):
        issues = analyze_agent_file(agent_file)
        all_issues.extend(issues)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 60)
    
    if all_issues:
        print(f"❌ Found {len(all_issues)} field name issues:")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i:2d}. {issue}")
    else:
        print("✅ No field name issues found! All agents match database schema.")
    
    # Recommendations
    print("\n📋 RECOMMENDATIONS:")
    if all_issues:
        print("1. Fix the field name mismatches listed above")
        print("2. Test each agent after fixing")
        print("3. Update frontend to use correct parameter names")
    else:
        print("1. All field names are correctly aligned")
        print("2. POST functions should work correctly")
    
    print("\n🎯 Analysis complete!")

if __name__ == "__main__":
    main()
