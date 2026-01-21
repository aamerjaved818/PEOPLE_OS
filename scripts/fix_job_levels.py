import sqlite3
import os
import time

ENV_DBS = [
    r'D:\Project\PEOPLE_OS\backend\data\people_os_dev.db',
    r'D:\Project\PEOPLE_OS\backend\data\people_os_test.db',
    r'D:\Project\PEOPLE_OS\backend\data\people_os_prod.db'
]

DEFAULT_LEVELS = [
    (1, "Intern", "INT"),
    (2, "Junior", "JUN"),
    (3, "Associate", "ASC"),
    (4, "Senior", "SNR"),
    (5, "Principal", "PRN"),
    (6, "Manager", "MGR"),
    (7, "Director", "DIR"),
    (8, "VP", "VP"),
    (9, "C-Level", "EXEC")
]

def fix_db(db_path):
    print(f"Checking {db_path}...")
    if not os.path.exists(db_path):
        print("  -> DB checks: Not found (Skipping)")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Create Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_levels (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT,
            rank INTEGER,
            description TEXT,
            is_active BOOLEAN DEFAULT 1,
            organization_id TEXT NOT NULL,
            created_by TEXT,
            updated_by TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(organization_id) REFERENCES core_organizations(id)
        );
        """)
        
        # 2. Get Orgs
        cursor.execute("SELECT id, name FROM core_organizations")
        orgs = cursor.fetchall()
        
        for org_id, org_name in orgs:
            cursor.execute("SELECT count(*) FROM job_levels WHERE organization_id=?", (org_id,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                print(f"  -> Seeding job levels for org: {org_name} ({org_id})")
                for rank, name, code in DEFAULT_LEVELS:
                    # Create a unique ID
                    level_id = f"JL-{org_id[-4:]}-{code}-{rank}" 
                    
                    cursor.execute("""
                        INSERT INTO job_levels (id, name, code, rank, organization_id, description, is_active, created_by)
                        VALUES (?, ?, ?, ?, ?, 'Standard System Level', 1, 'system')
                    """, (level_id, name, code, rank, org_id))
                conn.commit()
                print("     -> seeded.")
            else:
                print(f"  -> Levels already exist for {org_name} ({count} found)")
                
    except Exception as e:
        print(f"  -> Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    for db in ENV_DBS:
        fix_db(db)
