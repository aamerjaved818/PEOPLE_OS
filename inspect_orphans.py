import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os_dev.db")
print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n--- Orphan Sub-Departments ---")
    query = """
    SELECT sd.id, sd.name, sd.code, sd.parent_department_id
    FROM core_sub_departments sd
    """
    cursor.execute(query)
    orphans = cursor.fetchall()
    
    for o in orphans:
        print(f"SubDept: {o[1]} (Code: {o[2]}) | FK: {o[3]}")

    print("\n--- Valid Departments ---")
    cursor.execute("SELECT id, name, code FROM core_departments")
    depts = cursor.fetchall()
    for d in depts:
        print(f"Dept: {d[1]} (ID/Code: {d[0]})")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
