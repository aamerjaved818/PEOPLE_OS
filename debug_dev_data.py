import sqlite3
import os

DB_PATH = r"backend\data\people_os_dev.db"

def debug_data():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"DEBUGGING: {DB_PATH}")
    
    # 1. Get Active Organization
    print("\n--- Active Organizations ---")
    cursor.execute("SELECT id, name FROM core_organizations")
    orgs = cursor.fetchall()
    for org in orgs:
        print(f"Org ID: {org[0]} | Name: {org[1]}")
    
    if not orgs:
        print("!! NO ORGANIZATIONS FOUND !!")
        return
        
    active_org_id = orgs[0][0] # Assuming single tenant for now

    # 2. Check Locations (Plants)
    print("\n--- Core Locations (Plants) ---")
    cursor.execute(f"SELECT id, name, organization_id FROM core_locations")
    rows = cursor.fetchall()
    for row in rows:
        match = "MATCH" if row[2] == active_org_id else "MISMATCH"
        print(f"Plant: {row[1]} | OrgID: {row[2]} | Status: {match}")

    # 3. Check Job Levels
    print("\n--- Job Levels ---")
    cursor.execute(f"SELECT id, name, organization_id FROM hcm_job_levels")
    rows = cursor.fetchall()
    for row in rows:
        match = "MATCH" if row[2] == active_org_id else "MISMATCH"
        print(f"Level: {row[1]} | OrgID: {row[2]} | Status: {match}")

    conn.close()

if __name__ == "__main__":
    debug_data()
