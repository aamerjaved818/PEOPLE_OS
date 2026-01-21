import sqlite3
import os

BACKUP_DB = r'D:\Project\PEOPLE_OS\backend\data\backups\people_os.backup.db'
DEV_DB = r'D:\Project\PEOPLE_OS\backend\data\people_os_dev.db'
TABLE = 'core_organizations'

def get_columns(db_path, table):
    if not os.path.exists(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        cols = cursor.fetchall() # list of tuples (cid, name, type, notnull, dflt_value, pk)
        conn.close()
        return {c[1]: c[2] for c in cols} # name: type
    except Exception as e:
        print(f"Error reading {db_path}: {e}")
        return None

def compare():
    print(f"Comparing table '{TABLE}'...")
    backup_cols = get_columns(BACKUP_DB, TABLE)
    dev_cols = get_columns(DEV_DB, TABLE)
    
    if not backup_cols or not dev_cols:
        print("Could not fetch columns.")
        return

    print(f"Backup Columns ({len(backup_cols)}): {list(backup_cols.keys())}")
    print(f"Dev Columns ({len(dev_cols)}): {list(dev_cols.keys())}")
    
    only_in_backup = set(backup_cols.keys()) - set(dev_cols.keys())
    only_in_dev = set(dev_cols.keys()) - set(backup_cols.keys())
    
    if only_in_backup:
        print(f"\nWARNING: Columns in Backup but NOT in Dev: {only_in_backup}")
    
    if only_in_dev:
        print(f"\nWARNING: Columns in Dev but NOT in Backup: {only_in_dev}")
        
    if not only_in_backup and not only_in_dev:
        print("\nSchemas match perfectly.")

if __name__ == "__main__":
    compare()
