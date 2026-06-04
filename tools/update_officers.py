import os
import psycopg2

# Mapping provided by user: department_code -> officer_name
updates = {
    '22453-ee-004': 'harsha',
    '25nu5a4012': 'jyothsna',
    '25nu5a4207': 'surya',
    '22453-cm-012': 'buddi',
    '25nu5a4203': 'jagadeesh'
}

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
    for code, name in updates.items():
        cur.execute('UPDATE department_officers SET officer_name = %s WHERE department_code = %s', (name, code))
        print(f"Updated department_code={code}: rows affected={cur.rowcount}")
    conn.commit()
    cur.close()
    conn.close()
    print('Update complete')
except Exception as e:
    print('Error during update:', e)
    import sys
    sys.exit(1)
