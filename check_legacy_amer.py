import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os.db")
if not os.path.exists(db_path):
    print(f"Legacy DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
try:
    row = cursor.execute("SELECT id, username, role, password_hash, name, email, is_active, is_system_user, organization_id FROM core_users WHERE username='.amer'").fetchone()

    if row:
        print(f"User .amer FOUND in LEGACY: ID={row[0]}")
        # Print update SQL to help migration
        print("MIGRATION DATA:")
        print(row)
    else:
        print("User .amer NOT FOUND in LEGACY")
except Exception as e:
    print(f"Error reading legacy DB: {e}")
conn.close()
