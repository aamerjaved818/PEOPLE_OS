import sqlite3
import os

DBS = ['people_os_dev.db', 'people_os_test.db', 'people_os_prod.db', 'people_os.db']
ADMIN_ID = "00000000-0000-0000-0000-000000000001"

print("--- Verifying System User Seeding ---")
for db_name in DBS:
    db_path = os.path.join("backend", "data", db_name)
    if not os.path.exists(db_path):
        print(f"[{db_name}] File matches? MISSING")
        continue

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check System Users
        usernames = ["root", "super_admin", "ci_runner", "auditor"]
        for username in usernames:
            cursor.execute("SELECT count(*) FROM core_users WHERE username=?", (username,))
            count = cursor.fetchone()[0]
            status = "✅ FOUND" if count > 0 else "❌ MISSING"
            print(f"[{db_name}] User '{username}': {status}")

        conn.close()
    except Exception as e:
        print(f"[{db_name}] Error: {str(e)}")
