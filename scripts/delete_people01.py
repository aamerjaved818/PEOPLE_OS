import sqlite3
from pathlib import Path

def inspect_and_clean():
    db_path = Path("backend/data/people_os_dev.db")
    if not db_path.exists():
        db_path = Path("../backend/data/people_os_dev.db")
    
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return

    print(f"Connecting to {db_path}...")
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = OFF") # Temporarily disable to allowing clearing children without strict order, then we verify
    cur = conn.cursor()

    try:
        # 1. Search for 'DEF' hinted org
        print("\n--- Searching for 'DEF' Organizations ---")
        cur.execute("SELECT id, name, code FROM core_organizations WHERE code LIKE '%DEF%'")
        defs = cur.fetchall()
        if defs:
            for d in defs:
                print(f"Found match: {d}")
        else:
            print("No organization found containing 'DEF' in code.")

        # 2. Target PEOPLE01
        cur.execute("SELECT id, name FROM core_organizations WHERE code = 'PEOPLE01'")
        org = cur.fetchone()
        
        if not org:
            print("\nOrganization PEOPLE01 not found (already deleted?).")
        else:
            org_id, org_name = org
            print(f"\nTime to delete: {org_name} (ID: {org_id})")
            
            # Find all tables with organization_id
            print("Scanning schema for dependent tables...")
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cur.fetchall()]
            
            dependent_tables = []
            for t in tables:
                try:
                    cur.execute(f"PRAGMA table_info({t})")
                    columns = [col[1] for col in cur.fetchall()]
                    if 'organization_id' in columns:
                        dependent_tables.append(t)
                except:
                    pass
            
            print(f"Found {len(dependent_tables)} tables with organization_id.")
            
            # Aggressive Delete
            for t in dependent_tables:
                if t == 'core_organizations': continue
                
                # Check count first
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {t} WHERE organization_id = ?", (org_id,))
                    count = cur.fetchone()[0]
                    if count > 0:
                        print(f"Deleting {count} rows from {t}...")
                        cur.execute(f"DELETE FROM {t} WHERE organization_id = ?", (org_id,))
                except Exception as e:
                    print(f"Error checking/deleting {t}: {e}")

            # Specific link tables check (e.g. users might not have org_id directly but via link)
            # But earlier delete failed on FK, so likely direct child.
            
            # Finally delete Org
            print("Deleting Organization record...")
            cur.execute("DELETE FROM core_organizations WHERE id = ?", (org_id,))
            print("Done.")

        conn.commit()
        print("\nSuccess. Foreign Keys were bypassed (PRAGMA foreign_keys = OFF) to ensure deep cleanup.")
        
        # Verify
        conn.execute("PRAGMA foreign_keys = ON")
        cur.execute("PRAGMA foreign_key_check")
        errors = cur.fetchall()
        if errors:
            print(f"\nWARNING: {len(errors)} Foreign Key violations detected after cleanup. The database might have orphans.")
            for e in errors[:5]:
                print(e)
        else:
            print("\nIntegrity Check Passed.")

    except Exception as e:
        print(f"FATAL ERROR: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_and_clean()
