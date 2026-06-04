"""
Database Migration Script - Add Tracking Features
Run this script to add complaint tracking, timeline, and feedback features
"""

import psycopg2
import sys
from pathlib import Path

# Database configuration
DB_CONFIG = {
    'dbname': 'citizen_bridge',
    'user': 'postgres',
    'password': 'nsrit',
    'host': 'localhost',
    'port': 5432
}

def run_migration():
    """Execute the database migration SQL file"""
    print("=" * 60)
    print("  Citizen Bridge - Tracking Features Migration")
    print("=" * 60)
    print()
    
    migration_file = Path(__file__).parent / 'database_migration_tracking.sql'
    
    if not migration_file.exists():
        print(f"❌ Error: Migration file not found: {migration_file}")
        sys.exit(1)
    
    print(f"📄 Reading migration file: {migration_file.name}")
    
    try:
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("🔌 Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("📊 Executing migration...")
        cursor.execute(sql_content)
        
        print("✅ Migration completed successfully!")
        print()
        print("New features added:")
        print("  ✓ Tracking ID for all complaints")
        print("  ✓ Complaint timeline table")
        print("  ✓ Citizen feedback table")
        print("  ✓ Status history tracking")
        print()
        
        # Check if tables were created
        print("🔍 Verifying new tables...")
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('complaint_timeline', 'complaint_feedback')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        if len(tables) == 2:
            print("  ✓ complaint_timeline table created")
            print("  ✓ complaint_feedback table created")
        else:
            print("  ⚠️  Warning: Some tables may not have been created")
        
        # Check if tracking_id columns were added
        print()
        print("🔍 Verifying tracking_id columns...")
        for table in ['complaints_education', 'complaints_police', 'complaints_health', 
                     'complaints_electrical', 'complaints_transport']:
            cursor.execute(f"""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = '{table}' AND column_name = 'tracking_id'
            """)
            if cursor.fetchone():
                print(f"  ✓ {table} has tracking_id column")
            else:
                print(f"  ⚠️  {table} missing tracking_id column")
        
        cursor.close()
        conn.close()
        
        print()
        print("=" * 60)
        print("✨ Migration complete! You can now:")
        print("  1. Restart your backend server: python connet.py")
        print("  2. Open track_complaint.html to test tracking")
        print("  3. Check admin panels for new status update features")
        print("=" * 60)
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        run_migration()
    except KeyboardInterrupt:
        print("\n⚠️  Migration cancelled by user")
        sys.exit(1)
