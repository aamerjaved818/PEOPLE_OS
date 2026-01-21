import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os_dev.db")
print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Disable FKs to allow update
    cursor.execute("PRAGMA foreign_keys = OFF;")

    print("\n--- Fixing Employee Orphans ---")
    # We know RowIDs 1 and 2 are problematic.
    # We will set plant_id and department_id to NULL for these rows.
    # Note: Using RowID is safe for this specific cleanup on a small dev DB.
    
    cursor.execute("UPDATE hcm_employees SET plant_id = NULL, department_id = NULL WHERE rowid IN (1, 2)")
    print(f"Updated {cursor.rowcount} employee records (set plant/dept to NULL).")
    
    conn.commit()

    # Final Check
    print("\n--- Final Integrity Check ---")
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA foreign_key_check;")
    errors = cursor.fetchall()
    
    if errors:
        print("Integrity Violations Remaining:")
        for error in errors:
            print(error)
    else:
        print("All Integrity Checks Passed! Database is 100% Clean.")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
