import os
import psycopg2

DB_CONFIG = {
    'dbname': os.environ.get('CB_DB_NAME', 'citizen_bridge'),
    'user': os.environ.get('CB_DB_USER', 'postgres'),
    'password': os.environ.get('CB_DB_PASSWORD', os.environ.get('PGPASSWORD', '1437')),
    'host': os.environ.get('CB_DB_HOST', 'localhost'),
    'port': int(os.environ.get('CB_DB_PORT', 5432))
}

print('Using DB config:', {k: (v if k!='password' else '***') for k,v in DB_CONFIG.items()})

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute('SELECT id, username, officer_name, department_code, department_id, email, phone, created_at FROM department_officers ORDER BY id')
    rows = cur.fetchall()
    if not rows:
        print('No rows found in department_officers')
    else:
        print('\nCurrent department_officers:')
        for r in rows:
            print(f'id={r[0]:<3} username={r[1] or "":<20} officer_name={r[2] or "":<25} dept_code={r[3] or "":<15} dept_id={str(r[4]) if r[4] else "":<5} email={r[5] or "":<25} phone={r[6] or "":<15} created_at={r[7]}')
    cur.close()
    conn.close()
except Exception as e:
    print('Error connecting or querying DB:', e)
    import sys
    sys.exit(1)
