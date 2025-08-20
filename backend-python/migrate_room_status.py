"""
Database Migration: Add status column to rooms table
====================================================

This migration adds the missing 'status' column to the rooms table.
"""

from database import SessionLocal, engine
from sqlalchemy import text

def add_room_status_column():
    """Add status column to rooms table if it doesn't exist."""
    session = SessionLocal()
    
    try:
        print("🔄 Checking if rooms.status column exists...")
        
        # Check if status column already exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'rooms' AND column_name = 'status'
        """)
        
        result = session.execute(check_query).fetchone()
        
        if result:
            print("✅ rooms.status column already exists")
            return True
        
        print("➕ Adding status column to rooms table...")
        
        # Add the status column
        alter_query = text("""
            ALTER TABLE rooms 
            ADD COLUMN status VARCHAR(20) DEFAULT 'available'
        """)
        
        session.execute(alter_query)
        session.commit()
        
        print("✅ Successfully added status column to rooms table")
        
        # Update existing rooms to have 'available' status
        update_query = text("""
            UPDATE rooms 
            SET status = 'available' 
            WHERE status IS NULL
        """)
        
        session.execute(update_query)
        session.commit()
        
        print("✅ Updated existing rooms with 'available' status")
        return True
        
    except Exception as e:
        print(f"❌ Error adding status column: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def test_room_status():
    """Test that room status is working."""
    session = SessionLocal()
    
    try:
        from database import Room
        
        print("🧪 Testing room status functionality...")
        
        # Get a sample room
        room = session.query(Room).first()
        
        if room:
            print(f"✅ Sample room: {room.room_number}")
            print(f"✅ Room status: {room.status}")
            return True
        else:
            print("❌ No rooms found to test")
            return False
            
    except Exception as e:
        print(f"❌ Error testing room status: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("🏥 Room Status Migration")
    print("=" * 40)
    
    # Step 1: Add the column
    if add_room_status_column():
        # Step 2: Test the functionality
        test_room_status()
        print("🎉 Room status migration complete!")
    else:
        print("❌ Migration failed")
