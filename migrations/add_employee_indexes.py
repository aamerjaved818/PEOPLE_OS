"""
Database migration to add performance indexes for employee module.
Run with: python -m alembic upgrade head
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

def create_indexes(db: Session):
    """Create recommended indexes for employee table"""
    
    indexes = [
        # Email uniqueness within organization
        {
            "name": "idx_org_email",
            "sql": """
                CREATE INDEX IF NOT EXISTS idx_org_email 
                ON employees(organization_id, email)
            """
        },
        # Employee code lookup
        {
            "name": "idx_employee_code",
            "sql": """
                CREATE INDEX IF NOT EXISTS idx_employee_code 
                ON employees(employee_code)
            """
        },
        # Status filtering
        {
            "name": "idx_status",
            "sql": """
                CREATE INDEX IF NOT EXISTS idx_status 
                ON employees(status)
            """
        },
        # Line manager hierarchy queries
        {
            "name": "idx_line_manager",
            "sql": """
                CREATE INDEX IF NOT EXISTS idx_line_manager_id 
                ON employees(line_manager_id)
            """
        },
        # Organization + status for active employee checks
        {
            "name": "idx_org_status_active",
            "sql": """
                CREATE INDEX IF NOT EXISTS idx_org_status_active 
                ON employees(organization_id, status)
                WHERE status IN ('active', 'confirmed', 'probation')
            """
        },
        # CNIC uniqueness among active employees
        {
            "name": "idx_org_cnic_active",
            "sql": """
                CREATE INDEX IF NOT EXISTS idx_org_cnic_active 
                ON employees(organization_id, cnic)
                WHERE status IN ('active', 'confirmed', 'probation')
            """
        },
        # Phone numbers uniqueness among active employees
        {
            "name": "idx_org_phone_active",
            "sql": """
                CREATE INDEX IF NOT EXISTS idx_org_phone_active 
                ON employees(organization_id, phone)
                WHERE status IN ('active', 'confirmed', 'probation')
            """
        },
        {
            "name": "idx_org_personal_phone_active",
            "sql": """
                CREATE INDEX IF NOT EXISTS idx_org_personal_phone_active 
                ON employees(organization_id, personal_phone)
                WHERE status IN ('active', 'confirmed', 'probation')
            """
        },
        # Department filtering
        {
            "name": "idx_department",
            "sql": """
                CREATE INDEX IF NOT EXISTS idx_department_id 
                ON employees(department_id)
            """
        },
        # Plant filtering
        {
            "name": "idx_plant",
            "sql": """
                CREATE INDEX IF NOT EXISTS idx_plant_id 
                ON employees(plant_id)
            """
        }
    ]
    
    created = 0
    failed = []
    
    for index in indexes:
        try:
            db.execute(text(index["sql"]))
            db.commit()
            created += 1
            print(f"✓ Created index: {index['name']}")
        except Exception as e:
            failed.append(f"{index['name']}: {str(e)}")
            print(f"✗ Failed to create index {index['name']}: {str(e)}")
    
    return {
        "created": created,
        "failed": failed,
        "total": len(indexes),
        "message": f"Created {created}/{len(indexes)} indexes"
    }


def drop_indexes(db: Session):
    """Drop all employee-related indexes (for testing/cleanup)"""
    
    indexes = [
        "idx_org_email",
        "idx_employee_code",
        "idx_status",
        "idx_line_manager_id",
        "idx_org_status_active",
        "idx_org_cnic_active",
        "idx_org_phone_active",
        "idx_org_personal_phone_active",
        "idx_department_id",
        "idx_plant_id"
    ]
    
    dropped = 0
    
    for index_name in indexes:
        try:
            db.execute(text(f"DROP INDEX IF EXISTS {index_name}"))
            db.commit()
            dropped += 1
            print(f"✓ Dropped index: {index_name}")
        except Exception as e:
            print(f"✗ Failed to drop index {index_name}: {str(e)}")
    
    return {"dropped": dropped, "total": len(indexes)}


if __name__ == "__main__":
    # Run from project root: python backend/migrations/add_employee_indexes.py
    import sys
    sys.path.insert(0, '.')
    
    from backend.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        result = create_indexes(db)
        print(f"\n{result['message']}")
        if result['failed']:
            print("Failures:")
            for failure in result['failed']:
                print(f"  - {failure}")
    finally:
        db.close()
