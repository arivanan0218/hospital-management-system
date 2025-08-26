#!/usr/bin/env python3

import psycopg2
import json
from datetime import datetime, timedelta

def setup_bed_401a_cleaning():
    """Directly setup bed 401A cleaning in the database"""
    
    try:
        # Database connection
        conn = psycopg2.connect(
            host="localhost",
            database="hospital_management",
            user="postgres",
            password="1234"
        )
        cursor = conn.cursor()
        
        # Get bed UUID
        cursor.execute("SELECT id FROM beds WHERE bed_number = %s", ("401A",))
        bed_result = cursor.fetchone()
        
        if not bed_result:
            print("❌ Bed 401A not found")
            return
            
        bed_id = bed_result[0]
        print(f"✅ Found bed 401A: {bed_id}")
        
        # Update bed status to cleaning
        cursor.execute("""
            UPDATE beds 
            SET status = 'cleaning', updated_at = NOW()
            WHERE id = %s
        """, (bed_id,))
        
        # Delete any existing turnover record
        cursor.execute("DELETE FROM bed_turnovers WHERE bed_id = %s", (bed_id,))
        
        # Create new turnover record
        discharge_time = datetime.now() - timedelta(minutes=5)  # Discharged 5 minutes ago
        cleaning_start = datetime.now()
        
        cursor.execute("""
            INSERT INTO bed_turnovers 
            (id, bed_id, turnover_type, status, discharge_time, cleaning_start_time, 
             estimated_cleaning_duration, notes)
            VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s)
        """, (
            bed_id,
            'post_discharge',
            'cleaning', 
            discharge_time,
            cleaning_start,
            30,
            'Cleaning after patient discharge - demonstration'
        ))
        
        conn.commit()
        print("✅ Bed 401A set to cleaning status with 30-minute turnover")
        
        # Verify the setup
        cursor.execute("""
            SELECT b.bed_number, b.status, bt.status as turnover_status, 
                   bt.estimated_cleaning_duration, bt.cleaning_start_time, bt.discharge_time
            FROM beds b
            LEFT JOIN bed_turnovers bt ON b.id = bt.bed_id
            WHERE b.bed_number = %s
        """, ("401A",))
        
        result = cursor.fetchone()
        if result:
            bed_num, status, turnover_status, duration, cleaning_start, discharge_time = result
            print(f"🏥 Bed: {bed_num}")
            print(f"🧹 Status: {status}")
            print(f"🔄 Turnover: {turnover_status}")
            print(f"⏰ Duration: {duration} minutes")
            print(f"🕐 Cleaning started: {cleaning_start}")
            print(f"🕐 Discharged: {discharge_time}")
        
        cursor.close()
        conn.close()
        print("\n✅ Database setup complete!")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    setup_bed_401a_cleaning()
