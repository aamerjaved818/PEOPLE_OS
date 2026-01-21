import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os_dev.db")
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
row = cursor.execute("SELECT id, username, role FROM core_users WHERE username='.amer'").fetchone()

if row:
    print(f"User .amer FOUND: ID={row[0]}, Role={row[2]}")
else:
    print("User .amer NOT FOUND")
conn.close()
