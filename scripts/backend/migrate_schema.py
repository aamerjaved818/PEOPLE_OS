import sqlite3
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import DatabaseConfig

def migrate_db(db_path):
    print(f"\n🚀 Migrating {db_path}...")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF;")
    cursor = conn.cursor()
    
    try:
        # Define required columns and their FK targets for hcm_employees
        hcm_employees_fks = {
            "line_manager_id": "hcm_employees(id)",
            "sub_department_id": "core_sub_departments(id)",
            "department_id": "core_departments(id)",
            "designation_id": "hcm_designations(id)",
            "grade_id": "hcm_grades(id)",
            "plant_id": "core_locations(id)",
            "shift_id": "hcm_shifts(id)",
            "organization_id": "core_organizations(id)"
        }

        # --- 1. Migrate hcm_employees ---
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hcm_employees'")
        if cursor.fetchone():
            print("  Checking hcm_employees...")
            cursor.execute("PRAGMA table_info(hcm_employees)")
            existing_cols = [row[1] for row in cursor.fetchall()]
            
            for col in hcm_employees_fks.keys():
                if col not in existing_cols:
                    print(f"    Adding column {col} to hcm_employees...")
                    cursor.execute(f"ALTER TABLE hcm_employees ADD COLUMN {col} TEXT;")
                    existing_cols.append(col)
            
            cols_str = ", ".join(existing_cols)
            cursor.execute("ALTER TABLE hcm_employees RENAME TO _hcm_employees_old;")
            col_defs = [f"{col} TEXT" if col != 'id' else "id TEXT PRIMARY KEY" for col in existing_cols]
            fk_defs = [f"FOREIGN KEY({col}) REFERENCES {target}" for col, target in hcm_employees_fks.items()]
            create_sql = f"CREATE TABLE hcm_employees ({', '.join(col_defs)}, {', '.join(fk_defs)});"
            cursor.execute(create_sql)
            cursor.execute(f"INSERT INTO hcm_employees ({cols_str}) SELECT {cols_str} FROM _hcm_employees_old;")
            cursor.execute("DROP TABLE _hcm_employees_old;")
            print("    ✅ hcm_employees migrated.")
        else:
            print("  ⚠️ hcm_employees not found, skipping.")
        
        # --- 2. Migrate platform_incidents ---
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='platform_incidents'")
        if cursor.fetchone():
            print("  Checking platform_incidents...")
            cursor.execute("PRAGMA table_info(platform_incidents)")
            existing_cols = [row[1] for row in cursor.fetchall()]
            
            if "related_migration_id" not in existing_cols:
                print("    Adding column related_migration_id to platform_incidents...")
                cursor.execute("ALTER TABLE platform_incidents ADD COLUMN related_migration_id TEXT;")
                existing_cols.append("related_migration_id")
                
            cols_str = ", ".join(existing_cols)
            cursor.execute("ALTER TABLE platform_incidents RENAME TO _platform_incidents_old;")
            col_defs = [f"{col} TEXT" if col != 'id' else "id TEXT PRIMARY KEY" for col in existing_cols]
            create_sql = f"CREATE TABLE platform_incidents ({', '.join(col_defs)}, FOREIGN KEY(related_migration_id) REFERENCES platform_migrations(id));"
            cursor.execute(create_sql)
            cursor.execute(f"INSERT INTO platform_incidents ({cols_str}) SELECT {cols_str} FROM _platform_incidents_old;")
            cursor.execute("DROP TABLE _platform_incidents_old;")
            print("    ✅ platform_incidents migrated.")
        else:
            print("  ⚠️ platform_incidents not found, skipping.")
        
        conn.commit()
        print(f"✅ Finished migration for {os.path.basename(db_path)}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error migrating {db_path}: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    config = DatabaseConfig()
    for env, db_file in config.DATABASE_FILES.items():
        path = os.path.join(config.DATA_DIR, db_file)
        if os.path.exists(path):
            migrate_db(path)
