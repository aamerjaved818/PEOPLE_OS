import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os_dev.db")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    table = "core_sub_departments"
    print(f"\n--- {table} ---")
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
    result = cursor.fetchone()
    if result:
        print(result[0])
    else:
        print(f"Table {table} not found")
            
    conn.close()
except Exception as e:
    print(f"Error: {e}")
