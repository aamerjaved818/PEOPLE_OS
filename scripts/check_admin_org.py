import sqlite3
import os

DB_PATH = r"backend\data\people_os_dev.db"

def check_admin():
    if not os.path.exists(DB_PATH):
        print(f"DB not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Checking Admin User in {DB_PATH}...")
    
    # Get Admin User
    cursor.execute("SELECT id, username, organization_id FROM core_users WHERE username='admin'")
    admin = cursor.fetchone()
    
    if not admin:
        print("  [ERROR] User 'admin' not found!")
        return

    admin_id, username, org_id = admin
    print(f"  User: {username}")
    print(f"  Current Org ID: {org_id}")
    
    # Check what Org this ID resolves to
    cursor.execute("SELECT name FROM core_organizations WHERE id=?", (org_id,))
    org_name = cursor.fetchone()
    
    if org_name:
        print(f"  Org Name: {org_name[0]}")
    else:
        print(f"  [WARNING] Organization not found for ID: {org_id}")

    # Check Data Counts for this Org
    tables = ['core_locations', 'hcm_job_levels', 'core_departments']
    for table in tables:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE organization_id=?", (org_id,)).fetchone()[0]
        print(f"  My Data in {table}: {count} rows")

    conn.close()

if __name__ == "__main__":
    check_admin()
