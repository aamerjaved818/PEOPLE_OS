import sys
import os
from sqlalchemy import create_engine, inspect

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.config import settings

def inspect_schema():
    print(f"Connecting to Database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    table_names = inspector.get_table_names()
    print(f"Found Tables: {len(table_names)}")
    
    target_tables = ["hcm_employees", "hcm_grades", "hcm_job_levels"]
    
    for table in target_tables:
        if table not in table_names:
            print(f"❌ Table '{table}' NOT FOUND in database!")
            continue
            
        print(f"\n--- Checking Table: {table} ---")
        columns = inspector.get_columns(table)
        col_names = [col['name'] for col in columns]
        
        # Print columns with type
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
            
        # Specific checks for Employee
        if table == "hcm_employees":
            required_fks = ["grade_id", "designation_id", "department_id", "shift_id"]
            missing = [fk for fk in required_fks if fk not in col_names]
            if missing:
                print(f"  ❌ MISSING FOREIGN KEYS: {missing}")
            else:
                print("  ✅ All expected Foreign Key columns present.")

inspect_schema()
