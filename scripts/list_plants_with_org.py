import sqlite3
import os

db_path = os.path.join("backend", "data", "people_os_dev.db")
print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
        SELECT 
            p.name as plant_name, 
            p.code as plant_code, 
            o.name as org_name
        FROM core_locations p
        JOIN core_organizations o ON p.organization_id = o.id
        ORDER BY p.name;
    """
    
    cursor.execute(query)
    plants = cursor.fetchall()
    
    print(f"\nTotal Plants Found: {len(plants)}")
    print("-" * 60)
    print(f"{'Plant Name':<30} | {'Code':<10} | {'Parent Organization'}")
    print("-" * 60)
    
    for plant in plants:
        print(f"{plant[0]:<30} | {plant[1]:<10} | {plant[2]}")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
