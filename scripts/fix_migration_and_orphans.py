import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os_dev.db")
print(f"Connecting to database at: {db_path}")

target_old_id = "ORG-001"
target_new_id = "PEOPLE01"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Fix missed tables from migration
    missed_tables = ["hcm_shifts", "hcm_employees"]
    
    print("\n--- Fixing Missed Tables ---")
    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    for table in missed_tables:
        print(f"Checking {table}...")
        try:
            # Check for records with old Organization ID
            cursor.execute(f"SELECT count(*) FROM {table} WHERE organization_id = ?", (target_old_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"  - Found {count} records with old ID. Updating to {target_new_id}...")
                cursor.execute(f"UPDATE {table} SET organization_id = ? WHERE organization_id = ?", (target_new_id, target_old_id))
                print(f"  - Updated.")
            else:
                print(f"  - No records with old ID found.")
                
        except Exception as e:
            print(f"  - Error: {e}")

    # 2. Fix Orphan Designations (Bad Department ID)
    print("\n--- Fixing Orphan Designations ---")
    # Identify designations with invalid department_id
    query_bad_depts = """
        SELECT d.id, d.name, d.department_id 
        FROM hcm_designations d 
        LEFT JOIN core_departments dept ON d.department_id = dept.id
        WHERE d.department_id IS NOT NULL AND dept.id IS NULL
    """
    cursor.execute(query_bad_depts)
    orphans = cursor.fetchall()
    
    if orphans:
        print(f"Found {len(orphans)} designations with invalid Department ID:")
        for o in orphans:
            print(f"  - ID: {o[0]}, Name: {o[1]}, Invalid DeptID: {o[2]}")
        
        # Determine if department_id is nullable
        # Based on schema check, it didn't say NOT NULL, so update to NULL
        print("  -> Setting invalid department_ids to NULL...")
        ids_to_fix = [o[0] for o in orphans]
        placeholders = ','.join('?' * len(ids_to_fix))
        cursor.execute(f"UPDATE hcm_designations SET department_id = NULL WHERE id IN ({placeholders})", ids_to_fix)
        print("  -> Fixed.")
    else:
        print("No orphan designations found.")

    conn.commit()
    
    # 3. Final Integrity Check
    print("\n--- Final Integrity Check ---")
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA foreign_key_check;")
    errors = cursor.fetchall()
    
    if errors:
        print("Integrity Violations Remaining:")
        for error in errors:
            print(error)
    else:
        print("All Integrity Checks Passed!")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
