import sqlite3
import os

BACKUP_DB = r'D:\Project\PEOPLE_OS\backend\data\backups\people_os.backup.db'
ORG_ID = 'ORG-001'

def inspect_org():
    if not os.path.exists(BACKUP_DB):
        print(f"Backup not found at {BACKUP_DB}")
        return

    try:
        conn = sqlite3.connect(BACKUP_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print(f"Querying for {ORG_ID}...")
        cursor.execute("SELECT * FROM core_organizations WHERE id=?", (ORG_ID,))
        row = cursor.fetchone()
        
        if row:
            print(f"Found Organization: {ORG_ID}")
            for key in row.keys():
                print(f"  {key}: {row[key]}")
        else:
            print(f"Organization {ORG_ID} not found in backup.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    inspect_org()
