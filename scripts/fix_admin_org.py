import sqlite3
import os

DATABASES = {
    "dev": r"backend\data\people_os_dev.db",
    "prod": r"backend\data\people_os_prod.db",
    "test": r"backend\data\people_os_test.db"
}

def fix_admin(env_name, db_path):
    if not os.path.exists(db_path):
        print(f"[{env_name.upper()}] DB missing. Skipping.")
        return

    print(f"\n[{env_name.upper()}] Checking Admin in {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Get VALID Organization
        cursor.execute("SELECT id FROM core_organizations WHERE is_active=1 LIMIT 1")
        org = cursor.fetchone()
        
        if not org:
            # Fallback to any org
            cursor.execute("SELECT id FROM core_organizations LIMIT 1")
            org = cursor.fetchone()
            
        if not org:
            print("  [ERROR] No Organization found in DB!")
            return

        org_id = org[0]
        print(f"  Target Organization: {org_id}")

        # 2. Update Admin
        cursor.execute("UPDATE core_users SET organization_id = ? WHERE username = 'admin'", (org_id,))
        if cursor.rowcount > 0:
            print(f"  [SUCCESS] Admin linked to {org_id}")
        else:
            print("  [INFO] Admin user not found or already linked.")
            
        conn.commit()
    
    finally:
        conn.close()

if __name__ == "__main__":
    for env, path in DATABASES.items():
        fix_admin(env, path)
    print("\n✅ Admin User Organization Link Fixed.")
