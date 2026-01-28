import sqlite3
import os

DB_PATH = 'backend/data/people_os_dev.db'

def analyze():
    abs_path = os.path.abspath(DB_PATH)
    if not os.path.exists(abs_path):
        print(f"Database not found at {abs_path}")
        return

    print(f"Analyzing: {abs_path}")
    conn = sqlite3.connect(abs_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [t[0] for t in cursor.fetchall()]

    print(f"\nTotal Tables: {len(tables)}")
    print("-" * 40)
    
    row_data = []
    for t in tables:
        try:
            count = cursor.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"{t:<30} | {count}")
            row_data.append((t, count))
        except:
            print(f"{t:<30} | Error")

    print("-" * 40)
    
    # Heuristic for Users
    user_tables = [t for t in tables if 'user' in t.lower() or 'employee' in t.lower()]
    print(f"\nPotential Personnel Tables: {user_tables}")

    conn.close()

if __name__ == "__main__":
    analyze()
