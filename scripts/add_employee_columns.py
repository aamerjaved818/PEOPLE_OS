import sqlite3
import os

# Target the correct development database
DB_PATH = os.path.join("backend", "data", "people_os_dev.db")

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    
    # List of columns to add with their types
    columns = [
        ("father_name", "TEXT"),
        ("gender", "TEXT"),
        ("cnic", "TEXT"),
        ("cnic_expiry", "TEXT"),
        ("religion", "TEXT"),
        ("marital_status", "TEXT"),
        ("blood_group", "TEXT"),
        ("nationality", "TEXT"),
        ("phone", "TEXT"),
        ("personal_email", "TEXT"),
        ("personal_phone", "TEXT"),
        ("present_address", "TEXT"),
        ("permanent_address", "TEXT"),
        ("present_district", "TEXT"),
        ("permanent_district", "TEXT"),
        ("gross_salary", "REAL DEFAULT 0.0"),
        ("payment_mode", "TEXT"),
        ("bank_account", "TEXT"),
        ("bank_name", "TEXT"),
        ("eobi_number", "TEXT"),
        ("social_security_number", "TEXT"),
    ]

    print(f"Migrating {DB_PATH}...")
    
    # Check existing columns to avoid errors
    existing_columns = [x[1] for x in cur.execute("PRAGMA table_info(hcm_employees)").fetchall()]
    
    for col_name, col_type in columns:
        if col_name in existing_columns:
            print(f"Skipping {col_name} (already exists)")
            continue
            
        try:
            print(f"Adding column: {col_name}...")
            cur.execute(f"ALTER TABLE hcm_employees ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError as e:
            print(f"Error adding {col_name}: {e}")
                
    con.commit()
    con.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
