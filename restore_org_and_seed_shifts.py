import sqlite3
import os
import uuid
from datetime import datetime, timezone

DATABASES = {
    "dev": r"backend\data\people_os_dev.db",
    "prod": r"backend\data\people_os_prod.db",
    "test": r"backend\data\people_os_test.db"
}
BACKUP_DB = r"backend\data\backups\people_os.backup.db"

STANDARD_SHIFTS = [
    {
        "name": "General",
        "code": "G",
        "type": "Fixed",
        "start_time": "09:00",
        "end_time": "17:00",
        "grace_period": 15,
        "break_duration": 60,
        "work_days": "Mon,Tue,Wed,Thu,Fri",
        "color": "#3b82f6",
        "description": "Standard fixed shift.",
    },
    {
        "name": "Reliever",
        "code": "R",
        "type": "Reliever",
        "start_time": "09:00",
        "end_time": "17:00",
        "grace_period": 15,
        "break_duration": 60,
        "work_days": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "color": "#22c55e",
        "description": "Works on others rest days or flexibly.",
    },
    {
        "name": "Shift A",
        "code": "A",
        "type": "Rotating",
        "start_time": "06:00",
        "end_time": "14:00",
        "grace_period": 10,
        "break_duration": 30,
        "work_days": "Mon,Tue,Wed,Thu,Fri,Sat",
        "color": "#f59e0b",
        "description": "Morning Shift (Rotating).",
    },
    {
        "name": "Shift B",
        "code": "B",
        "type": "Rotating",
        "start_time": "14:00",
        "end_time": "22:00",
        "grace_period": 10,
        "break_duration": 30,
        "work_days": "Mon,Tue,Wed,Thu,Fri,Sat",
        "color": "#a855f7",
        "description": "Evening Shift (Rotating).",
    },
    {
        "name": "Shift C",
        "code": "C",
        "type": "Rotating",
        "start_time": "22:00",
        "end_time": "06:00",
        "grace_period": 10,
        "break_duration": 30,
        "work_days": "Mon,Tue,Wed,Thu,Fri,Sat",
        "color": "#ef4444",
        "description": "Night Shift (Rotating).",
    },
    {
        "name": "Flexible",
        "code": "F",
        "type": "Flexible",
        "start_time": "00:00",
        "end_time": "23:59",
        "grace_period": 0,
        "break_duration": 60,
        "work_days": "Mon,Tue,Wed,Thu,Fri",
        "color": "#06b6d4",
        "description": "Work any time flexibly.",
    },
]

def migrate_schema(conn, table_name="hcm_shifts"):
    """Ensure hcm_shifts has color and description."""
    cursor = conn.cursor()
    # Check if table exists
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if not cursor.fetchone():
        # Create table if missing (Simplified schema based on usage)
        print(f"  Creating table {table_name}...")
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id TEXT PRIMARY KEY,
                name TEXT,
                code TEXT,
                type TEXT,
                start_time TEXT,
                end_time TEXT,
                grace_period INTEGER,
                break_duration INTEGER,
                work_days TEXT,
                isActive BOOLEAN DEFAULT 1,
                organization_id TEXT,
                color TEXT,
                description TEXT,
                created_at DATETIME,
                updated_at DATETIME
            )
        """)
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]

    if "color" not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN color TEXT")
    if "description" not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN description TEXT")
    
    conn.commit()

def process_env(env_name, db_path):
    if not os.path.exists(db_path):
        print(f"[{env_name.upper()}] DB missing at {db_path}")
        return

    print(f"\n[{env_name.upper()}] Processing {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Restore Organization if missing
    cursor.execute("SELECT COUNT(*) FROM core_organizations")
    if cursor.fetchone()[0] == 0:
        print("  Restoring core_organizations from backup...")
        if os.path.exists(BACKUP_DB):
            cursor.execute(f"ATTACH DATABASE '{BACKUP_DB}' AS backup")
            try:
                cursor.execute("INSERT OR IGNORE INTO core_organizations SELECT * FROM backup.core_organizations")
                conn.commit()
                print("  [SUCCESS] Organization restored.")
            except Exception as e:
                print(f"  [ERROR] Restoring organization: {e}")
            cursor.execute("DETACH DATABASE backup")
        else:
            print("  [WARNING] Backup DB not found, cannot restore organization.")

    # 2. Get Organization ID
    cursor.execute("SELECT id FROM core_organizations LIMIT 1")
    org_row = cursor.fetchone()
    if not org_row:
        print("  [ERROR] No organization found. Skipping shift seeding.")
        conn.close()
        return

    organization_id = org_row[0]
    
    # 3. Seed Shifts
    migrate_schema(conn)
    
    print("  Seeding shifts...")
    now = datetime.now(timezone.utc).isoformat()
    
    for shift in STANDARD_SHIFTS:
        cursor.execute(
            "SELECT id FROM hcm_shifts WHERE code = ? AND organization_id = ?",
            (shift["code"], organization_id)
        )
        if not cursor.fetchone():
            shift_id = f"SHF-{shift['code']}-{str(uuid.uuid4())[:8]}"
            cursor.execute("""
                INSERT INTO hcm_shifts (
                    id, name, code, type, start_time, end_time,
                    grace_period, break_duration, work_days, isActive,
                    organization_id, color, description, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?)
            """, (
                shift_id, shift["name"], shift["code"], shift["type"],
                shift["start_time"], shift["end_time"], shift["grace_period"],
                shift["break_duration"], shift["work_days"], organization_id,
                shift["color"], shift["description"], now, now
            ))
            print(f"    + Created {shift['name']}")
        else:
            print(f"    . {shift['name']} exists")

    conn.commit()
    
    # Verify count
    count = cursor.execute("SELECT COUNT(*) FROM hcm_shifts").fetchone()[0]
    print(f"  Total Shifts: {count}")
    
    conn.close()

if __name__ == "__main__":
    for env, path in DATABASES.items():
        process_env(env, path)
    print("\n✅ Shift restoration/seeding complete.")
