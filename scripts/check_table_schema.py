import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os_dev.db")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='core_departments'")
    result = cursor.fetchone()
    if result:
        print(result[0])
    else:
        print("Table core_departments not found")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
