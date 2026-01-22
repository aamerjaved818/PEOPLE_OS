import sqlite3
import os
import sys

# Add backend to path to import models and schemas if needed, 
# but easier to just use sqlite3 for direct check of result.

db_path = r"d:\Project\PEOPLE_OS\backend\data\people_os_dev.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Setup: Ensure an employee exists with LHR01-002
# Check if exists first
cursor.execute("SELECT id FROM hcm_employees WHERE employee_code = 'LHR01-002'")
if not cursor.fetchone():
    print("Pre-inserting LHR01-002 for collision test...")
    cursor.execute("INSERT INTO hcm_employees (id, name, employee_code, organization_id) VALUES ('TEST_COLLISION', 'Collision Test', 'LHR01-002', 'ORG001')")
    conn.commit()

# 2. Setup: Set LHR01 sequence to 0
print("Setting LHR01 sequence to 0...")
cursor.execute("UPDATE core_locations SET current_sequence = 0 WHERE id = 'LHR01'")
conn.commit()

conn.close()

# 3. Call the API/Function (via a small python bridge to crud)
# Since I can't easily call the FastAPI app here with dependencies, 
# I'll just run a python script that imports crud and db.

print("Running crud verification...")
# We'll use a separate script that can import backend modules
