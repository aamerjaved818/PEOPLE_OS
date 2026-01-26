import sqlite3
import os

DEV_DB = r"backend\data\people_os_dev.db"
BACKUP_DB = r"backend\data\backups\people_os.backup.db"

def restore_departments():
    if not os.path.exists(DEV_DB) or not os.path.exists(BACKUP_DB):
        print("Database file missing.")
        return

    conn = sqlite3.connect(DEV_DB)
    cursor = conn.cursor()
    
    # Attach backup DB
    cursor.execute(f"ATTACH DATABASE '{BACKUP_DB}' AS backup")
    
    # Target columns (excluding plant_id)
    columns = [
        "id", "code", "name", "isActive", "organization_id", 
        "hod_id", "manager_id", "created_at", "updated_at", 
        "created_by", "updated_by"
    ]
    col_str = ", ".join(columns)
    
    print("Restoring core_departments...")
    try:
        # Insert data mapping columns explicitly
        cursor.execute(f"""
            INSERT OR IGNORE INTO core_departments ({col_str})
            SELECT {col_str} FROM backup.core_departments
        """)
        conn.commit()
        
        # Verify restoration
        new_count = cursor.execute(f"SELECT COUNT(*) FROM core_departments").fetchone()[0]
        print(f"  [SUCCESS] core_departments now has {new_count} rows.")
            
    except Exception as e:
        print(f"  [ERROR] core_departments: {e}")

    conn.close()

if __name__ == "__main__":
    restore_departments()
