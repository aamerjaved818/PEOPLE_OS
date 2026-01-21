import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os_dev.db")
print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Disable FKs
    cursor.execute("PRAGMA foreign_keys = OFF;")
    conn.execute("BEGIN TRANSACTION;")

    print(f"\nScanning hcm_job_levels...")
    cursor.execute(f"SELECT id, code, name FROM hcm_job_levels")
    rows = cursor.fetchall()
    
    updates_count = 0
    for row in rows:
        old_id = row[0]
        raw_code = row[1]
        name = row[2]
        
        if not raw_code:
            print(f"  [SKIP] Skipping {name} (old_id: {old_id}): No Code provided.")
            continue
            
        new_id = raw_code.strip().upper()
        
        if old_id == new_id:
            # Already migrated
            continue
            
        # Check if new_id already exists (collision check)
        cursor.execute(f"SELECT count(*) FROM hcm_job_levels WHERE id = ?", (new_id,))
        if cursor.fetchone()[0] > 0:
             print(f"  [ERROR] Collision: Target ID {new_id} already exists! Cannot migrate {name} ({old_id}).")
             continue

        print(f"  Migrating: {name} | {old_id} -> {new_id}")
        
        # 1. Update the record itself
        cursor.execute(f"UPDATE hcm_job_levels SET id = ? WHERE id = ?", (new_id, old_id))
        
        # 2. Update dependents: hcm_grades
        cursor.execute(f"UPDATE hcm_grades SET job_level_id = ? WHERE job_level_id = ?", (new_id, old_id))
        if cursor.rowcount > 0:
            print(f"    -> Updated {cursor.rowcount} linked grades.")
        
        updates_count += 1
        
    print(f"  Finished: {updates_count} updates processed.")

    conn.commit()
    print("\nTransaction committed.")

    # --- Final Integrity Check ---
    print("\nChecking foreign key integrity...")
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA foreign_key_check;")
    errors = cursor.fetchall()
    if errors:
        print("Integrity Violations Found:")
        for error in errors:
            print(error)
    else:
        print("Integrity Check Passed.")

    conn.close()

except Exception as e:
    print(f"Migration Failed: {e}")
    if conn:
        conn.rollback()
        print("Transaction Rolled Back.")
