import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os_dev.db")
print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, code FROM core_organizations")
    orgs = cursor.fetchall()
    
    print(f"\nTotal Organizations: {len(orgs)}")
    for org in orgs:
        print(f"ID: {org[0]}, Name: {org[1]}, Code: {org[2]}")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
