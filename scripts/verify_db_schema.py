import sqlite3
import os

db_path = "backend/data/people_os_dev.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

tables = [
    "hcm_payroll_ledger", "hcm_attendance", "hcm_leave_balances", "hcm_leave_requests",
    "hcm_employee_education", "hcm_employee_experience", "hcm_employee_family", 
    "hcm_employee_discipline", "hcm_employee_increments"
]

for table in tables:
    print(f"\n--- Schema for {table} ---")
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}';")
    result = cursor.fetchone()
    if result:
        print(result[0])
    else:
        print("Table not found.")

conn.close()
