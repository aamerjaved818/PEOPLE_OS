
import sqlite3
import os

DB_PATH = 'D:/Project/PEOPLE_OS/backend/data/people_os_dev.db'

def inspect_job_levels():
    if not os.path.exists(DB_PATH):
        print("dev db not found")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, code FROM hcm_job_levels")
        rows = cursor.fetchall()
        print(f"Total Job Levels in Dev: {len(rows)}")
        print(f"{'ID':<36} {'CODE':<10} {'NAME'}")
        print("-" * 70)
        for row in rows:
            print(f"{row[0]:<36} {str(row[2]):<10} {row[1]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_job_levels()
