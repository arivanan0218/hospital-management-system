"""
Database Migration: Add PatientSupplyUsage table and relationships
This script adds the new patient supply usage tracking functionality
"""

import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
from database import SessionLocal, Base, engine

def run_migration():
    """Run the database migration to add PatientSupplyUsage table"""
    
    print("🔄 Starting database migration for PatientSupplyUsage...")
    
    try:
        # Create all tables (this will only create new ones)
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/updated successfully")
        
        # Add supply_usage column to discharge_reports if not exists
        db = SessionLocal()
        try:
            # Check if supply_usage column exists
            result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'discharge_reports' 
                AND column_name = 'supply_usage'
            """)).fetchone()
            
            if not result:
                print("📝 Adding supply_usage column to discharge_reports table...")
                db.execute(text("""
                    ALTER TABLE discharge_reports 
                    ADD COLUMN supply_usage TEXT
                """))
                db.commit()
                print("✅ Added supply_usage column to discharge_reports")
            else:
                print("ℹ️  supply_usage column already exists in discharge_reports")
                
        except Exception as e:
            print(f"⚠️  Could not add supply_usage column (might already exist): {e}")
            db.rollback()
        finally:
            db.close()
        
        print("✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        return False

def create_sample_supplies():
    """Create sample medical supplies and categories for testing"""
    
    print("🔄 Creating sample medical supplies...")
    
    try:
        from database import Supply, SupplyCategory
        
        db = SessionLocal()
        
        # Create medication category if not exists
        med_category = db.query(SupplyCategory).filter(
            SupplyCategory.name == "Medications"
        ).first()
        
        if not med_category:
            med_category = SupplyCategory(
                name="Medications",
                description="Pharmaceutical medications and drugs"
            )
            db.add(med_category)
            db.commit()
            db.refresh(med_category)
            print("✅ Created Medications category")
        
        # Create medical supplies category if not exists
        supplies_category = db.query(SupplyCategory).filter(
            SupplyCategory.name == "Medical Supplies"
        ).first()
        
        if not supplies_category:
            supplies_category = SupplyCategory(
                name="Medical Supplies",
                description="General medical supplies and consumables"
            )
            db.add(supplies_category)
            db.commit()
            db.refresh(supplies_category)
            print("✅ Created Medical Supplies category")
        
        # Sample medications
        sample_medications = [
            {
                "item_code": "MED001",
                "name": "Paracetamol 500mg",
                "unit_of_measure": "tablets",
                "unit_cost": 0.25,
                "current_stock": 1000
            },
            {
                "item_code": "MED002", 
                "name": "Ibuprofen 400mg",
                "unit_of_measure": "tablets",
                "unit_cost": 0.35,
                "current_stock": 500
            },
            {
                "item_code": "MED003",
                "name": "Amoxicillin 250mg",
                "unit_of_measure": "capsules",
                "unit_cost": 0.75,
                "current_stock": 200
            }
        ]
        
        # Sample medical supplies
        sample_supplies = [
            {
                "item_code": "SUP001",
                "name": "Disposable Syringe 5ml",
                "unit_of_measure": "pieces",
                "unit_cost": 0.50,
                "current_stock": 1000
            },
            {
                "item_code": "SUP002",
                "name": "Sterile Gauze Pad",
                "unit_of_measure": "pieces", 
                "unit_cost": 0.25,
                "current_stock": 500
            },
            {
                "item_code": "SUP003",
                "name": "IV Fluid Bag 1L",
                "unit_of_measure": "bags",
                "unit_cost": 15.00,
                "current_stock": 100
            }
        ]
        
        # Create medications
        for med_data in sample_medications:
            existing = db.query(Supply).filter(Supply.item_code == med_data["item_code"]).first()
            if not existing:
                medication = Supply(
                    item_code=med_data["item_code"],
                    name=med_data["name"],
                    category_id=med_category.id,
                    unit_of_measure=med_data["unit_of_measure"],
                    unit_cost=med_data["unit_cost"],
                    current_stock=med_data["current_stock"],
                    minimum_stock_level=50
                )
                db.add(medication)
                print(f"✅ Created medication: {med_data['name']}")
        
        # Create medical supplies
        for sup_data in sample_supplies:
            existing = db.query(Supply).filter(Supply.item_code == sup_data["item_code"]).first()
            if not existing:
                supply = Supply(
                    item_code=sup_data["item_code"],
                    name=sup_data["name"],
                    category_id=supplies_category.id,
                    unit_of_measure=sup_data["unit_of_measure"],
                    unit_cost=sup_data["unit_cost"],
                    current_stock=sup_data["current_stock"],
                    minimum_stock_level=20
                )
                db.add(supply)
                print(f"✅ Created supply: {sup_data['name']}")
        
        db.commit()
        db.close()
        
        print("✅ Sample supplies created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample supplies: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

if __name__ == "__main__":
    print("🏥 Hospital Management System - Database Migration")
    print("=" * 60)
    
    # Run migration
    migration_success = run_migration()
    
    if migration_success:
        # Create sample data
        create_sample_supplies()
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("\n📋 New Features Available:")
        print("  - Patient Supply Usage Tracking")
        print("  - Medication Administration Records")
        print("  - Supply Usage in Discharge Reports")
        print("  - Cost Tracking for Patient Medications")
        print("\n🔧 New Tools Added:")
        print("  - record_patient_supply_usage")
        print("  - get_patient_supply_usage")
        print("  - update_supply_usage_status")
        print("  - get_supply_usage_for_discharge_report")
        print("  - list_patient_medications")
        print("  - search_supply_usage_by_patient")
        print("  - calculate_patient_medication_costs")
        
    else:
        print("\n" + "=" * 60)
        print("❌ Migration failed. Please check the errors above.")
