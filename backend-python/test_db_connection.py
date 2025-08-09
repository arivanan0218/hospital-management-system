#!/usr/bin/env python3
"""
Simple database connectivity test script for AWS deployment
"""
import os
import sys
import time
import psycopg2
from psycopg2 import sql

def test_database_connection():
    """Test database connection with retry logic"""
    print("🔍 Testing database connection...")
    
    # Database configuration
    db_config = {
        'host': 'localhost',  # In ECS task, containers share localhost
        'port': 5432,
        'database': 'hospital_management',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    print(f"📋 Database config: {db_config}")
    
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1}/{max_retries}...")
            
            # Try to connect
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✅ Database connection successful! Result: {result}")
            
            # Test if tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cursor.fetchall()
            print(f"📊 Found {len(tables)} tables: {[t[0] for t in tables]}")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
            else:
                print("❌ Max retries reached")
                return False
    
    return False

if __name__ == "__main__":
    print("🧪 Database Connectivity Test")
    print("=" * 50)
    
    if test_database_connection():
        print("🎉 Database is ready!")
        sys.exit(0)
    else:
        print("❌ Database connection failed")
        sys.exit(1)
