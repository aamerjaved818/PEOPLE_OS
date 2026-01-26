"""
Database Schema Migration for RBAC Enhancements
================================================

Migration: Add constraints and indexes for RBAC system
- Super Admin uniqueness per organization
- System user isolation enforcement
- Enhanced audit trail for role changes
- Indexes for performance
"""

import sqlite3
from datetime import datetime
from pathlib import Path


# Migration version
MIGRATION_VERSION = "001_rbac_enhancements"
MIGRATION_DATE = datetime.now().isoformat()


def migrate_up(db_path: str) -> dict:
    """
    Apply RBAC enhancement migrations.
    
    Returns:
        dict with success status and details
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    results = {
        "version": MIGRATION_VERSION,
        "date": MIGRATION_DATE,
        "statements": [],
        "errors": [],
        "success": True
    }
    
    try:
        # ================================================================
        # MIGRATION 1: Add UNIQUE constraint for Super Admin per org
        # ================================================================
        # SQLite doesn't support adding constraints directly, so we create
        # a new table and migrate data
        
        print("[1/5] Adding Super Admin uniqueness constraint...")
        
        # Check if constraint already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='core_users'
        """)
        
        if cursor.fetchone():
            # Create trigger to enforce Super Admin uniqueness
            trigger_sql = """
            CREATE TRIGGER IF NOT EXISTS enforce_super_admin_uniqueness
            BEFORE INSERT ON core_users
            WHEN NEW.role = 'Super Admin'
            BEGIN
                SELECT CASE
                    WHEN (
                        SELECT COUNT(*)
                        FROM core_users
                        WHERE role = 'Super Admin'
                        AND organization_id = NEW.organization_id
                        AND id != NEW.id
                    ) > 0
                    THEN RAISE(ABORT, 'Only one Super Admin allowed per organization')
                END;
            END;
            """
            
            cursor.execute(trigger_sql)
            results["statements"].append("Created TRIGGER enforce_super_admin_uniqueness")
        
        # ================================================================
        # MIGRATION 2: Add CHECK constraint for system user isolation
        # ================================================================
        
        print("[2/5] Adding system user isolation check constraint...")
        
        # Create trigger to enforce system user isolation
        trigger_sql = """
        CREATE TRIGGER IF NOT EXISTS enforce_system_user_isolation
        BEFORE INSERT ON core_users
        BEGIN
            SELECT CASE
                WHEN (
                    (NEW.is_system_user = 1 AND NEW.organization_id IS NOT NULL)
                    OR
                    (NEW.is_system_user = 0 AND NEW.organization_id IS NULL)
                )
                THEN RAISE(ABORT, 
                    'System users (is_system_user=1) cannot have organization_id, '
                    'and organization users (is_system_user=0) must have organization_id')
            END;
        END;
        """
        
        cursor.execute(trigger_sql)
        results["statements"].append("Created TRIGGER enforce_system_user_isolation")
        
        # ================================================================
        # MIGRATION 3: Create audit trail table for role changes
        # ================================================================
        
        print("[3/5] Creating role change audit table...")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core_role_change_audit (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            old_role TEXT,
            new_role TEXT NOT NULL,
            changed_by TEXT NOT NULL,
            reason TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES core_users(id),
            FOREIGN KEY (changed_by) REFERENCES core_users(id)
        );
        """)
        
        results["statements"].append("Created TABLE core_role_change_audit")
        
        # ================================================================
        # MIGRATION 4: Create permission change audit table
        # ================================================================
        
        print("[4/5] Creating permission change audit table...")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core_permission_change_audit (
            id TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            permission TEXT NOT NULL,
            action TEXT NOT NULL,  -- 'GRANT' or 'REVOKE'
            changed_by TEXT NOT NULL,
            organization_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (changed_by) REFERENCES core_users(id),
            FOREIGN KEY (organization_id) REFERENCES core_organizations(id)
        );
        """)
        
        results["statements"].append("Created TABLE core_permission_change_audit")
        
        # ================================================================
        # MIGRATION 5: Add indexes for performance
        # ================================================================
        
        print("[5/5] Adding performance indexes...")
        
        indexes = [
            # User lookups by role
            """
            CREATE INDEX IF NOT EXISTS idx_users_role 
            ON core_users(role);
            """,
            
            # User lookups by organization
            """
            CREATE INDEX IF NOT EXISTS idx_users_organization 
            ON core_users(organization_id);
            """,
            
            # User lookups by system user flag
            """
            CREATE INDEX IF NOT EXISTS idx_users_system_user 
            ON core_users(is_system_user);
            """,
            
            # Composite index for role + org lookups (Super Admin queries)
            """
            CREATE INDEX IF NOT EXISTS idx_users_role_org 
            ON core_users(role, organization_id);
            """,
            
            # Permission lookups
            """
            CREATE INDEX IF NOT EXISTS idx_role_permissions_role 
            ON core_role_permissions(role);
            """,
            
            # Audit trail queries
            """
            CREATE INDEX IF NOT EXISTS idx_role_change_audit_user 
            ON core_role_change_audit(user_id);
            """,
            
            """
            CREATE INDEX IF NOT EXISTS idx_role_change_audit_timestamp 
            ON core_role_change_audit(timestamp);
            """,
            
            # Permission audit queries
            """
            CREATE INDEX IF NOT EXISTS idx_permission_audit_timestamp 
            ON core_permission_change_audit(timestamp);
            """,
        ]
        
        for idx_sql in indexes:
            cursor.execute(idx_sql)
            results["statements"].append(f"Created index: {idx_sql.strip()[:50]}...")
        
        # ================================================================
        # VERIFICATION: Check data integrity
        # ================================================================
        
        print("\nVerifying data integrity...")
        
        # Check for Root users in database (should be none)
        cursor.execute("""
        SELECT COUNT(*) as root_count
        FROM core_users
        WHERE role = 'Root'
        """)
        
        root_count = cursor.fetchone()[0]
        if root_count > 0:
            results["errors"].append(
                f"WARNING: Found {root_count} Root user(s) in database. "
                "Root should only exist in-memory in dependencies.py"
            )
        else:
            results["statements"].append("✓ Verified: No Root users in database")
        
        # Check for orphaned Super Admins
        cursor.execute("""
        SELECT u.id, u.username, u.organization_id
        FROM core_users u
        WHERE u.role = 'Super Admin'
        AND u.organization_id NOT IN (
            SELECT id FROM core_organizations
        )
        """)
        
        orphaned = cursor.fetchall()
        if orphaned:
            results["errors"].append(
                f"WARNING: Found {len(orphaned)} orphaned Super Admin(s): {orphaned}"
            )
        else:
            results["statements"].append("✓ Verified: No orphaned Super Admins")
        
        # Check for multiple Super Admins per org
        cursor.execute("""
        SELECT organization_id, COUNT(*) as count
        FROM core_users
        WHERE role = 'Super Admin'
        GROUP BY organization_id
        HAVING count > 1
        """)
        
        duplicates = cursor.fetchall()
        if duplicates:
            results["errors"].append(
                f"ERROR: Found multiple Super Admins in same org(s): {duplicates}"
            )
            results["success"] = False
        else:
            results["statements"].append("✓ Verified: One Super Admin per organization")
        
        # Check system user isolation
        cursor.execute("""
        SELECT id, username, is_system_user, organization_id
        FROM core_users
        WHERE (is_system_user = 1 AND organization_id IS NOT NULL)
        OR (is_system_user = 0 AND organization_id IS NULL)
        """)
        
        violations = cursor.fetchall()
        if violations:
            results["errors"].append(
                f"ERROR: System user isolation violations found: {violations}"
            )
            results["success"] = False
        else:
            results["statements"].append("✓ Verified: System user isolation intact")
        
        conn.commit()
        
    except Exception as e:
        results["errors"].append(f"Migration error: {str(e)}")
        results["success"] = False
        conn.rollback()
    
    finally:
        conn.close()
    
    return results


