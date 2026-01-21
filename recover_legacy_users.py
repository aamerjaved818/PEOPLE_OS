import sqlite3
import shutil
import os

BACKUP_DB = r"backend\data\backups\people_os.backup.db"
TARGET_DB = r"backend\data\people_os_dev.db"

if not os.path.exists(BACKUP_DB):
    print(f"Backup DB not found at {BACKUP_DB}")
    exit(1)

print(f"Reading from: {BACKUP_DB}")

try:
    src_conn = sqlite3.connect(BACKUP_DB)
    src_cursor = src_conn.cursor()

    # Check for .amer and admin
    users_to_check = [".amer", "admin"]
    
    for username in users_to_check:
        row = src_cursor.execute("SELECT * FROM core_users WHERE username=?", (username,)).fetchone()
        if row:
            print(f"✅ Found '{username}' in backup. ID: {row[0]}")
            
            # Prepare migration to dev DB
            # We need to act carefully. Insert if not exists.
            tgt_conn = sqlite3.connect(TARGET_DB)
            tgt_cursor = tgt_conn.cursor()
            
            existing = tgt_cursor.execute("SELECT id FROM core_users WHERE username=?", (username,)).fetchone()
            if existing:
                 print(f"   ⚠️ User '{username}' already exists in DEV DB query (ID: {existing[0]}). Skipping overwrite.")
            else:
                 print(f"   🚀 Restoring '{username}' to DEV DB...")
                 # Get columns to construct insert dynamically or just use indices if schema matches
                 # Assuming schema match for now or just mapping known fields
                 # row structure: id, username, password_hash, role, name, email, is_active, is_system_user, created_at, updated_at, created_by, updated_by, organization_id, employee_id
                 
                 # Let's use column names to be safe
                 cols = [description[0] for description in src_cursor.description]
                 placeholders = ",".join(["?"] * len(cols))
                 sql = f"INSERT INTO core_users ({','.join(cols)}) VALUES ({placeholders})"
                 
                 try:
                     tgt_cursor.execute(sql, row)
                     tgt_conn.commit()
                     print("   ✅ Restore MATCHED and COMMITTED.")
                 except Exception as e:
                     print(f"   ❌ Restore FAILED: {e}")
            
            tgt_conn.close()

        else:
             print(f"❌ User '{username}' NOT FOUND in backup.")

    src_conn.close()

except Exception as e:
    print(f"Error: {e}")
