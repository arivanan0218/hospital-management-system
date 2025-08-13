#!/usr/bin/env python3
"""
Check existing database table structure
"""

import sys
import os

# Add the backend-python directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
import logging

# Database configuration using user's credentials
DATABASE_URL = "postgresql://postgres:Smrm%405670@localhost:5433/hospital_management"

def check_table_structure():
    """Check existing table structures"""
    
    try:
        # Create database engine
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check existing tables
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            
            tables = result.fetchall()
            print("📋 Existing tables:")
            for table in tables:
                print(f"   - {table[0]}")
            
            # Check meetings table if it exists
            if any(table[0] == 'meetings' for table in tables):
                print("\n📊 Meetings table structure:")
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default 
                    FROM information_schema.columns 
                    WHERE table_name = 'meetings' 
                    ORDER BY ordinal_position;
                """))
                
                columns = result.fetchall()
                for col in columns:
                    print(f"   {col[0]}: {col[1]} (nullable: {col[2]})")
            
            # Check meeting_participants table if it exists
            if any(table[0] == 'meeting_participants' for table in tables):
                print("\n📊 Meeting Participants table structure:")
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default 
                    FROM information_schema.columns 
                    WHERE table_name = 'meeting_participants' 
                    ORDER BY ordinal_position;
                """))
                
                columns = result.fetchall()
                for col in columns:
                    print(f"   {col[0]}: {col[1]} (nullable: {col[2]})")
            
            print("\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Checking Hospital Management System database structure...")
    
    check_table_structure()
