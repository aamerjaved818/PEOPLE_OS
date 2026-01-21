import sqlite3
import os

DB_PATH = r'D:\Project\PEOPLE_OS\backend\data\people_os_dev.db'

if not os.path.exists(DB_PATH):
    print(f"Database not found at {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='job_levels'")
    if not cursor.fetchone():
        print("Table 'job_levels' does not exist!")
    else:
        cursor.execute("SELECT count(*) FROM job_levels")
        count = cursor.fetchone()[0]
        print(f"Row count in 'job_levels': {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM job_levels LIMIT 5")
            print("Sample data:", cursor.fetchall())
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
