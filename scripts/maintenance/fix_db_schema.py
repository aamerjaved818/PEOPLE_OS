import sqlite3

db = sqlite3.connect('backend/data/people_os_dev.db')
cur = db.cursor()

# Get current columns
cur.execute("PRAGMA table_info(hcm_employees)")
existing_columns = {col[1] for col in cur.fetchall()}

print("Current columns in hcm_employees:")
for col in sorted(existing_columns):
    print(f"  - {col}")

# Missing columns needed by the model
missing_columns = {
    'emergency_contact_name': 'TEXT',
    'emergency_contact_phone': 'TEXT',
    'emergency_contact_relation': 'TEXT',
    'profile_photo_url': 'TEXT',
    'bio': 'TEXT',
}

print("\nAdding missing columns...")
for col_name, col_type in missing_columns.items():
    if col_name not in existing_columns:
        try:
            cur.execute(f"ALTER TABLE hcm_employees ADD COLUMN {col_name} {col_type}")
            print(f"  ✓ Added {col_name}")
        except Exception as e:
            print(f"  ✗ Error adding {col_name}: {e}")
    else:
        print(f"  - {col_name} already exists")

db.commit()
db.close()

print("\n✓ Database schema updated successfully!")
