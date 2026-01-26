import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os_dev.db")
print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    # Fix PROD-02 -> PROD
    print("\nFixing PROD-02 (Lot Making)...")
    cursor.execute("UPDATE core_sub_departments SET parent_department_id = 'PROD' WHERE code = 'PROD-02'")
    print(f"Updated {cursor.rowcount} row.")

    conn.commit()

    # Final Integrity Check
    print("\n--- Final Integrity Check ---")
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA foreign_key_check;")
    errors = cursor.fetchall()
    
    if errors:
        print("Integrity Violations Found:")
        for error in errors:
            print(error)
    else:
        print("All Integrity Checks Passed! System is 100% Clean.")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
