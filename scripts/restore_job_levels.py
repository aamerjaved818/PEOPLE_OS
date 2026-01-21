import sqlite3
import os
import time

BACKUP_DB = r'D:\Project\PEOPLE_OS\backend\data\backups\people_os.backup.db'
TARGET_DBS = [
    r'D:\Project\PEOPLE_OS\backend\data\people_os_dev.db',
    r'D:\Project\PEOPLE_OS\backend\data\people_os_test.db',
    r'D:\Project\PEOPLE_OS\backend\data\people_os_prod.db'
]

TARGET_ORG_ID = 'ORG-001'

def get_backup_data():
    if not os.path.exists(BACKUP_DB):
        print(f"Backup DB not found: {BACKUP_DB}")
        return None
    
    conn = sqlite3.connect(BACKUP_DB)
    # Use Row factory to access columns by name if needed, but tuple is fine for copying
    cursor = conn.cursor()
    
    try:
        print(f"Reading from backup: {BACKUP_DB}")
        cursor.execute(f"SELECT * FROM hcm_job_levels WHERE organization_id=?", (TARGET_ORG_ID,))
        data = cursor.fetchall()
        
        # Get column names to ensure correct mapping
        cursor.execute(f"PRAGMA table_info(hcm_job_levels)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"  -> Found {len(data)} rows for org {TARGET_ORG_ID}")
        return data, columns
    except Exception as e:
        print(f"  -> Error reading backup: {e}")
        return None, None
    finally:
        conn.close()

def restore_to_target(target_db, data, columns):
    print(f"\nRestoring to: {target_db}")
    if not os.path.exists(target_db):
        print("  -> DB file not found (Skipping)")
        return

    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()
    
    try:
        # 1. Drop incorrect table if exists
        cursor.execute("DROP TABLE IF EXISTS job_levels")
        print("  -> Dropped incorrect table 'job_levels' (if existed)")
        
        # 2. Ensure hcm_job_levels exists (Create if not)
        # Schema based on models.py
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hcm_job_levels (
            id TEXT PRIMARY KEY,
            name TEXT,
            code TEXT,
            description TEXT,
            is_active BOOLEAN,
            organization_id TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            updated_by TEXT,
            FOREIGN KEY(organization_id) REFERENCES core_organizations(id)
        );
        """)
        # Note: Added AuditMixin fields (created_at, etc) and Base fields as per likely schema
        
        # 3. Clear existing data for target org to prevent duplicates
        cursor.execute("DELETE FROM hcm_job_levels WHERE organization_id=?", (TARGET_ORG_ID,))
        print(f"  -> Cleared existing data for {TARGET_ORG_ID} ({cursor.rowcount} rows deleted)")
        
        # 4. Insert data from backup
        if not data:
            print("  -> No data to insert.")
            return

        # Prepare INSERT statement dynamically based on columns
        placeholders = ', '.join(['?'] * len(columns))
        col_names = ', '.join(columns)
        query = f"INSERT INTO hcm_job_levels ({col_names}) VALUES ({placeholders})"
        
        cursor.executemany(query, data)
        conn.commit()
        print(f"  -> Successfully restored {cursor.rowcount} rows.")
        
    except Exception as e:
        print(f"  -> Error restoring: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting Job Level Restoration...")
    rows, cols = get_backup_data()
    
    if rows and cols:
        print(f"Backup Columns: {cols}")
        for db in TARGET_DBS:
            restore_to_target(db, rows, cols)
    else:
        print("Failed to retrieve data from backup. Aborting.")
