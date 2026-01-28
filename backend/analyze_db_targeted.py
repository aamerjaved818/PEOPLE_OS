import sqlite3
import os

DB_PATH = 'backend/data/people_os_dev.db'

def analyze():
    abs_path = os.path.abspath(DB_PATH)
    if not os.path.exists(abs_path):
        print(f"Database not found at {abs_path}")
        return

    conn = sqlite3.connect(abs_path)
    cursor = conn.cursor()

    tables = ['core_users', 'core_organizations', 'hcm_employees', 'core_audit_logs', 'system_flags']
    
    print("Entity Counts:")
    print("-" * 30)
    for t in tables:
        try:
            count = cursor.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"{t}: {count}")
        except:
            print(f"{t}: Not Found")

    # Check for Root user
    try:
        root = cursor.execute("SELECT username, role, is_active FROM core_users WHERE username='root'").fetchone()
        print(f"\nRoot User: {root if root else 'Not Found'}")
    except:
        print("\nRoot User Check Failed")

    conn.close()

if __name__ == "__main__":
    analyze()
