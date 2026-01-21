import sqlite3
import os

BACKUP_PATH = r'D:\Project\PEOPLE_OS\backend\data\backups\people_os.backup.db'

print(f"Inspecting backup: {BACKUP_PATH}")
if not os.path.exists(BACKUP_PATH):
    print("Backup NOT FOUND")
    exit(1)

conn = sqlite3.connect(BACKUP_PATH)
cursor = conn.cursor()

try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables in backup:", tables)

    for table in tables:
        if 'job' in table[0].lower() or 'level' in table[0].lower():
            print(f"Possible Match: {table[0]}")
            cursor.execute(f"SELECT * FROM {table[0]}")
            print(f"Data in {table[0]}:")
            for row in cursor.fetchall():
                print(row)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='job_levels'")
    if not cursor.fetchone():
        print("Table 'job_levels' MISSING in backup")
    else:
        cursor.execute("SELECT count(*) FROM job_levels")
        count = cursor.fetchone()[0]
        print(f"Job Levels Count: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM job_levels LIMIT 5")
            print("Sample Data:")
            for row in cursor.fetchall():
                print(row)
                
    # Check Orgs in Backup
    cursor.execute("SELECT * FROM core_organizations")
    print("\nOrganizations in Backup:")
    for row in cursor.fetchall():
        print(row)
        
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
