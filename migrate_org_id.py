import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os_dev.db")
print(f"Connecting to database at: {db_path}")

target_old_id = "ORG-001"
target_new_id = "PEOPLE01"

tables_to_update = [
    "core_users",
    "core_locations",
    "core_departments",
    "core_sub_departments",
    "hcm_job_levels",
    "hcm_grades",
    "hcm_designations",
    # "payroll_settings" # Verify if this table exists and has organization_id
]

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if target ID already exists
    cursor.execute("SELECT count(*) FROM core_organizations WHERE id = ?", (target_new_id,))
    if cursor.fetchone()[0] > 0:
        print(f"Target ID {target_new_id} already exists! Aborting to prevent duplicates.")
        conn.close()
        exit(1)

    # Check if old ID exists
    cursor.execute("SELECT count(*) FROM core_organizations WHERE id = ?", (target_old_id,))
    if cursor.fetchone()[0] == 0:
        print(f"Source ID {target_old_id} not found! Nothing to migrate.")
        conn.close()
        exit(0)

    print(f"Migrating {target_old_id} -> {target_new_id}...")

    # Disable Foreign Keys
    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    try:
        conn.execute("BEGIN TRANSACTION;")

        # 1. Update Parent Organization
        print(f"Updating core_organizations...")
        cursor.execute("UPDATE core_organizations SET id = ? WHERE id = ?", (target_new_id, target_old_id))
        
        # 2. Update Children Tables
        for table in tables_to_update:
            print(f"Updating {table}...")
            try:
                # Check if table has organization_id column before updating
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [info[1] for info in cursor.fetchall()]
                if "organization_id" in columns:
                    cursor.execute(f"UPDATE {table} SET organization_id = ? WHERE organization_id = ?", (target_new_id, target_old_id))
                    print(f"  - Updated {cursor.rowcount} rows.")
                else:
                    print(f"  - Skipped (no organization_id column).")
            except sqlite3.OperationalError as e:
                 print(f"  - Skipped (Table might not exist: {e})")

        # 3. Special check for payroll_settings if not in loop
        # (Included in loop logic with generic check)

        conn.commit()
        print("Transaction committed.")

    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        print("Transaction rolled back.")

    finally:
        # Re-enable Foreign Keys
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Check Integrity
        print("\nChecking foreign key integrity...")
        cursor.execute("PRAGMA foreign_key_check;")
        errors = cursor.fetchall()
        if errors:
            print("Foreign Key Integrity Violations found:")
            for error in errors:
                print(error)
        else:
            print("Integrity check passed.")

    conn.close()

except Exception as e:
    print(f"Database connection error: {e}")
