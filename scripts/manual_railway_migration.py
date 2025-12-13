"""
Manual migration script for Railway deployment.
Run this once via Railway shell to add missing columns.
"""
import sqlite3
import os

def run_migration():
    """Add is_draft and deleted_at columns to messages table"""
    db_path = 'workflowx.db'
    
    if not os.path.exists(db_path):
        print(f"ERROR: Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(messages)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"Current columns: {columns}")
        
        # Add is_draft column if it doesn't exist
        if 'is_draft' not in columns:
            print("Adding is_draft column...")
            cursor.execute("""
                ALTER TABLE messages 
                ADD COLUMN is_draft INTEGER DEFAULT 0
            """)
            print("✓ Added is_draft column")
        else:
            print("✓ is_draft column already exists")
        
        # Add deleted_at column if it doesn't exist
        if 'deleted_at' not in columns:
            print("Adding deleted_at column...")
            cursor.execute("""
                ALTER TABLE messages 
                ADD COLUMN deleted_at TEXT
            """)
            print("✓ Added deleted_at column")
        else:
            print("✓ deleted_at column already exists")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Railway Database Migration")
    print("=" * 60)
    run_migration()
