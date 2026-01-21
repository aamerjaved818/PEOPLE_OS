import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os_dev.db")
print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = ["core_locations", "core_departments", "core_sub_departments"]
    
    for table in tables:
        print(f"\n--- {table} ---")
        try:
            cursor.execute(f"SELECT id, name, code FROM {table}")
            rows = cursor.fetchall()
            print(f"Total records: {len(rows)}")
            print(f"{'ID':<20} | {'Name':<30} | {'Code':<15}")
            print("-" * 70)
            for row in rows:
                print(f"{row[0]:<20} | {row[1]:<30} | {row[2]}")
        except Exception as e:
            print(f"Error reading {table}: {e}")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
