import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os_dev.db")
print(f"Connecting to database at: {db_path}")

# Manual mapping based on output
# SubDept Code -> Parent Dept Code (which is now Parent ID)
mapping = {
    "ADMIN-01": "ADMIN",  # Admin Support -> Administration
    "ADMIN-02": "ADMIN",  # Gate Office -> Administration
    "ADMIN-03": "ADMIN",  # Kitchen -> Administration
    "HR-01": "HR",        # HR Operations -> Human Resources
    "HR-02": "HR",        # Recruitment -> Human Resources
    "SALE-01": "SALE",    # Sales Operations -> Sales
    "PROD-01": "PROD",    # Cutting -> Production
    "PROD-03": "PROD",    # Flat Knitting -> Production
    "QUAL-01": "QUAL",    # Stitching Quality -> Quality
}

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = OFF;")
    conn.execute("BEGIN TRANSACTION;")

    print("\n--- Repairing Sub-Departments FKs ---")
    for sd_code, parent_code in mapping.items():
        print(f"Linking SubDept {sd_code} -> Parent {parent_code}...")
        cursor.execute("UPDATE core_sub_departments SET parent_department_id = ? WHERE code = ?", (parent_code, sd_code))

    print("\n--- Migrating Sub-Departments IDs (Code -> ID) ---")
    # Now migrate standard Sub-Dept IDs if not done
    cursor.execute("SELECT id, code, name FROM core_sub_departments")
    rows = cursor.fetchall()
    for row in rows:
        old_id = row[0]
        code = row[1]
        name = row[2]
        
        if code and old_id != code:
            new_id = code.strip().upper()
            print(f"Migrating SubDept: {name} | {old_id} -> {new_id}")
            
            # Check collision
            cursor.execute("SELECT count(*) FROM core_sub_departments WHERE id = ?", (new_id,))
            if cursor.fetchone()[0] == 0:
                 cursor.execute("UPDATE core_sub_departments SET id = ? WHERE id = ?", (new_id, old_id))
                 
                 # Update dependents (hcm_employees)
                 cursor.execute("UPDATE hcm_employees SET sub_department_id = ? WHERE sub_department_id = ?", (new_id, old_id))
            else:
                 print(f"  [SKIP] Target ID {new_id} already exists.")

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
         print("All Integrity Checks Passed!")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
    if conn:
        conn.rollback()
