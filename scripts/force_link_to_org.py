import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os_dev.db")
print(f"Connecting to database at: {db_path}")

target_new_id = "PEOPLE01"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables_to_force = [
        "hcm_shifts",
        "hcm_employees",
        "payroll_settings"
    ]
    
    print(f"\nTarget Organization ID: {target_new_id}")
    print("Forcing all records in the following tables to link to this Org:")
    
    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    for table in tables_to_force:
        print(f"\n--- {table} ---")
        try:
            cursor.execute(f"SELECT count(*) FROM {table}")
            total = cursor.fetchone()[0]
            print(f"  Total records: {total}")
            
            if total > 0:
                cursor.execute(f"UPDATE {table} SET organization_id = ?", (target_new_id,))
                print(f"  -> Updated {cursor.rowcount} records to {target_new_id}.")
            else:
                print("  -> Table empty.")
                
        except Exception as e:
            print(f"  Error: {e}")

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
        print("All Integrity Checks Passed! System is Clean.")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
