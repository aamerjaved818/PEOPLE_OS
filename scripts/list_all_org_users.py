import sqlite3
import os
from pprint import pprint

DB = os.path.join('backend', 'data', 'people_os_dev.db')
if not os.path.exists(DB):
    print('DB not found:', DB)
    raise SystemExit(1)

conn = sqlite3.connect(DB)
cur = conn.cursor()

print('Users in core_users:')
cur.execute('SELECT id, username, role, organization_id, employee_id, is_system_user FROM core_users ORDER BY organization_id NULLS FIRST, username')
rows = cur.fetchall()
for r in rows:
    print(r)

print('\nSummary by organization:')
cur.execute("SELECT organization_id, COUNT(*) FROM core_users WHERE organization_id IS NOT NULL GROUP BY organization_id")
for org_id, cnt in cur.fetchall():
    print(f" - {org_id}: {cnt} users")

conn.close()
