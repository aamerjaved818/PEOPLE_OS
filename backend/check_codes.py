import sqlite3
conn = sqlite3.connect(r'd:\Project\PEOPLE_OS\backend\data\people_os_dev.db')
cursor = conn.cursor()
cursor.execute("SELECT id, name, employee_code, plant_id FROM hcm_employees")
for row in cursor.fetchall():
    print(row)
conn.close()
