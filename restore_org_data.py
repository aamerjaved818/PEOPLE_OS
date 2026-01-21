import sqlite3
import os

DEV_DB = r"backend\data\people_os_dev.db"
BACKUP_DB = r"backend\data\backups\people_os.backup.db"

def restore_data():
    if not os.path.exists(DEV_DB) or not os.path.exists(BACKUP_DB):
        print("Database file missing.")
        return

    conn = sqlite3.connect(DEV_DB)
    cursor = conn.cursor()
    
    # Attach backup DB
    cursor.execute(f"ATTACH DATABASE '{BACKUP_DB}' AS backup")
    
    tables = ['core_locations', 'core_departments', 'hcm_designations']
    
    print("Restoring organization data...")
    
    for table in tables:
        try:
            # Check if source table exists
            backup_count = cursor.execute(f"SELECT COUNT(*) FROM backup.{table}").fetchone()[0]
            if backup_count == 0:
                print(f"  [SKIP] {table} is empty in backup.")
                continue

            print(f"  Restoring {table} ({backup_count} rows)...")
            
            # Insert data (Ignore duplicates if any)
            cursor.execute(f"INSERT OR IGNORE INTO {table} SELECT * FROM backup.{table}")
            conn.commit()
            
            # Verify restoration
            new_count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  [SUCCESS] {table} now has {new_count} rows.")
            
        except sqlite3.OperationalError as e:
            print(f"  [ERROR] {table}: {e}")
        except Exception as e:
            print(f"  [ERROR] {table}: {e}")

    conn.close()
    print("Restoration complete.")

if __name__ == "__main__":
    restore_data()
