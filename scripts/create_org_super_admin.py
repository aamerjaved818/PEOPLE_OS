import sqlite3
import os
import uuid
import bcrypt
from datetime import datetime

DB_PATH = os.path.join('backend', 'data', 'people_os_dev.db')
ORG_CODE = 'PEOPLE01'
ORG_ID = 'PEOPLE01'
EMP_ID = 'PEOPLE01-0001'
USER_USERNAME = 'people01_admin'
USER_PASSWORD = 'ChangeMe123!'

if not os.path.exists(DB_PATH):
    print('Database not found:', DB_PATH)
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Ensure organization exists
cur.execute("SELECT id, code, name FROM core_organizations WHERE code = ?", (ORG_CODE,))
org = cur.fetchone()
if org:
    print('Organization exists:', org)
else:
    print('Creating organization', ORG_CODE)
    cur.execute(
        "INSERT INTO core_organizations (id, code, name, is_active, email) VALUES (?,?,?,?,?)",
        (ORG_ID, ORG_CODE, 'People Organization', 1, 'admin@people01.local'),
    )

# Ensure employee exists
cur.execute("SELECT id FROM hcm_employees WHERE id = ?", (EMP_ID,))
if cur.fetchone():
    print('Employee already exists:', EMP_ID)
else:
    print('Creating employee', EMP_ID)
    cur.execute(
        '''INSERT INTO hcm_employees (id, employee_code, name, organization_id, join_date, email, status)
           VALUES (?,?,?,?,?,?,?)''',
        (EMP_ID, EMP_ID, 'PEOPLE01 Super Admin', ORG_ID, datetime.utcnow().date().isoformat(), 'people01_admin@example.com', 'Active'),
    )

# Ensure user exists
cur.execute("SELECT id, username FROM core_users WHERE username = ?", (USER_USERNAME,))
row = cur.fetchone()
if row:
    print('User already exists:', row)
    user_id = row[0]
else:
    # create user
    user_id = str(uuid.uuid4())
    password_hash = bcrypt.hashpw(USER_PASSWORD.encode(), bcrypt.gensalt()).decode()
    print('Creating user', USER_USERNAME, 'id=', user_id)
    cur.execute(
        "INSERT INTO core_users (id, username, password_hash, role, name, email, organization_id, employee_id, is_active, is_system_user, created_at, updated_at, created_by, updated_by) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (user_id, USER_USERNAME, password_hash, 'Super Admin', 'PEOPLE01 Admin', 'people01_admin@example.com', ORG_ID, EMP_ID, 1, 0, datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), 'script', 'script'),
    )

conn.commit()

# Show verification
cur.execute("SELECT id, code, name FROM core_organizations WHERE code = ?", (ORG_CODE,))
print('Organization:', cur.fetchone())
cur.execute("SELECT id, employee_code, name, organization_id FROM hcm_employees WHERE id = ?", (EMP_ID,))
print('Employee:', cur.fetchone())
cur.execute("SELECT id, username, role, organization_id, employee_id FROM core_users WHERE username = ?", (USER_USERNAME,))
print('User:', cur.fetchone())

conn.close()
print('\nDone. Credentials: username=', USER_USERNAME, ' password=', USER_PASSWORD)
