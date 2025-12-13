"""
Database Migration: Add is_draft and deleted_at columns to messages table.

This script adds support for draft messages and soft deletion.
Run this once to update your MS SQL Server database schema.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text

def add_message_columns():
    """Add is_draft and deleted_at columns to messages table."""
    print("Starting database migration...")
    print("Adding is_draft and deleted_at columns to messages table...")
    
    try:
        with app.app_context():
            # Check if columns already exist
            check_query = text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'messages' 
                AND COLUMN_NAME IN ('is_draft', 'deleted_at')
            """)
            
            result = db.session.execute(check_query).fetchone()
            existing_count = result[0]
            
            if existing_count == 2:
                print("✓ Columns already exist. No migration needed.")
                return
            
            # Add is_draft column (boolean, default False)
            print("Adding is_draft column...")
            add_is_draft = text("""
                ALTER TABLE messages
                ADD is_draft BIT NOT NULL DEFAULT 0
            """)
            db.session.execute(add_is_draft)
            print("✓ is_draft column added")
            
            # Add deleted_at column (datetime, nullable)
            print("Adding deleted_at column...")
            add_deleted_at = text("""
                ALTER TABLE messages
                ADD deleted_at DATETIME NULL
            """)
            db.session.execute(add_deleted_at)
            print("✓ deleted_at column added")
            
            # Commit changes
            db.session.commit()
            print("\n✓ Migration completed successfully!")
            print("  - is_draft column added (BIT, default 0)")
            print("  - deleted_at column added (DATETIME, nullable)")
            
    except Exception as e:
        db.session.rollback()
        print(f"\n✗ Migration failed: {str(e)}")
        print("\nIf columns already exist, you can ignore this error.")
        raise

if __name__ == '__main__':
    print("=" * 60)
    print("MESSAGE TABLE MIGRATION")
    print("=" * 60)
    print()
    add_message_columns()
    print()
    print("=" * 60)
