import sqlite3, os

db='backend/data/people_os_dev.db'
if not os.path.exists(db):
    print('DB not found', db)
    raise SystemExit(1)
conn=sqlite3.connect(db)
c=conn.cursor()
emp_id='ADMIN01-0001'
# Insert employee if not exists
c.execute("SELECT id FROM hcm_employees WHERE id=?", (emp_id,))
if not c.fetchone():
    c.execute('''INSERT INTO hcm_employees (id, employee_code, name, organization_id, join_date, email, status)
                 VALUES (?,?,?,?,?,?,?)''', (emp_id, emp_id, 'Admin Employee', 'PEOPLE01', '2020-01-01', 'admin@example.com', 'Active'))
    print('Inserted employee', emp_id)
else:
    print('Employee already exists')
# Link to user
c.execute("SELECT id, username, employee_id FROM core_users WHERE username='admin'")
row=c.fetchone()
if row:
    print('Found user', row)
    c.execute("UPDATE core_users SET employee_id=? WHERE username='admin'", (emp_id,))
    print('Linked user admin ->', emp_id)
else:
    print('Admin user not found')
conn.commit()
# Verify
c.execute("SELECT id, employee_code, name, join_date FROM hcm_employees WHERE id=?", (emp_id,))
print('Employee row:', c.fetchone())
c.execute("SELECT id, username, employee_id FROM core_users WHERE username='admin'")
print('User row after update:', c.fetchone())
conn.close()
