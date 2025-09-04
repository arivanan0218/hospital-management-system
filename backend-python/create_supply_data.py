"""Script to create comprehensive supply categories and supplies data."""

import sys
import os
import uuid
import random
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import (
    test_connection, SessionLocal,
    Supply, SupplyCategory, Department, User
)

def create_supply_data():
    """Create comprehensive supply categories and supplies data."""
    db = SessionLocal()
    
    try:
        print("Creating supply categories and supplies...")
        
        # === STEP 1: Create Supply Categories ===
        print("1. Creating supply categories...")
        
        supply_categories_data = [
            ("Medications", "Pharmaceuticals and medical drugs"),
            ("Surgical Supplies", "Items used in surgical procedures"),
            ("Wound Care", "Supplies for wound treatment and dressing"),
            ("IV and Injection", "Intravenous and injection related supplies"),
            ("Diagnostic Supplies", "Items for patient diagnosis and testing"),
            ("Personal Protective Equipment", "Safety equipment for staff and patients"),
            ("Patient Care", "General patient care and comfort items"),
            ("Laboratory Supplies", "Lab testing and analysis materials"),
            ("Emergency Supplies", "Emergency response and trauma care items"),
            ("Rehabilitation", "Physical therapy and recovery supplies"),
            ("Nutrition", "Dietary and nutritional supplements"),
            ("Sterilization", "Cleaning and sterilization materials"),
            ("Respiratory Care", "Breathing and oxygen therapy supplies"),
            ("Cardiac Care", "Heart and cardiovascular care supplies"),
            ("Pediatric Care", "Children's healthcare specific supplies")
        ]
        
        supply_categories = []
        for name, description in supply_categories_data:
            category = SupplyCategory(
                name=name,
                description=description
            )
            supply_categories.append(category)
        
        db.add_all(supply_categories)
        db.commit()
        
        print(f"✅ Created {len(supply_categories)} supply categories")
        
        # === STEP 2: Create Supplies ===
        print("2. Creating supplies...")
        
        # Comprehensive supply data organized by category
        supplies_by_category = {
            "Medications": [
                ("Acetaminophen 500mg", "Pain reliever and fever reducer", "tablet"),
                ("Ibuprofen 200mg", "Anti-inflammatory pain reliever", "tablet"),
                ("Aspirin 81mg", "Low-dose aspirin for cardiac care", "tablet"),
                ("Morphine 10mg/ml", "Strong pain medication", "ml"),
                ("Insulin (Regular)", "Diabetes medication", "unit"),
                ("Insulin (Long-acting)", "Extended diabetes medication", "unit"),
                ("Epinephrine 1mg/ml", "Emergency allergy/cardiac medication", "ml"),
                ("Amoxicillin 500mg", "Antibiotic medication", "tablet"),
                ("Lisinopril 10mg", "Blood pressure medication", "tablet"),
                ("Metformin 500mg", "Diabetes medication", "tablet"),
                ("Prednisone 5mg", "Anti-inflammatory steroid", "tablet"),
                ("Warfarin 5mg", "Blood thinner medication", "tablet"),
                ("Digoxin 0.25mg", "Heart rhythm medication", "tablet"),
                ("Furosemide 40mg", "Diuretic medication", "tablet"),
                ("Albuterol Inhaler", "Respiratory bronchodilator", "inhaler"),
                ("Nitroglycerin 0.4mg", "Cardiac chest pain medication", "tablet"),
                ("Heparin 5000u/ml", "Blood thinner injection", "ml"),
                ("Lidocaine 2%", "Local anesthetic", "ml"),
                ("Normal Saline 0.9%", "IV fluid solution", "ml"),
                ("Lactated Ringers", "IV electrolyte solution", "ml")
            ],
            "Surgical Supplies": [
                ("Surgical Gloves (Size 7)", "Sterile latex surgical gloves", "pair"),
                ("Surgical Gloves (Size 8)", "Sterile latex surgical gloves", "pair"),
                ("Surgical Mask", "Disposable surgical face mask", "piece"),
                ("Surgical Gown", "Sterile surgical protection gown", "piece"),
                ("Surgical Drape", "Sterile surgical field drape", "piece"),
                ("Scalpel Blade #15", "Disposable surgical blade", "piece"),
                ("Scalpel Blade #11", "Disposable surgical blade", "piece"),
                ("Surgical Suture 3-0", "Non-absorbable suture material", "piece"),
                ("Surgical Suture 4-0", "Non-absorbable suture material", "piece"),
                ("Absorbable Suture 2-0", "Absorbable suture material", "piece"),
                ("Surgical Staples", "Wound closure staples", "piece"),
                ("Hemostatic Agent", "Bleeding control powder", "g"),
                ("Bone Wax", "Surgical bone bleeding control", "g"),
                ("Surgical Sponges", "Absorbent surgical sponges", "piece"),
                ("Electrocautery Tips", "Disposable cautery tips", "piece"),
                ("Surgical Clips", "Vessel closure clips", "piece"),
                ("Trocar 5mm", "Laparoscopic port", "piece"),
                ("Trocar 12mm", "Laparoscopic port", "piece"),
                ("Endotracheal Tube 7.0", "Airway intubation tube", "piece"),
                ("Endotracheal Tube 8.0", "Airway intubation tube", "piece")
            ],
            "Wound Care": [
                ("Gauze Pads 4x4", "Sterile wound dressing pads", "piece"),
                ("Gauze Pads 2x2", "Small sterile dressing pads", "piece"),
                ("Medical Tape 1 inch", "Adhesive medical tape", "roll"),
                ("Medical Tape 2 inch", "Wide adhesive medical tape", "roll"),
                ("Transparent Dressing", "Clear adhesive wound cover", "piece"),
                ("Hydrocolloid Dressing", "Advanced wound healing dressing", "piece"),
                ("Foam Dressing", "Absorbent foam wound dressing", "piece"),
                ("Silver Sulfadiazine Cream", "Antimicrobial wound cream", "g"),
                ("Antibiotic Ointment", "Topical infection prevention", "g"),
                ("Hydrogen Peroxide 3%", "Wound cleaning solution", "ml"),
                ("Betadine Solution", "Antiseptic wound cleaner", "ml"),
                ("Alcohol Prep Pads", "Skin preparation wipes", "piece"),
                ("Iodine Prep Pads", "Antiseptic preparation wipes", "piece"),
                ("Elastic Bandage 4 inch", "Compression support bandage", "roll"),
                ("Elastic Bandage 6 inch", "Wide compression bandage", "roll"),
                ("Wound Irrigation Syringe", "Wound cleaning syringe", "piece"),
                ("Skin Staple Remover", "Surgical staple removal tool", "piece"),
                ("Suture Removal Kit", "Sterile suture removal set", "kit"),
                ("Pressure Bandage", "Emergency bleeding control", "piece"),
                ("Burn Gel", "Cooling burn treatment gel", "g")
            ],
            "IV and Injection": [
                ("IV Catheter 18G", "Large bore IV catheter", "piece"),
                ("IV Catheter 20G", "Medium bore IV catheter", "piece"),
                ("IV Catheter 22G", "Small bore IV catheter", "piece"),
                ("IV Catheter 24G", "Pediatric IV catheter", "piece"),
                ("IV Tubing Set", "Standard IV administration set", "piece"),
                ("IV Extension Set", "IV line extension tubing", "piece"),
                ("Syringe 1ml", "Small volume injection syringe", "piece"),
                ("Syringe 3ml", "Medium volume injection syringe", "piece"),
                ("Syringe 5ml", "Standard injection syringe", "piece"),
                ("Syringe 10ml", "Large volume injection syringe", "piece"),
                ("Needle 25G 1 inch", "Thin injection needle", "piece"),
                ("Needle 23G 1 inch", "Standard injection needle", "piece"),
                ("Needle 21G 1.5 inch", "Large injection needle", "piece"),
                ("IV Bag 500ml Normal Saline", "IV fluid bag", "bag"),
                ("IV Bag 1000ml Normal Saline", "Large IV fluid bag", "bag"),
                ("IV Bag 500ml D5W", "Dextrose IV solution", "bag"),
                ("Blood Collection Tube", "Vacuum blood draw tube", "piece"),
                ("Butterfly Needle 23G", "Winged blood collection needle", "piece"),
                ("Tourniquet", "Blood draw compression band", "piece"),
                ("IV Site Dressing", "Catheter site protection", "piece")
            ],
            "Diagnostic Supplies": [
                ("Urine Collection Cup", "Sterile urine specimen container", "piece"),
                ("Blood Culture Bottle", "Sterile blood culture medium", "bottle"),
                ("Throat Swab", "Bacterial culture swab", "piece"),
                ("Wound Culture Swab", "Sterile specimen collection swab", "piece"),
                ("Pregnancy Test Strip", "Urine pregnancy detection", "piece"),
                ("Glucose Test Strip", "Blood sugar testing strip", "piece"),
                ("pH Test Strip", "Urine pH testing strip", "piece"),
                ("Ketone Test Strip", "Urine ketone detection strip", "piece"),
                ("Hemoglobin Test Kit", "Blood hemoglobin testing", "kit"),
                ("Cholesterol Test Kit", "Blood cholesterol screening", "kit"),
                ("ECG Electrodes", "Heart rhythm monitoring pads", "piece"),
                ("Pulse Oximeter Probe", "Oxygen saturation sensor", "piece"),
                ("Thermometer Probe Cover", "Disposable temperature cover", "piece"),
                ("Blood Pressure Cuff Adult", "Standard BP measurement cuff", "piece"),
                ("Blood Pressure Cuff Pediatric", "Child BP measurement cuff", "piece"),
                ("Stethoscope Diaphragm", "Replacement stethoscope part", "piece"),
                ("Otoscope Speculum", "Ear examination attachment", "piece"),
                ("Ophthalmoscope Bulb", "Eye examination light bulb", "piece"),
                ("Reflex Hammer", "Neurological testing tool", "piece"),
                ("Tuning Fork", "Hearing and vibration testing", "piece")
            ],
            "Personal Protective Equipment": [
                ("N95 Respirator Mask", "High filtration respiratory protection", "piece"),
                ("Surgical Mask", "Basic face protection mask", "piece"),
                ("Face Shield", "Full face protection shield", "piece"),
                ("Safety Goggles", "Eye protection glasses", "piece"),
                ("Nitrile Gloves Small", "Powder-free examination gloves", "piece"),
                ("Nitrile Gloves Medium", "Powder-free examination gloves", "piece"),
                ("Nitrile Gloves Large", "Powder-free examination gloves", "piece"),
                ("Latex Gloves Small", "Natural rubber examination gloves", "piece"),
                ("Latex Gloves Medium", "Natural rubber examination gloves", "piece"),
                ("Latex Gloves Large", "Natural rubber examination gloves", "piece"),
                ("Isolation Gown", "Protective clothing garment", "piece"),
                ("Hair Cover", "Disposable head protection", "piece"),
                ("Shoe Covers", "Disposable foot protection", "pair"),
                ("Hand Sanitizer 500ml", "Alcohol-based hand disinfectant", "bottle"),
                ("Disinfectant Wipes", "Surface cleaning wipes", "piece"),
                ("Biohazard Bag", "Infectious waste disposal bag", "piece"),
                ("Sharps Container", "Needle disposal container", "piece"),
                ("Respirator Fit Test Kit", "N95 mask fitting supplies", "kit"),
                ("Disposable Apron", "Fluid-resistant protection apron", "piece"),
                ("Lead Apron", "Radiation protection garment", "piece")
            ],
            "Patient Care": [
                ("Adult Diaper Large", "Incontinence protection garment", "piece"),
                ("Adult Diaper Medium", "Incontinence protection garment", "piece"),
                ("Bed Pad Disposable", "Absorbent bed protection", "piece"),
                ("Bed Sheet Set", "Hospital bed linens", "set"),
                ("Pillow Case", "Washable pillow cover", "piece"),
                ("Patient Gown", "Hospital patient clothing", "piece"),
                ("Blanket Warmer", "Heated patient comfort blanket", "piece"),
                ("Ice Pack", "Cold therapy pack", "piece"),
                ("Heat Pack", "Warm therapy pack", "piece"),
                ("Denture Cup", "Dental appliance storage", "piece"),
                ("Emesis Basin", "Vomit collection basin", "piece"),
                ("Bedpan", "Patient waste collection", "piece"),
                ("Urinal", "Male patient urine collection", "piece"),
                ("Commode Liner", "Portable toilet liner", "piece"),
                ("Wash Basin", "Patient bathing basin", "piece"),
                ("Soap Dispenser", "Hand hygiene soap dispenser", "piece"),
                ("Lotion Bottle", "Skin moisturizing lotion", "bottle"),
                ("Shampoo", "Hair cleaning product", "bottle"),
                ("Toothbrush", "Oral hygiene brush", "piece"),
                ("Toothpaste", "Oral hygiene paste", "tube")
            ]
        }
        
        supplies = []
        supply_counter = 1
        
        for category_name, supply_items in supplies_by_category.items():
            # Find the category
            category = next(c for c in supply_categories if c.name == category_name)
            
            for name, description, unit in supply_items:
                supply = Supply(
                    item_code=f"SUP{supply_counter:05d}",
                    name=name,
                    category_id=category.id,
                    description=description,
                    unit_of_measure=unit,
                    minimum_stock_level=random.randint(10, 50),
                    maximum_stock_level=random.randint(100, 500),
                    current_stock=random.randint(25, 200),
                    unit_cost=Decimal(f"{random.uniform(0.5, 100.0):.2f}"),
                    supplier=random.choice([
                        "MedSupply Corp", "Healthcare Solutions", "Medical Distributors Inc",
                        "Premier Medical", "Cardinal Health", "McKesson", "Henry Schein",
                        "Medline Industries", "Owens & Minor", "Patterson Medical"
                    ]),
                    expiry_date=date.today() + timedelta(days=random.randint(180, 1095)),
                    location=random.choice([
                        "Pharmacy", "Supply Room A", "Supply Room B", "Central Storage",
                        "Emergency Stock", "ICU Supply", "OR Supply", "Lab Storage"
                    ])
                )
                supplies.append(supply)
                supply_counter += 1
        
        # Add supplies in batches to avoid memory issues
        batch_size = 50
        for i in range(0, len(supplies), batch_size):
            batch = supplies[i:i + batch_size]
            db.add_all(batch)
            db.commit()
            print(f"✅ Added supplies batch {i//batch_size + 1}/{(len(supplies)-1)//batch_size + 1}")
        
        print(f"✅ Created {len(supplies)} supplies across {len(supply_categories)} categories")
        
        # Print summary
        print(f"\n📊 Supply Data Summary:")
        print(f"Supply Categories: {db.query(SupplyCategory).count()}")
        print(f"Supplies: {db.query(Supply).count()}")
        
        # Print category breakdown
        print(f"\n📈 Supplies by Category:")
        for category in supply_categories:
            count = db.query(Supply).filter(Supply.category_id == category.id).count()
            print(f"  {category.name}: {count} items")
        
    except Exception as e:
        print(f"❌ Error creating supply data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function to create supply data."""
    print("🏥 Hospital Management System - Supply Data Creation")
    print("=" * 60)
    
    # Test connection
    print("1. Testing database connection...")
    if not test_connection():
        print("❌ Database connection failed. Please check your PostgreSQL setup.")
        print("💡 Make sure:")
        print("   - PostgreSQL is running")
        print("   - Database 'hospital_management' exists")
        print("   - Credentials in .env file are correct")
        return
    
    # Create supply data
    print("2. Creating supply categories and supplies...")
    try:
        create_supply_data()
        print("✅ Supply data created successfully!")
    except Exception as e:
        print(f"❌ Error creating supply data: {e}")
        return
    
    print("\n🎉 Supply data creation completed successfully!")
    print("\n📋 What was created:")
    print("  - 15 comprehensive supply categories")
    print("  - 140+ individual supply items")
    print("  - Realistic stock levels and pricing")
    print("  - Proper categorization and metadata")
    
    print("\n🔧 Next steps:")
    print("  - Run the multi-agent server to use supply tools")
    print("  - Test supply management features")
    print("  - Use supply codes (SUP00001, SUP00002, etc.) in tools")

if __name__ == "__main__":
    main()
