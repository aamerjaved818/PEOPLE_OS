import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os_dev.db")
print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Check Schema of hcm_job_levels and hcm_grades (main dependent)
    tables = ["hcm_job_levels", "hcm_grades"]
    for table in tables:
        print(f"\n--- Schema: {table} ---")
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        result = cursor.fetchone()
        if result:
            print(result[0])
        else:
            print(f"Table {table} not found")

    # 2. Check Data in hcm_job_levels
    print(f"\n--- Data: hcm_job_levels ---")
    cursor.execute("SELECT id, name, code FROM hcm_job_levels")
    rows = cursor.fetchall()
    print(f"{'ID':<30} | {'Name':<20} | {'Code':<10}")
    print("-" * 65)
    for row in rows:
        print(f"{row[0]:<30} | {row[1]:<20} | {row[2]}")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
