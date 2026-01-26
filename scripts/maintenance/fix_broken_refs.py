
import sqlite3
import os
import sys

# Add parent dir to path
sys.path.append(os.getcwd())
from backend.config import database_config

def fix_schema():
    db_path = database_config.DB_PATH
    print(f"Dynamically fixing broken FKs in: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys=OFF")
    
    try:
        # Find all broken tables
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE sql LIKE '%core_organizations_temp_fix%' AND type='table'")
        broken_tables = cursor.fetchall()
        
        print(f"Found {len(broken_tables)} broken tables.")
        
        for name, sql in broken_tables:
            print(f"Fixing {name}...")
            
            # 1. Rename current broken table to temp
            temp_name = f"{name}_temp_fix"
            cursor.execute(f"DROP TABLE IF EXISTS {temp_name}") # Safety
            cursor.execute(f"ALTER TABLE {name} RENAME TO {temp_name}")
            
            # 2. Generate correct SQL
            # Replace the bad reference with the good one
            new_sql = sql.replace('"core_organizations_temp_fix"', 'core_organizations')
            new_sql = new_sql.replace('core_organizations_temp_fix', 'core_organizations')
            
            # Also fix any other lingering temp fixes if they exist in the definition
            new_sql = new_sql.replace('"core_departments_temp_fix"', 'core_departments')
            new_sql = new_sql.replace('core_departments_temp_fix', 'core_departments')
            new_sql = new_sql.replace('"core_sub_departments_temp_fix"', 'core_sub_departments')
            new_sql = new_sql.replace('core_sub_departments_temp_fix', 'core_sub_departments')
            
            # 3. Create new table
            cursor.execute(new_sql)
            
            # 4. Copy data
            cursor.execute(f"INSERT INTO {name} SELECT * FROM {temp_name}")
            
            # 5. Drop temp
            cursor.execute(f"DROP TABLE {temp_name}")
            print(f"✅ {name} fixed.")
            
        conn.commit()
        print("All tables repaired.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_schema()
