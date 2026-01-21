import sqlite3
import os

DB_PATH = r"backend\data\people_os_dev.db"

def check_table():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='core_role_permissions'")
        result = cursor.fetchone()
        
        if result:
            print("✅ Table 'core_role_permissions' exists.")
            
            # Check columns
            cursor.execute("PRAGMA table_info(core_role_permissions)")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"Columns: {columns}")
        else:
            print("❌ Table 'core_role_permissions' NOT FOUND.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_table()
