import sqlite3
import os

db_path = 'data/people_os.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- Tables ---")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for t in tables:
    print(f"- {t[0]}")

print("\n--- Users (core_users) ---")
try:
    cursor.execute("SELECT id, username, role, is_system_user FROM core_users;")
    users = cursor.fetchall()
    for u in users:
        print(f"ID: {u[0]}, User: {u[1]}, Role: {u[2]}, System: {u[3]}")
except Exception as e:
    print(f"Error querying core_users: {e}")

conn.close()
