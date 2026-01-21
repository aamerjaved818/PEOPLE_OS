import sqlite3
import os

# Connect to the database
db_path = os.path.join("backend", "data", "people_os_dev.db")
print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get the main organization ID
    cursor.execute("SELECT id, name FROM core_organizations")
    orgs = cursor.fetchall()
    
    if not orgs:
        print("No organizations found! Cannot fix orphans.")
        exit(1)

    main_org_id = orgs[0][0]
    print(f"Target Organization ID: {main_org_id} ({orgs[0][1]})")

    tables_to_fix = [
        "hcm_job_levels",
        "hcm_grades",
        "hcm_designations"
    ]

    for table in tables_to_fix:
        print(f"\n--- Fixing {table} ---")
        try:
            # Count orphans before fix
            query_invalid_count = f"SELECT count(*) FROM {table} WHERE organization_id != ?"
            cursor.execute(query_invalid_count, (main_org_id,))
            before_count = cursor.fetchone()[0]
            print(f"Orphans found: {before_count}")

            if before_count > 0:
                # Update invalid records to point to main_org_id
                query_update = f"UPDATE {table} SET organization_id = ? WHERE organization_id != ?"
                cursor.execute(query_update, (main_org_id, main_org_id))
                conn.commit()
                print(f"Updated {before_count} records.")
            else:
                print("No orphans to fix.")
                
        except Exception as e:
            print(f"Error fixing {table}: {e}")

    conn.close()
    print("\nOrphan fix complete.")

except Exception as e:
    print(f"Database connection error: {e}")
