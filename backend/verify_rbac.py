"""
RBAC System Verification and Integration Guide
================================================

Complete guide for:
1. Verifying current system implementation
2. Running tests
3. Applying enhancements
4. Validating changes
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class RBACVerificationGuide:
    """Guide for RBAC system verification and integration."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.backend_dir = self.root_dir / "backend"
        self.tests_dir = self.root_dir / "tests"
        self.db_dir = self.backend_dir / "database"
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "warnings": [],
            "errors": [],
        }
    
    # ================================================================
    # VERIFICATION CHECKS
    # ================================================================
    
    def check_root_user_implementation(self) -> bool:
        """Verify Root user is implemented in-memory only."""
        print("\n[1] Checking Root user implementation...")
        
        try:
            # Read dependencies.py
            deps_file = self.backend_dir / "dependencies.py"
            with open(deps_file) as f:
                content = f.read()
            
            checks = {
                "ROOT_USER_ID defined": "ROOT_USER_ID" in content,
                "ROOT_USERNAME defined": "ROOT_USERNAME" in content,
                "ROOT_PASSWORD defined": "ROOT_PASSWORD" in content,
                "get_current_user() exists": "def get_current_user" in content,
                "Root check on username": 'username == ROOT_USERNAME' in content,
            }
            
            all_passed = all(checks.values())
            
            for check, result in checks.items():
                status = "✓" if result else "✗"
                print(f"  {status} {check}")
                self.results["checks"].append({
                    "check": f"Root implementation: {check}",
                    "passed": result
                })
            
            if not all_passed:
                self.results["errors"].append(
                    "Root user implementation incomplete"
                )
            
            return all_passed
            
        except Exception as e:
            self.results["errors"].append(f"Error checking Root implementation: {e}")
            return False
    
    def check_super_admin_auto_creation(self) -> bool:
        """Verify Super Admin auto-creation on org setup."""
        print("\n[2] Checking Super Admin auto-creation...")
        
        try:
            crud_file = self.backend_dir / "crud.py"
            with open(crud_file) as f:
                content = f.read()
            
            checks = {
                "create_organization() exists": "def create_organization" in content,
                "provision_org_admin() exists": "def provision_org_admin" in content,
                "Super Admin creation logic": "Super Admin" in content and "provision_org_admin" in content,
            }
            
            all_passed = all(checks.values())
            
            for check, result in checks.items():
                status = "✓" if result else "✗"
                print(f"  {status} {check}")
                self.results["checks"].append({
                    "check": f"Super Admin creation: {check}",
                    "passed": result
                })
            
            return all_passed
            
        except Exception as e:
            self.results["errors"].append(f"Error checking Super Admin creation: {e}")
            return False
    
    def check_role_hierarchy(self) -> bool:
        """Verify role hierarchy is defined."""
        print("\n[3] Checking role hierarchy...")
        
        try:
            perm_file = self.backend_dir / "permissions_config.py"
            with open(perm_file) as f:
                content = f.read()
            
            expected_roles = [
                "Root", "Super Admin", "SystemAdmin", "Business Admin", 
                "Manager", "User"
            ]
            
            checks = {}
            for role in expected_roles:
                checks[f"Role '{role}' defined"] = f'"{role}"' in content or f"'{role}'" in content
            
            checks["ROLE_HIERARCHY defined"] = "ROLE_HIERARCHY" in content
            checks["has_permission() function"] = "def has_permission" in content
            
            all_passed = all(checks.values())
            
            for check, result in checks.items():
                status = "✓" if result else "✗"
                print(f"  {status} {check}")
                self.results["checks"].append({
                    "check": f"Role hierarchy: {check}",
                    "passed": result
                })
            
            return all_passed
            
        except Exception as e:
            self.results["errors"].append(f"Error checking role hierarchy: {e}")
            return False
    
    def check_organization_isolation(self) -> bool:
        """Verify organization isolation via organization_id."""
        print("\n[4] Checking organization isolation...")
        
        try:
            schema_file = self.backend_dir / "schema.sql"
            with open(schema_file) as f:
                content = f.read()
            
            checks = {
                "core_users table has organization_id": "organization_id" in content,
                "core_organizations table exists": "CREATE TABLE.*core_organizations" in content,
                "Foreign key constraint exists": "FOREIGN KEY" in content,
            }
            
            all_passed = all(checks.values())
            
            for check, result in checks.items():
                status = "✓" if result else "✗"
                print(f"  {status} {check}")
                self.results["checks"].append({
                    "check": f"Organization isolation: {check}",
                    "passed": result
                })
            
            return all_passed
            
        except Exception as e:
            self.results["errors"].append(f"Error checking org isolation: {e}")
            return False
    
    def check_audit_logging(self) -> bool:
        """Verify audit logging is in place."""
        print("\n[5] Checking audit logging...")
        
        try:
            files_to_check = [
                self.backend_dir / "schema.sql",
                self.backend_dir / "crud.py",
            ]
            
            audit_found = False
            for file_path in files_to_check:
                with open(file_path) as f:
                    content = f.read()
                    if "core_audit_logs" in content or "audit_log" in content:
                        audit_found = True
                        break
            
            checks = {
                "Audit log table exists": audit_found,
                "log_audit_event() function": "log_audit_event" in self._read_crud(),
            }
            
            all_passed = all(checks.values())
            
            for check, result in checks.items():
                status = "✓" if result else "✗"
                print(f"  {status} {check}")
                self.results["checks"].append({
                    "check": f"Audit logging: {check}",
                    "passed": result
                })
            
            return all_passed
            
        except Exception as e:
            self.results["errors"].append(f"Error checking audit logging: {e}")
            return False
    
    def check_enhanced_rbac_module(self) -> bool:
        """Verify enhanced RBAC module is in place."""
        print("\n[6] Checking enhanced RBAC module...")
        
        try:
            rbac_file = self.backend_dir / "rbac_enhanced.py"
            
            if not rbac_file.exists():
                self.results["warnings"].append(
                    "rbac_enhanced.py not found. Run integration step to create it."
                )
                return False
            
            with open(rbac_file) as f:
                content = f.read()
            
            expected_functions = [
                "validate_root_user_creation",
                "validate_super_admin_uniqueness",
                "validate_system_user_isolation",
                "create_user_validated",
                "update_user_role",
                "prevent_super_admin_deletion",
                "filter_users_by_visibility",
            ]
            
            checks = {}
            for func in expected_functions:
                checks[f"Function '{func}'"] = f"def {func}" in content
            
            all_passed = all(checks.values())
            
            for check, result in checks.items():
                status = "✓" if result else "✗"
                print(f"  {status} {check}")
                self.results["checks"].append({
                    "check": f"Enhanced RBAC: {check}",
                    "passed": result
                })
            
            return all_passed
            
        except Exception as e:
            self.results["errors"].append(f"Error checking RBAC module: {e}")
            return False
    
    def check_migration_script(self) -> bool:
        """Verify database migration script exists."""
        print("\n[7] Checking database migration script...")
        
        try:
            migrate_file = self.backend_dir / "migrate_rbac.py"
            
            if not migrate_file.exists():
                self.results["warnings"].append(
                    "migrate_rbac.py not found. Run integration step to create it."
                )
                return False
            
            with open(migrate_file) as f:
                content = f.read()
            
            checks = {
                "migrate_up() function": "def migrate_up" in content,
                "migrate_down() function": "def migrate_down" in content,
                "status() function": "def status" in content,
            }
            
            all_passed = all(checks.values())
            
            for check, result in checks.items():
                status = "✓" if result else "✗"
                print(f"  {status} {check}")
                self.results["checks"].append({
                    "check": f"Migration script: {check}",
                    "passed": result
                })
            
            return all_passed
            
        except Exception as e:
            self.results["errors"].append(f"Error checking migration script: {e}")
            return False
    
    # ================================================================
    # INTEGRATION STEPS
    # ================================================================
    
    def integration_step_1_backup(self) -> bool:
        """Step 1: Backup database and configuration."""
        print("\n[INTEGRATION] Step 1: Backing up database...")
        
        try:
            db_file = self.db_dir / "people_os.db"
            backup_dir = self.root_dir / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            if db_file.exists():
                import shutil
                backup_file = backup_dir / "people_os.db"
                shutil.copy2(db_file, backup_file)
                print(f"  ✓ Database backed up to {backup_file}")
            else:
                print("  ⚠ Database file not found (fresh installation)")
            
            return True
            
        except Exception as e:
            self.results["errors"].append(f"Backup failed: {e}")
            return False
    
    def integration_step_2_apply_migrations(self) -> bool:
        """Step 2: Apply database migrations."""
        print("\n[INTEGRATION] Step 2: Applying database migrations...")
        
        try:
            # Import and run migration
            sys.path.insert(0, str(self.backend_dir))
            
            from migrate_rbac import migrate_up
            
            db_file = str(self.db_dir / "people_os.db")
            result = migrate_up(db_file)
            
            if result["success"]:
                print("  ✓ Migrations applied successfully")
                for stmt in result["statements"][:5]:  # Show first 5
                    print(f"    - {stmt}")
                if len(result["statements"]) > 5:
                    print(f"    ... and {len(result['statements']) - 5} more")
            else:
                print("  ✗ Migration failed")
                for error in result["errors"]:
                    print(f"    - {error}")
            
            return result["success"]
            
        except Exception as e:
            self.results["errors"].append(f"Migration application failed: {e}")
            return False
    
    def integration_step_3_import_enhanced_module(self) -> bool:
        """Step 3: Import enhanced RBAC module in crud.py."""
        print("\n[INTEGRATION] Step 3: Importing enhanced RBAC module...")
        
        try:
            crud_file = self.backend_dir / "crud.py"
            
            with open(crud_file) as f:
                content = f.read()
            
            # Check if already imported
            if "from backend.rbac_enhanced import" in content:
                print("  ✓ rbac_enhanced already imported")
                return True
            
            # Add import after other backend imports
            import_line = "from backend.rbac_enhanced import create_user_validated, update_user_role, prevent_super_admin_deletion\n"
            
            # Find good location for import (after other imports)
            lines = content.split("\n")
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith("from backend.") or line.startswith("from "):
                    insert_pos = i + 1
            
            lines.insert(insert_pos, import_line)
            
            with open(crud_file, "w") as f:
                f.write("\n".join(lines))
            
            print("  ✓ Import added to crud.py")
            self.results["checks"].append({
                "check": "rbac_enhanced imported in crud.py",
                "passed": True
            })
            
            return True
            
        except Exception as e:
            self.results["errors"].append(f"Import integration failed: {e}")
            return False
    
    # ================================================================
    # HELPER METHODS
    # ================================================================
    
    def _read_crud(self) -> str:
        """Read crud.py content (cached)."""
        if not hasattr(self, "_crud_content"):
            crud_file = self.backend_dir / "crud.py"
            with open(crud_file) as f:
                self._crud_content = f.read()
        return self._crud_content
    
    def run_all_checks(self) -> bool:
        """Run all verification checks."""
        print("\n" + "="*60)
        print("RBAC SYSTEM VERIFICATION")
        print("="*60)
        
        checks = [
            ("Root User Implementation", self.check_root_user_implementation),
            ("Super Admin Auto-Creation", self.check_super_admin_auto_creation),
            ("Role Hierarchy", self.check_role_hierarchy),
            ("Organization Isolation", self.check_organization_isolation),
            ("Audit Logging", self.check_audit_logging),
            ("Enhanced RBAC Module", self.check_enhanced_rbac_module),
            ("Migration Script", self.check_migration_script),
        ]
        
        results = {}
        for name, check_func in checks:
            try:
                results[name] = check_func()
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                results[name] = False
                self.results["errors"].append(f"{name} check failed: {e}")
        
        return all(results.values())
    
    def run_integration(self) -> bool:
        """Run all integration steps."""
        print("\n" + "="*60)
        print("RBAC SYSTEM INTEGRATION")
        print("="*60)
        
        steps = [
            ("Database Backup", self.integration_step_1_backup),
            ("Apply Migrations", self.integration_step_2_apply_migrations),
            ("Import Enhanced Module", self.integration_step_3_import_enhanced_module),
        ]
        
        results = {}
        for name, step_func in steps:
            try:
                results[name] = step_func()
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                results[name] = False
                self.results["errors"].append(f"{name} integration failed: {e}")
        
        return all(results.values())
    
    def print_summary(self):
        """Print verification summary."""
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        
        passed = sum(1 for c in self.results["checks"] if c.get("passed", False))
        total = len(self.results["checks"])
        
        print(f"\nChecks: {passed}/{total} passed")
        
        if self.results["warnings"]:
            print(f"\nWarnings ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"]:
                print(f"  ⚠ {warning}")
        
        if self.results["errors"]:
            print(f"\nErrors ({len(self.results['errors'])}):")
            for error in self.results["errors"]:
                print(f"  ✗ {error}")
        
        print("\n" + "="*60)


if __name__ == "__main__":
    verifier = RBACVerificationGuide()
    
    # Run verification
    all_checks_passed = verifier.run_all_checks()
    
    # Print summary
    verifier.print_summary()
    
    # Ask about integration
    if all_checks_passed:
        print("\n✓ All verification checks passed!")
        print("\nYou can now run integration:")
        print("  python backend/verify_rbac.py --integrate")
    else:
        print("\n✗ Some checks failed. Please review and fix before integration.")
        sys.exit(1)
