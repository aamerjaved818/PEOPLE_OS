import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'people_os_dev.db')
DB_PATH = os.path.normpath(DB_PATH)

def main():
    print('Verification run at (UTC):', datetime.datetime.utcnow().isoformat() + 'Z')
    if not os.path.exists(DB_PATH):
        print('Database not found at', DB_PATH)
        return 1

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    roots = cur.execute(
        "SELECT id, username, role, is_system_user, organization_id FROM core_users WHERE role = 'Root'"
    ).fetchall()

    print('\nRoot users found:', len(roots))
    for r in roots:
        print(' - ID:', r[0], ' Username:', r[1], ' Role:', r[2], ' SystemUser:', r[3], ' Org:', r[4])

    # Also search for '.amer' and 'amer' specifically
    for uname in ['.amer', 'amer']:
        row = cur.execute("SELECT id, username, role, is_system_user, organization_id FROM core_users WHERE username=?", (uname,)).fetchone()
        if row:
            print(f"\nUser check: Found user {uname}: ID={row[0]} Role={row[2]} SystemUser={row[3]} Org={row[4]}")
        else:
            print(f"\nUser check: {uname} NOT FOUND")

    conn.close()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
