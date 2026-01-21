import sqlite3
import os

DB_PATH = "backend/data/people_os_dev.db"

def check_orgs():
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print(f"Absolute Path: {os.path.abspath(DB_PATH)}")
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Tables in DB:", [t[0] for t in tables])

        # Count organizations
        cursor.execute("SELECT count(*) FROM core_organizations")
        count = cursor.fetchone()[0]
        print(f"Total organizations in DB: {count}")

        # Try inserting a dummy org
        try:
            print("Attempting to insert dummy org...")
            cursor.execute("INSERT INTO core_organizations (id, name, code, is_active) VALUES ('ORG-DUMMY', 'Dummy Org', 'DUMMY', 1)")
            conn.commit()
            print("Insert successful.")
        except Exception as e:
            print(f"Insert failed: {e}")

        # Count again
        cursor.execute("SELECT count(*) FROM core_organizations")
        count = cursor.fetchone()[0]
        print(f"Total organizations in DB after insert: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, name, code, is_active FROM core_organizations")
            rows = cursor.fetchall()
            print("Organizations:")
            for row in rows:
                print(row)
        else:
            print("No organizations found in table core_organizations.")
            
        conn.close()
    except Exception as e:
        print(f"Error accessing DB: {e}")

if __name__ == "__main__":
    check_orgs()
