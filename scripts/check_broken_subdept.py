import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os_dev.db")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check rowid 7 directly
    cursor.execute("SELECT rowid, id, name, code, parent_department_id FROM core_sub_departments WHERE rowid = 7")
    row = cursor.fetchone()
    print(f"\nRowID 7: {row}")
    
    # Check if parent exists
    if row:
        parent_id = row[4]
        cursor.execute("SELECT id FROM core_departments WHERE id = ?", (parent_id,))
        layout = cursor.fetchone()
        if not layout:
             print(f"Parent ID '{parent_id}' NOT FOUND in core_departments.")
        else:
             print(f"Parent ID '{parent_id}' exists.")

    conn.close()
except Exception as e:
    print(f"Error: {e}")
