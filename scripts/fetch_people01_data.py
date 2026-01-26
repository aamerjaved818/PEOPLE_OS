import sqlite3
import json
from pathlib import Path

def fetch_data():
    db_path = Path("backend/data/people_os_dev.db")
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get Organization
    cur.execute("SELECT id, name, code FROM core_organizations WHERE code = 'PEOPLE01'")
    org = cur.fetchone()
    if not org:
        print("Organization PEOPLE01 not found.")
        return

    org_id = org['id']
    print(f"Organization: {org['name']} ({org['code']}) ID: {org_id}")

    # Departments
    cur.execute("SELECT id, name, code FROM core_departments WHERE organization_id = ?", (org_id,))
    deps = cur.fetchall()
    print(f"\nDepartments ({len(deps)}):")
    for d in deps:
        print(f"  - {d['name']} ({d['code']})")

    # Job Levels
    cur.execute("SELECT id, name, code FROM hcm_job_levels WHERE organization_id = ?", (org_id,))
    levels = cur.fetchall()
    print(f"\nJob Levels ({len(levels)}):")
    for l in levels:
        print(f"  - {l['name']} ({l['code']})")

    # Grades
    cur.execute("SELECT id, name, code FROM hcm_grades WHERE organization_id = ?", (org_id,))
    grades = cur.fetchall()
    print(f"\nGrades ({len(grades)}):")
    for g in grades:
        print(f"  - {g['name']} ({g['code']})")

    # Designations
    cur.execute("SELECT id, name, code FROM hcm_designations WHERE organization_id = ?", (org_id,))
    desigs = cur.fetchall()
    print(f"\nDesignations ({len(desigs)}):")
    for d in desigs:
        print(f"  - {d['name']} ({d['code']})")

    # Employees
    cur.execute("SELECT id, name, employee_code FROM hcm_employees WHERE organization_id = ?", (org_id,))
    emps = cur.fetchall()
    print(f"\nEmployees ({len(emps)}):")
    for e in emps:
        print(f"  - {e['name']} ({e['employee_code']})")

    conn.close()

if __name__ == "__main__":
    fetch_data()
