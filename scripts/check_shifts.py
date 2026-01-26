import sqlite3
import os

BACKUP_DB = r"backend\data\backups\people_os.backup.db"

def check_backup():
    if not os.path.exists(BACKUP_DB):
        print(f"Backup DB not found at {BACKUP_DB}")
        return

    conn = sqlite3.connect(BACKUP_DB)
    cursor = conn.cursor()
    
    table = 'hcm_shifts'
    
    print(f"Checking backup: {BACKUP_DB}")
    try:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count} rows")
    except sqlite3.OperationalError:
        print(f"  {table}: TABLE NOT FOUND")
    except Exception as e:
        print(f"  {table}: Error - {e}")
            
    conn.close()

if __name__ == "__main__":
    check_backup()
