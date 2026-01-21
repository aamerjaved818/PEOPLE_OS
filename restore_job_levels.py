import sqlite3
import os

DATABASES = {
    "dev": r"backend\data\people_os_dev.db",
    "prod": r"backend\data\people_os_prod.db",
    "test": r"backend\data\people_os_test.db"
}
BACKUP_DB = r"backend\data\backups\people_os.backup.db"

def restore_job_levels():
    if not os.path.exists(BACKUP_DB):
        print("Backup DB missing!")
        return

    for env, path in DATABASES.items():
        if not os.path.exists(path):
            print(f"[{env.upper()}] DB missing at {path}. Skipping.")
            continue

        print(f"\n[{env.upper()}] Restoring to {path}...")
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        cursor.execute(f"ATTACH DATABASE '{BACKUP_DB}' AS backup")
        
        tables = ['hcm_job_levels', 'core_locations']
        
        for table in tables:
            try:
                # Insert data (Ignore duplicates)
                cursor.execute(f"INSERT OR IGNORE INTO {table} SELECT * FROM backup.{table}")
                conn.commit()
                
                # Check row count
                count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                print(f"  + {table}: {count} rows.")
                
            except Exception as e:
                print(f"  - {table} Error: {e}")

        conn.close()

if __name__ == "__main__":
    restore_job_levels()
