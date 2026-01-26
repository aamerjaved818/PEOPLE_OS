
import sqlite3
import os
import sys

# Add parent dir to path
sys.path.append(os.getcwd())

from backend.config import database_config

def inspect():
    db_path = database_config.DB_PATH
    print(f"Inspecting DB at: {db_path}")
    
    # Fallback check
    if not os.path.exists(db_path):
         # Try identifying if we are in dev and just 'people.db' or 'people_os_dev.db' is elsewhere
         alternatives = ['people.db', 'backend/data/people_os_dev.db']
         for alt in alternatives:
             if os.path.exists(alt):
                 print(f"Config path not found, falling back to: {alt}")
                 db_path = alt
                 break
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("--- Searching ALL Checkraints/Triggers/Views/Indexes referencing 'core_users_backup' ---")
        cursor.execute("SELECT type, name, tbl_name, sql FROM sqlite_master WHERE sql LIKE '%core_users_backup%'")
        objects = cursor.fetchall()
        
        if objects:
            for type_, name, tbl, sql in objects:
                print(f"FOUND {type_.upper()}: {name} on table {tbl}")
                print(f"SQL: {sql}")
                print("-" * 20)
        else:
             print("No DB objects found referencing that table.")
             
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect()
