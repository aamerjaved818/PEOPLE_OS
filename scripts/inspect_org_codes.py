
import sqlite3

DB_PATH = 'D:/Project/PEOPLE_OS/backend/data/people_os_dev.db'

import sqlite3

DB_PATH = 'D:/Project/PEOPLE_OS/backend/data/people_os_dev.db'

def inspect_dates():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        print("--- core_locations (Plants) ---")
        cursor.execute("SELECT id, created_at, updated_at FROM core_locations")
        rows = cursor.fetchall()
        print(f"{'ID':<10} {'CREATED_AT':<30} {'UPDATED_AT'}")
        print("-" * 70)
        for row in rows:
            print(f"{row[0]:<10} {str(row[1]):<30} {str(row[2])}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_dates()

if __name__ == "__main__":
    inspect_dates()
