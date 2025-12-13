"""
Auto-migration script that runs on Railway startup.
This ensures database schema is always up to date.
"""

import os
import sys
import sqlite3

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_migrations():
    """Run all pending database migrations."""
    print("=" * 60)
    print("RUNNING DATABASE MIGRATIONS")
    print("=" * 60)
    
    try:
        # Direct SQLite migration - no dependencies needed
        db_path = 'workflowx.db'
        
        if os.path.exists(db_path):
            print(f"Found database: {db_path}")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check current columns
            cursor.execute("PRAGMA table_info(messages)")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"Current columns: {columns}")
            
            # Add is_draft column if missing
            if 'is_draft' not in columns:
                print("Adding is_draft column...")
                cursor.execute("ALTER TABLE messages ADD COLUMN is_draft INTEGER DEFAULT 0")
                print("✓ Added is_draft column")
            else:
                print("✓ is_draft column already exists")
            
            # Add deleted_at column if missing
            if 'deleted_at' not in columns:
                print("Adding deleted_at column...")
                cursor.execute("ALTER TABLE messages ADD COLUMN deleted_at TEXT")
                print("✓ Added deleted_at column")
            else:
                print("✓ deleted_at column already exists")
            
            conn.commit()
            conn.close()
            print("\n✓ All migrations completed successfully!")
        else:
            print(f"Database not found at {db_path}, will be created on first run")
        
    except Exception as e:
        print(f"\n✗ Migration error: {str(e)}")
        import traceback
        traceback.print_exc()
        print("Application will continue with existing schema.")
    
    print("=" * 60)

if __name__ == '__main__':
    run_migrations()
