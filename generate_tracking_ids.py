import psycopg2
import secrets
from datetime import datetime

def generate_tracking_id(department):
    """Generate a unique tracking ID"""
    dept_codes = {
        'education': 'EDU',
        'police': 'POL',
        'health': 'HLT',
        'electrical': 'ELE',
        'transport': 'TRN'
    }
    dept_code = dept_codes.get(department, 'GEN')
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = secrets.token_hex(2).upper()
    return f"{dept_code}-{date_str}-{random_str}"

def generate_tracking_ids_for_department(cursor, department):
    """Generate tracking IDs for all complaints in a department without tracking IDs"""
    table_name = f"complaints_{department}"
    
    # Get complaints without tracking IDs
    cursor.execute(f"""
        SELECT id, created_at 
        FROM {table_name} 
        WHERE tracking_id IS NULL
    """)
    
    complaints = cursor.fetchall()
    updated_count = 0
    
    for complaint_id, created_at in complaints:
        # Generate unique tracking ID
        while True:
            tracking_id = generate_tracking_id(department)
            
            # Check if tracking ID already exists in any table
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE tracking_id = %s", (tracking_id,))
            if cursor.fetchone()[0] == 0:
                break
        
        # Update complaint with tracking ID
        cursor.execute(f"""
            UPDATE {table_name}
            SET tracking_id = %s
            WHERE id = %s
        """, (tracking_id, complaint_id))
        
        # Add initial timeline entry
        cursor.execute("""
            INSERT INTO complaint_timeline (complaint_id, department, status, notes, changed_by)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            complaint_id,
            department,
            'Submitted',
            f'Complaint submitted - Tracking ID: {tracking_id}',
            'System'
        ))
        
        updated_count += 1
        print(f"  ✓ Generated {tracking_id} for complaint ID {complaint_id}")
    
    return updated_count

def main():
    print("=" * 60)
    print("GENERATING TRACKING IDs FOR EXISTING COMPLAINTS")
    print("=" * 60)
    
    # Database connection
    conn = psycopg2.connect(
        dbname="citizen_bridge",
        user="postgres",
        password="nsrit",
        host="localhost",
        port="5432"
    )
    
    cursor = conn.cursor()
    departments = ['education', 'police', 'health', 'electrical', 'transport']
    total_updated = 0
    
    try:
        for dept in departments:
            print(f"\n📋 Processing {dept.upper()} department...")
            count = generate_tracking_ids_for_department(cursor, dept)
            total_updated += count
            print(f"   Updated {count} complaints")
        
        # Commit all changes
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ SUCCESS: Generated tracking IDs for {total_updated} complaints")
        print("=" * 60)
        
        # Verification
        print("\n📊 VERIFICATION:")
        for dept in departments:
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total,
                    COUNT(tracking_id) as with_tracking,
                    COUNT(*) - COUNT(tracking_id) as without_tracking
                FROM complaints_{dept}
            """)
            total, with_tracking, without_tracking = cursor.fetchone()
            print(f"  {dept.upper()}: {total} total, {with_tracking} with tracking ID, {without_tracking} pending")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
