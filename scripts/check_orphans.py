import sqlite3
import pandas as pd
import os

# Connect to the database
db_path = os.path.join("backend", "data", "people_os_dev.db")
print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get the main organization ID
    cursor.execute("SELECT id, name, code FROM core_organizations")
    orgs = cursor.fetchall()
    print("\n--- Organizations ---")
    for org in orgs:
        print(f"ID: {org[0]}, Name: {org[1]}, Code: {org[2]}")
    
    main_org_id = orgs[0][0] if orgs else None

    tables_to_check = [
        "core_departments",
        "core_sub_departments",
        "hcm_job_levels",
        "hcm_grades",
        "hcm_designations"
    ]

    for table in tables_to_check:
        print(f"\n--- {table} ---")
        try:
            # Check for records with NULL organization_id
            query_null = f"SELECT count(*) FROM {table} WHERE organization_id IS NULL"
            cursor.execute(query_null)
            null_count = cursor.fetchone()[0]
            
            # Check for records with organization_id not in the org list
            if main_org_id:
                query_invalid = f"SELECT count(*) FROM {table} WHERE organization_id IS NOT NULL AND organization_id != ?"
                cursor.execute(query_invalid, (main_org_id,))
                invalid_count = cursor.fetchone()[0]
            else:
                invalid_count = 0

            print(f"Total Records: {pd.read_sql_query(f'SELECT count(*) FROM {table}', conn).iloc[0,0]}")
            print(f"Orphan (NULL org_id): {null_count}")
            print(f"Orphan (Invalid org_id): {invalid_count}")
            
            # Show a few examples if orphans exist
            if null_count > 0:
                print("Example Orphans (NULL org_id):")
                print(pd.read_sql_query(f"SELECT * FROM {table} WHERE organization_id IS NULL LIMIT 3", conn))
                
        except Exception as e:
            print(f"Error checking {table}: {e}")

    conn.close()

except Exception as e:
    print(f"Database connection error: {e}")
