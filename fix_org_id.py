import sqlite3
import os

DATABASES = {
    "dev": r"backend\data\people_os_dev.db",
    "prod": r"backend\data\people_os_prod.db",
    "test": r"backend\data\people_os_test.db"
}

def fix_org_ids_for_env(env_name, db_path):
    if not os.path.exists(db_path):
        print(f"[{env_name.upper()}] DB missing. Skipping.")
        return

    print(f"\n[{env_name.upper()}] Fixing Organization IDs in {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Get correct Active Organization ID
        cursor.execute("SELECT id FROM core_organizations LIMIT 1")
        org = cursor.fetchone()
        if not org:
            print("  [ERROR] No active organization found.")
            return
        
        active_org_id = org[0]
        print(f"  Active Org ID: {active_org_id}")

        # 2. Update Restored Tables
        tables = [
            'core_locations', 
            'hcm_job_levels', 
            'core_departments', 
            'hcm_designations',
            'hcm_shifts' 
        ]
        
        for table in tables:
            try:
                # Check if table exists
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if not cursor.fetchone():
                    continue

                # Update records that belong to different organizations
                cursor.execute(f"UPDATE {table} SET organization_id = ? WHERE organization_id != ?", (active_org_id, active_org_id))
                updated = cursor.rowcount
                if updated > 0:
                    print(f"  [FIXED] {table}: Updated {updated} rows.")
                else:
                    print(f"  [OK] {table}: All rows match.")

            except Exception as e:
                print(f"  [ERROR] {table}: {e}")

        conn.commit()

    finally:
        conn.close()

if __name__ == "__main__":
    for env, path in DATABASES.items():
        fix_org_ids_for_env(env, path)
    print("\n✅ Organization ID standardization complete.")
