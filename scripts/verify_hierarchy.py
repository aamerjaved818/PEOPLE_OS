import sqlite3
import os

DB_PATH = r'D:\Project\PEOPLE_OS\backend\data\people_os_dev.db'
TARGET_ORG_ID = 'ORG-001'

def verify_hierarchy():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"--- Verifying Hierarchy for {TARGET_ORG_ID} ---\n")

    # 1. Locations -> Org
    print("1. Locations linked to Organization:")
    cursor.execute(f"SELECT count(*), count(organization_id) FROM core_locations WHERE organization_id=?", (TARGET_ORG_ID,))
    total, linked = cursor.fetchone()
    print(f"   Total Locations for Org: {total}")
    if total > 0 and total == linked:
        print("   [SUCCESS] All locations are linked.")
    else:
        print(f"   [FAILURE] Linked: {linked}/{total}")

    # 2. Departments -> Org
    print("\n2. Departments linked to Organization:")
    cursor.execute(f"SELECT count(*), count(organization_id) FROM core_departments WHERE organization_id=?", (TARGET_ORG_ID,))
    total, linked = cursor.fetchone()
    print(f"   Total Departments for Org: {total}")
    if total > 0 and total == linked:
        print("   [SUCCESS] All departments are linked.")
    else:
        print(f"   [FAILURE] Linked: {linked}/{total}")

    # 3. Job Levels -> Org
    print("\n3. Job Levels linked to Organization:")
    cursor.execute(f"SELECT count(*), count(organization_id) FROM hcm_job_levels WHERE organization_id=?", (TARGET_ORG_ID,))
    total, linked = cursor.fetchone()
    print(f"   Total Job Levels for Org: {total}")
    if total > 0 and total == linked:
        print("   [SUCCESS] All Job Levels are linked.")
    else:
        print(f"   [FAILURE] Linked: {linked}/{total}")

    # 4. Grades -> Job Levels
    # First get all job level IDs for this org
    cursor.execute("SELECT id FROM hcm_job_levels WHERE organization_id=?", (TARGET_ORG_ID,))
    job_level_ids = [row[0] for row in cursor.fetchall()]
    
    if not job_level_ids:
        print("\n4. Grades -> Job Levels:")
        print("   [WARNING] No Job Levels found, cannot verify grades.")
    else:
        placeholders = ','.join(['?'] * len(job_level_ids))
        print(f"\n4. Grades linked to Job Levels (for {len(job_level_ids)} levels):")
        
        # Check if column is job_level_id or jobLevelId
        try:
            cursor.execute(f"SELECT count(*) FROM hcm_grades WHERE job_level_id IN ({placeholders})", job_level_ids)
            col_name = "job_level_id"
        except:
             col_name = "jobLevelId" # fallback guess

        try:
            query = f"SELECT count(*), count({col_name}) FROM hcm_grades WHERE {col_name} IN ({placeholders})"
            cursor.execute(query, job_level_ids)
            total, linked = cursor.fetchone()
            print(f"   Total Grades found: {total}")
            if total > 0:
                 print("   [SUCCESS] Grades are linked to valid Job Levels.")
            else:
                 print("   [INFO] No grades found for these levels.")
        except Exception as e:
            print(f"   [ERROR] Could not verify grades: {e}")

    # 5. Designations -> Grades
    # Get all grades for this org (via job levels)
    if job_level_ids:
        placeholders = ','.join(['?'] * len(job_level_ids))
        # Assuming job_level_id here based on previous step success or standard
        cursor.execute(f"SELECT id FROM hcm_grades WHERE job_level_id IN ({placeholders})", job_level_ids)
        grade_ids = [row[0] for row in cursor.fetchall()]
        
        if not grade_ids:
             print("\n5. Designations -> Grades:")
             print("   [WARNING] No Grades found, cannot verify designations.")
        else:
             grade_placeholders = ','.join(['?'] * len(grade_ids))
             print(f"\n5. Designations linked to Grades (for {len(grade_ids)} grades):")
             
             try:
                query = f"SELECT count(*), count(grade_id) FROM hcm_designations WHERE grade_id IN ({grade_placeholders})"
                cursor.execute(query, grade_ids)
                total, linked = cursor.fetchone()
                print(f"   Total Designations found: {total}")
                if total > 0:
                    print("   [SUCCESS] Designations are linked to valid Grades.")
                else:
                    print("   [INFO] No designations found for these grades.")
             except Exception as e:
                print(f"   [ERROR] Could not verify designations: {e}")

    conn.close()

if __name__ == "__main__":
    verify_hierarchy()
