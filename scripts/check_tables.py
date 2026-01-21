import sqlite3
import os

DB_PATH = r'D:\Project\PEOPLE_OS\backend\data\people_os_dev.db'

def check_tables():
    if not os.path.exists(DB_PATH):
        print(f"DB not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables in {DB_PATH}:")
    for table in tables:
        print(f" - {table[0]}")
        
    # Check specifically for job related tables
    print("\nJob Level related tables:")
    for table in tables:
        if 'job' in table[0].lower() or 'level' in table[0].lower():
             print(f" -> {table[0]}")
             # Count rows
             try:
                 cursor.execute(f"SELECT count(*) FROM {table[0]}")
                 count = cursor.fetchone()[0]
                 print(f"    Rows: {count}")
             except:
                 print("    (Could not count rows)")

    conn.close()

if __name__ == "__main__":
    check_tables()
