#!/usr/bin/env python3
"""
Manually update bed 401A to active cleaning status in database
"""

from database import SessionLocal, BedTurnover, Bed
from sqlalchemy import text
import uuid
from datetime import datetime, timedelta

def update_bed_401a_to_cleaning():
    """Update bed 401A to active cleaning status"""
    session = SessionLocal()
    try:
        # Find bed 401A
        bed_401a = session.query(Bed).filter(Bed.bed_number == '401A').first()
        if not bed_401a:
            print("❌ Bed 401A not found")
            return
            
        print(f"✅ Found bed 401A (ID: {bed_401a.id})")
        
        # Find or create turnover record
        turnover = session.query(BedTurnover).filter(
            BedTurnover.bed_id == bed_401a.id,
            BedTurnover.status.in_(['initiated', 'cleaning'])
        ).first()
        
        if turnover:
            print(f"✅ Found existing turnover record")
            # Update to active cleaning
            turnover.status = 'cleaning'
            turnover.cleaning_start_time = datetime.now() - timedelta(minutes=5)  # Started 5 minutes ago
            turnover.estimated_cleaning_duration = 30
            print(f"✅ Updated turnover to active cleaning (5 minutes elapsed, 25 minutes remaining)")
        else:
            print("Creating new cleaning turnover record...")
            turnover = BedTurnover(
                bed_id=bed_401a.id,
                previous_patient_id=None,
                status='cleaning',
                turnover_type='standard',
                discharge_time=datetime.now() - timedelta(minutes=10),
                cleaning_start_time=datetime.now() - timedelta(minutes=5),  # Started 5 minutes ago
                estimated_cleaning_duration=30
            )
            session.add(turnover)
            print(f"✅ Created new cleaning turnover record")
        
        # Update bed status to cleaning
        bed_401a.status = 'cleaning'
        bed_401a.updated_at = datetime.now()
        
        session.commit()
        print(f"✅ Updated bed 401A status to 'cleaning'")
        
        # Show final status
        elapsed = (datetime.now() - turnover.cleaning_start_time).total_seconds() / 60
        remaining = max(0, turnover.estimated_cleaning_duration - elapsed)
        progress = min(100, (elapsed / turnover.estimated_cleaning_duration) * 100)
        
        print(f"\n🏥 BED 401A CLEANING STATUS:")
        print(f"════════════════════════════════")
        print(f"🧽 Status: CLEANING IN PROGRESS")
        print(f"⏱️  Time Remaining: {remaining:.0f} minutes")
        print(f"📊 Progress: {progress:.1f}%")
        print(f"────────────────────────────────")
        print(f"💡 🧽 Bed is actively being cleaned...")
        print(f"⏰ Estimated completion in {remaining:.0f} minutes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    print("🏥 UPDATING BED 401A TO ACTIVE CLEANING")
    print("═════════════════════════════════════")
    update_bed_401a_to_cleaning()
