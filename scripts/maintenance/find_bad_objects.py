
import sqlite3
import os
import sys

# Add parent dir to path
sys.path.append(os.getcwd())
from backend.config import database_config

def dump_schema():
    db_path = database_config.DB_PATH
    print(f"Dumping schema from: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT type, name, tbl_name, sql FROM sqlite_master WHERE sql LIKE '%core_organizations_temp_fix%'")
    rows = cursor.fetchall()
    
    with open("db_dump.txt", "w", encoding="utf-8") as f:
        if not rows:
            f.write("No matching objects found.")
        for type_, name, tbl, sql in rows:
            f.write(f"TYPE: {type_}\nNAME: {name}\nTABLE: {tbl}\nSQL: {sql}\n")
            f.write("-" * 40 + "\n")
            
    print("Dump complete -> db_dump.txt")
    conn.close()

if __name__ == "__main__":
    dump_schema()
