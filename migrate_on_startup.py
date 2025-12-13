"""
Auto-migration script that runs on Railway startup.
This ensures database schema is always up to date.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_migrations():
    """Run all pending database migrations."""
    print("=" * 60)
    print("RUNNING DATABASE MIGRATIONS")
    print("=" * 60)
    
    try:
        # Import and run message columns migration
        from scripts.add_message_draft_columns import add_message_columns
        add_message_columns()
        
        print("\n✓ All migrations completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Migration error: {str(e)}")
        print("Application will continue with existing schema.")
    
    print("=" * 60)

if __name__ == '__main__':
    run_migrations()
