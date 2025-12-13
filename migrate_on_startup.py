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
        
        # Get absolute path
        abs_db_path = os.path.abspath(db_path)
        print(f"Looking for database at: {abs_db_path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Database exists: {os.path.exists(db_path)}")
        
        if os.path.exists(db_path):
            print(f"Found database: {db_path}")
            
            # Connect with explicit timeout
            conn = sqlite3.connect(db_path, timeout=30.0)
            cursor = conn.cursor()
            
            # Check if messages table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
            if not cursor.fetchone():
                print("⚠ messages table does not exist yet - skipping migration")
                conn.close()
                return
            
            # Check current columns
            cursor.execute("PRAGMA table_info(messages)")
            columns_info = cursor.fetchall()
            columns = [col[1] for col in columns_info]
            print(f"Current columns in messages table: {columns}")
            
            changes_made = False
            
            # Add is_draft column if missing
            if 'is_draft' not in columns:
                print("Adding is_draft column...")
                cursor.execute("ALTER TABLE messages ADD COLUMN is_draft INTEGER DEFAULT 0")
                changes_made = True
                print("✓ Added is_draft column")
                
                # Update existing messages to not be drafts
                cursor.execute("UPDATE messages SET is_draft = 0 WHERE is_draft IS NULL")
                print("✓ Updated existing messages to is_draft=0")
            else:
                print("✓ is_draft column already exists")
            
            # Add deleted_at column if missing
            if 'deleted_at' not in columns:
                print("Adding deleted_at column...")
                cursor.execute("ALTER TABLE messages ADD COLUMN deleted_at TEXT")
                changes_made = True
                print("✓ Added deleted_at column")
            else:
                print("✓ deleted_at column already exists")
            
            if changes_made:
                conn.commit()
                print("\n✓ All migrations committed successfully!")
                
                # Verify changes
                cursor.execute("PRAGMA table_info(messages)")
                new_columns = [col[1] for col in cursor.fetchall()]
                print(f"Updated columns: {new_columns}")
            else:
                print("\n✓ No migrations needed - schema is up to date")
            
            conn.close()
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