def migrate_down(db_path: str) -> dict:
    """
    Rollback RBAC enhancement migrations.
    
    Returns:
        dict with success status and details
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    results = {
        "version": MIGRATION_VERSION,
        "date": MIGRATION_DATE,
        "statements": [],
        "errors": [],
        "success": True
    }
    
    try:
        print("Rolling back RBAC enhancements...")
        
        # Drop triggers
        triggers_to_drop = [
            "enforce_super_admin_uniqueness",
            "enforce_system_user_isolation",
        ]
        
        for trigger in triggers_to_drop:
            cursor.execute(f"DROP TRIGGER IF EXISTS {trigger};")
            results["statements"].append(f"Dropped TRIGGER {trigger}")
        
        # Drop new tables
        cursor.execute("DROP TABLE IF EXISTS core_role_change_audit;")
        results["statements"].append("Dropped TABLE core_role_change_audit")
        
        cursor.execute("DROP TABLE IF EXISTS core_permission_change_audit;")
        results["statements"].append("Dropped TABLE core_permission_change_audit")
        
        # Note: We keep indexes for performance, but could drop them with:
        # DROP INDEX IF EXISTS idx_name;
        
        conn.commit()
        
    except Exception as e:
        results["errors"].append(f"Rollback error: {str(e)}")
        results["success"] = False
        conn.rollback()
    
    finally:
        conn.close()
    
    return results


def status(db_path: str) -> dict:
    """
    Check migration status.
    
    Returns:
        dict with migration status information
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    status_info = {
        "tables": [],
        "triggers": [],
        "indexes": [],
    }
    
    try:
        # Check tables
        cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name LIKE 'core_%'
        ORDER BY name
        """)
        
        status_info["tables"] = [row[0] for row in cursor.fetchall()]
        
        # Check triggers
        cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='trigger' AND name LIKE 'enforce_%'
        ORDER BY name
        """)
        
        status_info["triggers"] = [row[0] for row in cursor.fetchall()]
        
        # Check indexes
        cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index' AND name LIKE 'idx_%'
        ORDER BY name
        """)
        
        status_info["indexes"] = [row[0] for row in cursor.fetchall()]
        
    finally:
        conn.close()
    
    return status_info


if __name__ == "__main__":
    import sys
    
    # Default database path
    db_path = "backend/database/people_os.db"
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "up":
            print("Applying RBAC enhancement migrations...")
            result = migrate_up(db_path)
            
            print(f"\nMigration Status: {'✓ SUCCESS' if result['success'] else '✗ FAILED'}")
            print(f"Statements executed: {len(result['statements'])}")
            
            for stmt in result["statements"]:
                print(f"  ✓ {stmt}")
            
            if result["errors"]:
                print(f"\nWarnings/Errors: {len(result['errors'])}")
                for error in result["errors"]:
                    print(f"  ⚠ {error}")
        
        elif command == "down":
            print("Rolling back RBAC enhancements...")
            result = migrate_down(db_path)
            
            print(f"\nRollback Status: {'✓ SUCCESS' if result['success'] else '✗ FAILED'}")
            print(f"Statements executed: {len(result['statements'])}")
            
            for stmt in result["statements"]:
                print(f"  ✓ {stmt}")
        
        elif command == "status":
            print("RBAC Migration Status:")
            info = status(db_path)
            
            print(f"\nTables: {len(info['tables'])}")
            for table in info["tables"]:
                print(f"  ✓ {table}")
            
            print(f"\nTriggers: {len(info['triggers'])}")
            for trigger in info["triggers"]:
                print(f"  ✓ {trigger}")
            
            print(f"\nIndexes: {len(info['indexes'])}")
            for index in info["indexes"]:
                print(f"  ✓ {index}")
    
    else:
        print("Usage: python migrate_rbac.py [up|down|status]")
        print("  up     - Apply RBAC enhancements")
        print("  down   - Rollback RBAC enhancements")
        print("  status - Check migration status")
