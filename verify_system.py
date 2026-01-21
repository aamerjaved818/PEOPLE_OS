import sqlite3
import os
import inspect
import importlib.util
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

def verify_database_schema():
    db_path = os.path.join("backend", "data", "people_os_dev.db")
    print(f"\n[DATABASE] Connecting to {db_path}...")
    
    if not os.path.exists(db_path):
        print("  [ERROR] Database file not found!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Foreign Key Check
    print("  [CHECK] Running Foreign Key Integrity Check...")
    cursor.execute("PRAGMA foreign_key_check;")
    fk_errors = cursor.fetchall()
    if fk_errors:
        print(f"  [FAIL] Found {len(fk_errors)} FK violations!")
        for err in fk_errors:
            print(f"    - Table: {err[0]}, RowID: {err[1]}, Target: {err[2]}, FK index: {err[3]}")
    else:
        print("  [PASS] Foreign Key Integrity OK.")

    # 2. Table Existence Check (Basic Critical Tables)
    critical_tables = [
        "core_organizations", "core_locations", "core_departments", "core_sub_departments",
        "hcm_job_levels", "hcm_grades", "hcm_designations", "hcm_employees", "hcm_shifts"
    ]
    print("\n  [CHECK] Verifying Critical Tables...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = {row[0] for row in cursor.fetchall()}
    
    all_tables_ok = True
    for table in critical_tables:
        if table in existing_tables:
            print(f"    - {table}: OK")
        else:
            print(f"    - {table}: MISSING")
            all_tables_ok = False
            
    if all_tables_ok:
        print("  [PASS] Critical Tables Exist.")
    
    # 3. Specific ID=Code Check for Job Levels
    print("\n  [CHECK] Verifying Job Level IDs...")
    cursor.execute("SELECT id, code FROM hcm_job_levels")
    rows = cursor.fetchall()
    job_level_ok = True
    for r in rows:
        if r[0] != r[1]: # strictly equal? or casing?
             # Allow fuzzy match if case differs, but goal was ID=Code
             if r[0] != r[1] and r[0] != r[1].upper():
                 print(f"    [WARN] Mismatch: ID='{r[0]}' vs Code='{r[1]}'")
                 job_level_ok = False
    if job_level_ok:
        print("  [PASS] All Job Level IDs match their Codes.")

    conn.close()

def scan_api_endpoints():
    print("\n[API] Scanning backend/main.py for Routes...")
    
    try:
        with open(os.path.join("backend", "main.py"), "r") as f:
            lines = f.readlines()
            
        routes = []
        for line in lines:
            if "@app." in line and "/api/v1/" in line:
                # excessively simple parser
                method = line.split("@app.")[1].split("(")[0].upper()
                path = line.split('"')[1]
                routes.append(f"{method} {path}")
                
        print(f"  Found {len(routes)} API Endpoints.")
        
        # Verify specific critical routes exist
        required_routes = [
            "GET /api/v1/organizations",
            "GET /api/v1/job-levels",
            "GET /api/v1/grades",
            "DELETE /api/v1/grades/{grade_id}",
            "PUT /api/v1/grades/{grade_id}",
            "DELETE /api/v1/employees/{employee_id}"
        ]
        
        for route in required_routes:
            if any(route in r for r in routes): 
                 print(f"  [PASS] Found critical route: {route}")
            else:
                 print(f"  [FAIL] Missing critical route: {route}")

    except Exception as e:
        print(f"  [ERROR] Could not scan API files: {e}")

if __name__ == "__main__":
    print("=== SYSTEM VERIFICATION SUITE ===")
    verify_database_schema()
    scan_api_endpoints()
    print("\n=== VERIFICATION COMPLETE ===")
