import sqlite3
import os

db_path = r"d:/Project/PEOPLE_OS/backend/data/people_os_dev.db"

def check_schema():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(hcm_employees)")
        columns = cursor.fetchall()
        print("Columns in hcm_employees:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_schema()
