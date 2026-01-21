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

    def migrate_table(table_name, id_col, code_col, dependents):
        print(f"\nScanning {table_name}...")
        cursor.execute(f"SELECT {id_col}, {code_col}, name FROM {table_name}")
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
            cursor.execute(f"SELECT count(*) FROM {table_name} WHERE {id_col} = ?", (new_id,))
            if cursor.fetchone()[0] > 0:
                 print(f"  [ERROR] Collision: Target ID {new_id} already exists! Cannot migrate {name} ({old_id}).")
                 continue

            print(f"  Migrating: {name} | {old_id} -> {new_id}")
            
            # 1. Update the record itself
            cursor.execute(f"UPDATE {table_name} SET {id_col} = ? WHERE {id_col} = ?", (new_id, old_id))
            
            # 2. Update dependents
            for dep_table, dep_col in dependents:
                try:
                    # Check if column exists first
                    cursor.execute(f"PRAGMA table_info({dep_table})")
                    cols = [c[1] for c in cursor.fetchall()]
                    if dep_col in cols:
                        cursor.execute(f"UPDATE {dep_table} SET {dep_col} = ? WHERE {dep_col} = ?", (new_id, old_id))
                        if cursor.rowcount > 0:
                            print(f"    -> Updated {cursor.rowcount} rows in {dep_table}.{dep_col}")
                except Exception as e:
                    print(f"    [WARN] Failed to update dependent {dep_table}: {e}")
            
            updates_count += 1
            
        print(f"  Finished {table_name}: {updates_count} updates processed.")

    # --- 1. Migrate Plants (core_locations) ---
    # Dependencies: core_departments(plant_id), hcm_employees(plant_id)
    migrate_table(
        "core_locations", 
        "id", 
        "code", 
        [("core_departments", "plant_id"), ("hcm_employees", "plant_id")]
    )

    # --- 2. Migrate Departments (core_departments) ---
    # Dependencies: 
    #   core_sub_departments(parentDepartmentId), - Note: ensure column name is correct
    #   hcm_designations(department_id),
    #   hcm_employees(department_id),
    #   hcm_job_vacancies(department) - Note: schema check showed 'department' as simple text or FK? We will check.
    migrate_table(
        "core_departments", 
        "id", 
        "code", 
        [
            ("core_sub_departments", "parentDepartmentId"), # Verify case/name?
            ("hcm_designations", "department_id"),
            ("hcm_employees", "department_id"),
            ("hcm_job_vacancies", "department") # Needs verification if this is ID linkage
        ]
    )

    # --- 3. Migrate Sub-Departments (core_sub_departments) ---
    # Dependencies: hcm_employees(sub_department_id)
    migrate_table(
        "core_sub_departments", 
        "id", 
        "code", 
        [("hcm_employees", "sub_department_id")]
    )

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
