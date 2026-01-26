import sqlite3
import os
import bcrypt
from datetime import datetime

DB_PATH = os.path.join('backend', 'data', 'people_os_dev.db')
ORG_CODE = 'PEOPLE01'
ORG_ID = 'PEOPLE01'
DEFAULT_PASSWORD = 'ChangeMe123!'

if not os.path.exists(DB_PATH):
    print('Database not found:', DB_PATH)
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Find organization
cur.execute("SELECT id, code, name FROM core_organizations WHERE code = ?", (ORG_CODE,))
org = cur.fetchone()
if not org:
    print('Organization not found:', ORG_CODE)
    conn.close()
    raise SystemExit(1)

org_id = org[0]
org_code = org[1]

# Check existing Super Admins for org (exclude global/system users)
cur.execute("SELECT id, username, role, employee_id, is_system_user FROM core_users WHERE organization_id = ? AND role = 'Super Admin' AND (is_system_user IS NULL OR is_system_user = 0)", (org_id,))
rows = cur.fetchall()

if len(rows) > 1:
    print('WARNING: Multiple Super Admins found for this organization. Listing:')
    for r in rows:
        print(' -', r)
    print('Will not create a new Super Admin. Resolve duplicates manually.')
    conn.close()
    raise SystemExit(1)

if len(rows) == 1:
    user = rows[0]
    user_id, username, role, employee_id, is_system = user
    print('Existing Super Admin found:', username, 'id=', user_id)
    # Ensure org-only (unlink any employee)
    if employee_id:
        print(' - Linked to employee', employee_id, ' -> unlinking to make org-only')
        cur.execute("UPDATE core_users SET employee_id=NULL WHERE id=?", (user_id,))
        conn.commit()
        print(' - Unlinked employee_id')
    else:
        print(' - Already org-only Super Admin')

    # Do not exit: ensure username/password match org id below
    # Set preferred_username variables now so later logic can operate
    preferred_username = org_code.lower()
    preferred_password = org_code.lower()

    # If existing Super Admin already has the preferred username, prepare to update its password
    if username == preferred_username:
        preferred_user_id = user_id
        now = datetime.utcnow().isoformat()
        pwd_hash = bcrypt.hashpw(preferred_password.encode(), bcrypt.gensalt()).decode()
        cur.execute("UPDATE core_users SET password_hash = ?, updated_at = ?, updated_by = ? WHERE id = ?", (pwd_hash, now, 'script', preferred_user_id))
        conn.commit()
        print('Updated password for existing preferred Super Admin:', preferred_username)
    else:
        # If a user with preferred username exists, promote them; otherwise rename current user
        cur.execute("SELECT id FROM core_users WHERE username = ?", (preferred_username,))
        pref = cur.fetchone()
        if pref:
            pref_id = pref[0]
            now = datetime.utcnow().isoformat()
            pwd_hash = bcrypt.hashpw(preferred_password.encode(), bcrypt.gensalt()).decode()
            cur.execute(
                "UPDATE core_users SET role = 'Super Admin', organization_id = ?, employee_id = NULL, is_system_user = 0, password_hash = ?, updated_at = ?, updated_by = ? WHERE id = ?",
                (org_id, pwd_hash, now, 'script', pref_id),
            )
            preferred_user_id = pref_id
            # Demote the old super admin row
            cur.execute("UPDATE core_users SET role = 'Manager', updated_at = ?, updated_by = ? WHERE id = ?", (now, 'script', user_id))
            conn.commit()
            print('Promoted existing', preferred_username, 'to Super Admin and demoted previous Super Admin')
        else:
            # Rename existing super admin to preferred username
            now = datetime.utcnow().isoformat()
            cur.execute("UPDATE core_users SET username = ?, updated_at = ?, updated_by = ? WHERE id = ?", (preferred_username, now, 'script', user_id))
            preferred_user_id = user_id
            pwd_hash = bcrypt.hashpw(preferred_password.encode(), bcrypt.gensalt()).decode()
            cur.execute("UPDATE core_users SET password_hash = ? WHERE id = ?", (pwd_hash, preferred_user_id))
            conn.commit()
            print('Renamed existing Super Admin to preferred username and updated password:', preferred_username)

preferred_username = org_code.lower()
preferred_password = org_code.lower()

# Ensure there is exactly one org-level Super Admin with username == org id (lowercase)
cur.execute("SELECT id, username FROM core_users WHERE username = ?", (preferred_username,))
existing_pref = cur.fetchone()

if existing_pref:
    pref_id = existing_pref[0]
    # Update this user to be org Super Admin and clear employee link
    pwd_hash = bcrypt.hashpw(preferred_password.encode(), bcrypt.gensalt()).decode()
    now = datetime.utcnow().isoformat()
    cur.execute(
        "UPDATE core_users SET role = ?, organization_id = ?, employee_id = NULL, is_system_user = 0, password_hash = ?, updated_at = ?, updated_by = ? WHERE id = ?",
        ('Super Admin', org_id, pwd_hash, now, 'script', pref_id),
    )
    preferred_user_id = pref_id
    print('Updated existing user to org Super Admin:', preferred_username)
else:
    # Create new user with username == org id
    pwd_hash = bcrypt.hashpw(preferred_password.encode(), bcrypt.gensalt()).decode()
    user_id = os.urandom(8).hex()
    now = datetime.utcnow().isoformat()
    cur.execute(
        "INSERT INTO core_users (id, username, password_hash, role, name, email, organization_id, employee_id, is_active, is_system_user, created_at, updated_at, created_by, updated_by) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (user_id, preferred_username, pwd_hash, 'Super Admin', f'{org_code} Super Admin', f'{preferred_username}@{org_code.lower()}.local', org_id, None, 1, 0, now, now, 'script', 'script')
    )
    preferred_user_id = user_id
    print('Created org Super Admin:', preferred_username, 'id=', preferred_user_id)

# Demote any other org Super Admins (keep only the preferred one)
cur.execute("SELECT id FROM core_users WHERE organization_id = ? AND role = 'Super Admin' AND id != ?", (org_id, preferred_user_id))
others = cur.fetchall()
if others:
    for o in others:
        oid = o[0]
        cur.execute("UPDATE core_users SET role = 'Manager', updated_at = ?, updated_by = ? WHERE id = ?", (now, 'script', oid))
    print('Demoted other Super Admins to Manager for org', org_code)

conn.commit()
print('Credentials: username=', preferred_username, ' password=', preferred_password)
conn.close()
