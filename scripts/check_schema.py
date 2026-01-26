import sqlite3

DEV_DB = r"backend\data\people_os_dev.db"
BACKUP_DB = r"backend\data\backups\people_os.backup.db"

def check_schema():
    conn_dev = sqlite3.connect(DEV_DB)
    curr_dev = conn_dev.cursor()
    dev_cols = [date[1] for date in curr_dev.execute("PRAGMA table_info(core_departments)").fetchall()]
    conn_dev.close()
    
    conn_bak = sqlite3.connect(BACKUP_DB)
    curr_bak = conn_bak.cursor()
    bak_cols = [date[1] for date in curr_bak.execute("PRAGMA table_info(core_departments)").fetchall()]
    conn_bak.close()
    
    print(f"Dev  Columns ({len(dev_cols)}): {dev_cols}")
    print(f"Backup Columns ({len(bak_cols)}): {bak_cols}")
    
    # Find difference
    extra_in_backup = set(bak_cols) - set(dev_cols)
    missing_in_backup = set(dev_cols) - set(bak_cols)
    
    if extra_in_backup:
        print(f"Extra in Backup: {extra_in_backup}")
    if missing_in_backup:
        print(f"Missing in Backup: {missing_in_backup}")

if __name__ == "__main__":
    check_schema()
