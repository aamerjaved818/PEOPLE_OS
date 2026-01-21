
import sqlite3

BACKUP_DB = 'D:/Project/PEOPLE_OS/backend/data/backups/people_os.backup.db'

try:
    conn = sqlite3.connect(BACKUP_DB)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(hcm_job_levels);")
    columns = cursor.fetchall()
    print("Columns in hcm_job_levels:")
    for col in columns:
        print(col)
    conn.close()
except Exception as e:
    print(f"Error: {e}")

if __name__ == "__main__":
    list_tables()
