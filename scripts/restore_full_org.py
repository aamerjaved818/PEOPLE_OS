import sqlite3
import os
import time

BACKUP_DB = r'D:\Project\PEOPLE_OS\backend\data\backups\people_os.backup.db'
TARGET_DBS = [
    r'D:\Project\PEOPLE_OS\backend\data\people_os_dev.db',
    # r'D:\Project\PEOPLE_OS\backend\data\people_os_test.db',
    # r'D:\Project\PEOPLE_OS\backend\data\people_os_prod.db'
]

TARGET_ORG_ID = 'ORG-001'

# Tables to restore in order of dependency (Parents first)
# Tuple format: (Table Name, Filter Column)
# For core_organizations, we filter by 'id'. For others, by 'organization_id'.
TABLES_TO_RESTORE = [
    ('core_organizations', 'id'),
    ('core_locations', 'organization_id'),
    ('core_departments', 'organization_id'),
    ('core_sub_departments', 'organization_id'),
    ('core_divisions', 'organization_id'),
    ('hcm_job_levels', 'organization_id'),
    ('hcm_grades', 'organization_id'),
    ('hcm_designations', 'organization_id'),
    ('hcm_shifts', 'organization_id'),
    ('hcm_holidays', 'organization_id'),
    ('hcm_banks', 'organization_id'),
    ('hcm_job_vacancies', 'organization_id'),
    ('hcm_positions', 'organization_id')
]

def get_backup_data(table_name, filter_col):
    if not os.path.exists(BACKUP_DB):
        print(f"Backup DB not found: {BACKUP_DB}")
        return None, None
    
    conn = sqlite3.connect(BACKUP_DB)
    cursor = conn.cursor()
    
    try:
        # Check if table exists in backup
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            print(f"  [Backup] Table '{table_name}' not found. Skipping.")
            return [], []

        print(f"  [Backup] Reading '{table_name}' for {TARGET_ORG_ID}...")
        cursor.execute(f"SELECT * FROM {table_name} WHERE {filter_col}=?", (TARGET_ORG_ID,))
        data = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"    -> Found {len(data)} rows.")
        return data, columns
    except Exception as e:
        print(f"    -> Error reading backup: {e}")
        return None, None
    finally:
        conn.close()

# Column Mappings (Backup Column -> Target Column)
COLUMN_MAPPINGS = {
    'core_organizations': {
        'tax_id': 'tax_identifier'
    }
}

def get_target_columns(cursor, table_name):
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        return {col[1] for col in cursor.fetchall()}
    except:
        return set()

def restore_table(cursor, table_name, filter_col, data, source_columns):
    if not data:
        return

    # 1. Clear existing data for target org
    try:
        cursor.execute(f"DELETE FROM {table_name} WHERE {filter_col}=?", (TARGET_ORG_ID,))
        print(f"    -> Cleared {cursor.rowcount} existing rows from '{table_name}'.")
    except sqlite3.OperationalError as e:
        print(f"    -> Warning: Could not clear '{table_name}': {e}. Table might not exist in target.")
        return

    # 2. Map Columns
    target_cols = get_target_columns(cursor, table_name)
    if not target_cols:
        print(f"    -> Error: Could not fetch schema for target table '{table_name}'.")
        return

    final_columns = []
    final_indices = []
    mappings = COLUMN_MAPPINGS.get(table_name, {})

    for idx, col in enumerate(source_columns):
        target_col = mappings.get(col, col)
        if target_col in target_cols:
            final_columns.append(target_col)
            final_indices.append(idx)
        else:
            # print(f"    -> Skipping column '{col}' (mapped to '{target_col}') as it does not exist in target.")
            pass
            
    if not final_columns:
        print(f"    -> Error: No matching columns found for '{table_name}'.")
        return

    # 3. Prepare Data
    filtered_data = []
    for row in data:
        new_row = [row[i] for i in final_indices]
        filtered_data.append(tuple(new_row))

    # 4. Insert data
    placeholders = ', '.join(['?'] * len(final_columns))
    col_names = ', '.join(final_columns)
    query = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"
    
    try:
        cursor.executemany(query, filtered_data)
        print(f"    -> Inserted {cursor.rowcount} rows into '{table_name}'.")
    except Exception as e:
        print(f"    -> Error inserting into '{table_name}': {e}")

def process_target_db(db_path, restoration_data):
    print(f"\nProcessing Target: {db_path}")
    if not os.path.exists(db_path):
        print("  -> DB file not found. Skipping.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # We process tables in order
        for table_name, filter_col in TABLES_TO_RESTORE:
            if table_name in restoration_data:
                rows, cols = restoration_data[table_name]
                if rows and cols:
                    restore_table(cursor, table_name, filter_col, rows, cols)
        
        conn.commit()
        print("  -> Commit successful.")
        
    except Exception as e:
        print(f"  -> Critical Error during restoration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print(f"Starting Full Restoration for Organization: {TARGET_ORG_ID}")
    
    # 1. Fetch all data from backup first
    restoration_payload = {}
    for table, filter_col in TABLES_TO_RESTORE:
        rows, cols = get_backup_data(table, filter_col)
        if rows is not None:
            restoration_payload[table] = (rows, cols)
            
    # 2. Apply to all targets
    for db in TARGET_DBS:
        process_target_db(db, restoration_payload)
        
    print("\nRestoration Complete.")
