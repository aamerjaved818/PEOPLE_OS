import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os_dev.db")
print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"\n--- Job Levels Organization Link Check ---")
    cursor.execute("SELECT id, name, code, organization_id FROM hcm_job_levels")
    rows = cursor.fetchall()
    
    print(f"{'ID':<10} | {'Name':<20} | {'Org ID':<15}")
    print("-" * 50)
    for row in rows:
        print(f"{row[0]:<10} | {row[1]:<20} | {row[3]}")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
