"""
Database Migration Script
Adds Message table and admin_notes column to LeaveRequest table
Works with both SQLite and SQL Server
"""

from app import app, db
from models import Message, LeaveRequest
from sqlalchemy import text, inspect

def migrate_database():
    """Add new columns and tables to existing database."""
    with app.app_context():
        print("🔄 Starting database migration...")
        
        try:
            # Detect database type
            inspector = inspect(db.engine)
            db_url = str(db.engine.url)
            is_sqlite = 'sqlite' in db_url.lower()
            is_mssql = 'mssql' in db_url.lower() or 'sqlserver' in db_url.lower()
            
            print(f"  📊 Database type: {'SQLite' if is_sqlite else 'SQL Server' if is_mssql else 'Unknown'}")
            
            # Check if admin_notes column exists
            columns = [col['name'] for col in inspector.get_columns('leave_requests')]
            
            if 'admin_notes' not in columns:
                print("  ➕ Adding admin_notes column to leave_requests...")
                with db.engine.connect() as conn:
                    if is_sqlite:
                        conn.execute(text("ALTER TABLE leave_requests ADD COLUMN admin_notes TEXT"))
                    else:  # SQL Server or other
                        conn.execute(text("ALTER TABLE leave_requests ADD admin_notes NVARCHAR(MAX)"))
                    conn.commit()
                print("  ✅ admin_notes column added successfully")
            else:
                print("  ℹ️  admin_notes column already exists")
            
            # Create messages table if it doesn't exist
            if 'messages' not in inspector.get_table_names():
                print("  ➕ Creating messages table...")
                db.create_all()
                print("  ✅ messages table created successfully")
            else:
                print("  ℹ️  messages table already exists")
            
            print("✅ Database migration completed successfully!")
            print("\n📝 Changes applied:")
            print("   - Added 'admin_notes' column to leave_requests table")
            print("   - Created 'messages' table for internal messaging")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    migrate_database()
