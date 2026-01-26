"""
Comprehensive RBAC Verification Test Suite
===========================================

Tests for:
1. Root user system-level access
2. Super Admin organization-level access
3. Role hierarchy enforcement
4. Permission checking
5. Organization isolation
6. Audit trail completeness
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.rbac_enhanced import (
    validate_root_user_creation,
    validate_super_admin_uniqueness,
    validate_system_user_isolation,
    validate_organization_exists,
    validate_creator_authority,
    create_user_validated,
    update_user_role,
    prevent_super_admin_deletion,
    grant_permission,
    revoke_permission,
    filter_users_by_visibility,
    can_user_manage_role,
    list_superadmins_by_org,
)
from backend.permissions_config import ROLE_HIERARCHY, has_permission
from backend.shared.models import models


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def root_user_dict():
    """Create a Root user dictionary."""
    return {
        "id": "root-system-001",
        "username": "root",
        "role": "Root",
        "organization_id": None,
        "is_system_user": True,
    }


@pytest.fixture
def org_user_dict():
    """Create organization test data."""
    return {
        "id": "ORG-001",
        "code": "ORG001",
        "name": "Test Organization",
        "email": "org@test.local",
    }


@pytest.fixture
def super_admin_user_dict(org_user_dict):
    """Create a Super Admin user for test org."""
    return {
        "id": "sa-user-001",
        "username": "admin",
        "password": "password123",
        "role": "Super Admin",
        "organization_id": org_user_dict["id"],
        "is_system_user": False,
        "email": "admin@test.local",
    }


@pytest.fixture
def manager_user_dict(org_user_dict):
    """Create a Manager user for test org."""
    return {
        "id": "mgr-user-001",
        "username": "manager",
        "password": "password123",
        "role": "Manager",
        "organization_id": org_user_dict["id"],
        "is_system_user": False,
        "email": "manager@test.local",
    }


# ============================================================
# TESTS: ROOT USER VALIDATION
# ============================================================

class TestRootUserValidation:
    """Test Root user protection and validation."""
    
    def test_root_user_not_in_database(self, mock_db):
        """Root user should never appear in database."""
        # Setup: No Root user in DB
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = validate_root_user_creation(mock_db)
        assert result == True, "Root user validation should pass when no Root in DB"
    
    def test_root_user_in_database_fails_validation(self, mock_db, root_user_dict):
        """Validation should fail if Root user found in DB."""
        # Setup: Root user exists in DB
        mock_root = Mock()
        mock_root.id = root_user_dict["id"]
        mock_root.role = "Root"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_root
        
        result = validate_root_user_creation(mock_db)
        assert result == False, "Root user validation should fail if Root exists in DB"
    
    def test_only_one_root_user_allowed_in_system(self, mock_db):
        """System should support exactly one Root (in-memory)."""
        # Root is in-memory, so DB check should always be clear
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Multiple checks should all pass
        result1 = validate_root_user_creation(mock_db)
        result2 = validate_root_user_creation(mock_db)
        
        assert result1 == True
        assert result2 == True


# ============================================================
# TESTS: SUPER ADMIN VALIDATION
# ============================================================

class TestSuperAdminValidation:
    """Test Super Admin uniqueness and organization binding."""
    
    def test_no_super_admin_yet(self, mock_db, org_user_dict):
        """Before creation, validation should pass (no Super Admin)."""
        # Setup: No Super Admin for org
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        
        result = validate_super_admin_uniqueness(mock_db, org_user_dict["id"])
        assert result == True, "Uniqueness check should pass when no Super Admin exists"
    
    def test_one_super_admin_exists(self, mock_db, org_user_dict, super_admin_user_dict):
        """After creation, validation should pass (exactly one)."""
        # Setup: One Super Admin for org
        mock_db.query.return_value.filter.return_value.count.return_value = 1
        
        result = validate_super_admin_uniqueness(mock_db, org_user_dict["id"])
        assert result == True, "Uniqueness check should pass with exactly one Super Admin"
    
    def test_multiple_super_admins_fail_validation(self, mock_db, org_user_dict):
        """Validation should fail if multiple Super Admins found."""
        # Setup: Multiple Super Admins (corruption)
        mock_db.query.return_value.filter.return_value.count.return_value = 2
        
        result = validate_super_admin_uniqueness(mock_db, org_user_dict["id"])
        assert result == False, "Uniqueness check should fail with multiple Super Admins"
    
    def test_exclude_user_id_in_update(self, mock_db, org_user_dict):
        """Exclude current user when checking uniqueness during update."""
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        
        result = validate_super_admin_uniqueness(
            mock_db, 
            org_user_dict["id"],
            exclude_user_id="sa-user-001"
        )
        assert result == True


# ============================================================
# TESTS: SYSTEM USER ISOLATION
# ============================================================

class TestSystemUserIsolation:
    """Test system user isolation from organizations."""
    
    def test_system_user_with_org_fails(self):
        """System users cannot have organization_id."""
        user_data = {
            "username": "sysadmin",
            "role": "SystemAdmin",
            "is_system_user": True,
            "organization_id": "ORG-001"  # VIOLATION!
        }
        
        result = validate_system_user_isolation(user_data)
        assert result["valid"] == False
        assert "System users cannot be assigned" in result["errors"][0]
    
    def test_org_user_without_org_fails(self):
        """Organization users must have organization_id."""
        user_data = {
            "username": "manager",
            "role": "Manager",
            "is_system_user": False,
            "organization_id": None  # VIOLATION!
        }
        
        result = validate_system_user_isolation(user_data)
        assert result["valid"] == False
    
    def test_super_admin_must_be_org_user(self):
        """Super Admin is an organization user, not system user."""
        # Invalid: Super Admin as system user
        user_data = {
            "username": "admin",
            "role": "Super Admin",
            "is_system_user": True,
            "organization_id": "ORG-001"
        }
        
        result = validate_system_user_isolation(user_data)
        assert result["valid"] == False
    
    def test_valid_system_user_isolation(self):
        """Valid system user has no org assignment."""
        user_data = {
            "username": "sysadmin",
            "role": "SystemAdmin",
            "is_system_user": True,
            "organization_id": None
        }
        
        result = validate_system_user_isolation(user_data)
        assert result["valid"] == True
    
    def test_valid_org_user_isolation(self):
        """Valid org user has org assignment."""
        user_data = {
            "username": "manager",
            "role": "Manager",
            "is_system_user": False,
            "organization_id": "ORG-001"
        }
        
        result = validate_system_user_isolation(user_data)
        assert result["valid"] == True


# ============================================================
# TESTS: CREATOR AUTHORITY
# ============================================================

class TestCreatorAuthority:
    """Test role hierarchy enforcement for user creation."""
    
    def test_root_can_create_any_role(self):
        """Root can create any non-Root user."""
        assert validate_creator_authority("Root", "Super Admin") == True
        assert validate_creator_authority("Root", "Manager") == True
        assert validate_creator_authority("Root", "User") == True
    
    def test_super_admin_can_create_lower_roles(self):
        """Super Admin can create Manager, User, etc."""
        assert validate_creator_authority("Super Admin", "Manager") == True
        assert validate_creator_authority("Super Admin", "User") == True
    
    def test_super_admin_cannot_create_super_admin(self):
        """Super Admin cannot create another Super Admin."""
        assert validate_creator_authority("Super Admin", "Super Admin") == False
    
    def test_manager_cannot_create_admin(self):
        """Manager cannot create Super Admin."""
        assert validate_creator_authority("Manager", "Super Admin") == False
    
    def test_manager_can_create_user(self):
        """Manager can create User role."""
        assert validate_creator_authority("Manager", "User") == True
    
    def test_none_role_cannot_create(self):
        """User with None role cannot create anyone."""
        assert validate_creator_authority(None, "User") == False
    
    def test_invalid_role_cannot_create(self):
        """User with invalid role cannot create."""
        assert validate_creator_authority("InvalidRole", "User") == False
    
    def test_cannot_create_root(self):
        """No one can create Root user."""
        assert validate_creator_authority("Root", "Root") == False
        assert validate_creator_authority("Super Admin", "Root") == False


# ============================================================
# TESTS: ORGANIZATION EXISTENCE
# ============================================================

class TestOrganizationValidation:
    """Test organization existence validation."""
    
    def test_organization_exists(self, mock_db, org_user_dict):
        """Should return org if it exists."""
        mock_org = Mock(spec=models.DBOrganization)
        mock_org.id = org_user_dict["id"]
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_org
        
        result = validate_organization_exists(mock_db, org_user_dict["id"])
        assert result.id == org_user_dict["id"]
    
    def test_organization_not_found(self, mock_db, org_user_dict):
        """Should raise HTTPException if org not found."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            validate_organization_exists(mock_db, "INVALID-ORG")
        
        assert exc_info.value.status_code == 404


# ============================================================
# TESTS: PERMISSION CHECKING
# ============================================================

class TestPermissionChecking:
    """Test permission enforcement."""
    
    def test_root_has_all_permissions(self, root_user_dict):
        """Root user has all permissions."""
        assert has_permission("Root", "any_permission") == True
        assert has_permission("Root", "admin_system") == True
    
    def test_super_admin_has_all_permissions(self):
        """Super Admin has all permissions (org-scoped)."""
        assert has_permission("Super Admin", "any_permission") == True
    
    def test_regular_role_needs_explicit_permission(self):
        """Regular roles only have permissions explicitly granted."""
        # Manager has no default permissions
        assert has_permission("Manager", "view_employees") == False
        assert has_permission("Manager", "admin_system") == False
    
    def test_business_admin_has_default_permission(self):
        """Business Admin has view_employees by default."""
        assert has_permission("Business Admin", "view_employees") == True


# ============================================================
# TESTS: USER ROLE MANAGEMENT
# ============================================================

class TestUserRoleManagement:
    """Test user role updates and constraints."""
    
    def test_prevent_super_admin_deletion_last(self, mock_db, super_admin_user_dict, org_user_dict):
        """Should prevent deletion if user is last Super Admin."""
        mock_user = Mock(spec=models.DBUser)
        mock_user.id = super_admin_user_dict["id"]
        mock_user.role = "Super Admin"
        mock_user.organization_id = org_user_dict["id"]
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value.filter.return_value.count.return_value = 0  # No other admins
        
        result = prevent_super_admin_deletion(mock_db, super_admin_user_dict["id"])
        assert result == org_user_dict["id"], "Should return org_id when user is last Super Admin"
    
    def test_allow_super_admin_deletion_not_last(self, mock_db, super_admin_user_dict):
        """Should allow deletion if there are other Super Admins."""
        mock_user = Mock(spec=models.DBUser)
        mock_user.id = super_admin_user_dict["id"]
        mock_user.role = "Super Admin"
        mock_user.organization_id = "ORG-001"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value.filter.return_value.count.return_value = 1  # Another admin exists
        
        result = prevent_super_admin_deletion(mock_db, super_admin_user_dict["id"])
        assert result is None, "Should return None when other Super Admins exist"
    
    def test_allow_non_admin_user_deletion(self, mock_db, manager_user_dict):
        """Should allow deletion of non-admin users."""
        mock_user = Mock(spec=models.DBUser)
        mock_user.id = manager_user_dict["id"]
        mock_user.role = "Manager"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = prevent_super_admin_deletion(mock_db, manager_user_dict["id"])
        assert result is None, "Should allow deletion of non-Super-Admin users"


# ============================================================
# TESTS: USER VISIBILITY FILTERING
# ============================================================

class TestUserVisibilityFiltering:
    """Test role-based user visibility filters."""
    
    def test_root_sees_all_users(self):
        """Root user sees all users in system."""
        mock_query = Mock()
        root_user = {"role": "Root", "organization_id": None}
        
        result = filter_users_by_visibility(mock_query, root_user)
        # Root query should not be filtered
        assert result == mock_query
    
    def test_super_admin_sees_org_and_system_users(self):
        """Super Admin sees users in their org + system users."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        
        super_admin = {"role": "Super Admin", "organization_id": "ORG-001"}
        
        result = filter_users_by_visibility(mock_query, super_admin)
        # Should filter to own org + system users
        mock_query.filter.assert_called()
    
    def test_regular_user_sees_only_own_org(self):
        """Regular users see only users in their org."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        
        manager = {"role": "Manager", "organization_id": "ORG-001"}
        
        result = filter_users_by_visibility(mock_query, manager)
        mock_query.filter.assert_called()


# ============================================================
# TESTS: USER MANAGEMENT AUTHORITY
# ============================================================

class TestUserManagementAuthority:
    """Test who can manage which users."""
    
    def test_root_can_manage_anyone(self, root_user_dict, manager_user_dict):
        """Root can manage any user."""
        mock_target = Mock(spec=models.DBUser)
        mock_target.organization_id = "ANY-ORG"
        
        result = can_user_manage_role(root_user_dict, mock_target)
        assert result == True
    
    def test_super_admin_can_manage_own_org_users(self, super_admin_user_dict, manager_user_dict):
        """Super Admin can manage users in their org."""
        super_admin_dict = {
            "role": "Super Admin",
            "organization_id": "ORG-001"
        }
        
        mock_target = Mock(spec=models.DBUser)
        mock_target.organization_id = "ORG-001"  # Same org
        
        result = can_user_manage_role(super_admin_dict, mock_target)
        assert result == True
    
    def test_super_admin_cannot_manage_other_org_users(self, super_admin_user_dict):
        """Super Admin cannot manage users in other orgs."""
        super_admin_dict = {
            "role": "Super Admin",
            "organization_id": "ORG-001"
        }
        
        mock_target = Mock(spec=models.DBUser)
        mock_target.organization_id = "ORG-002"  # Different org
        
        result = can_user_manage_role(super_admin_dict, mock_target)
        assert result == False
    
    def test_manager_cannot_manage_anyone(self, manager_user_dict):
        """Manager cannot manage any users."""
        manager_dict = {
            "role": "Manager",
            "organization_id": "ORG-001"
        }
        
        mock_target = Mock(spec=models.DBUser)
        mock_target.organization_id = "ORG-001"
        
        result = can_user_manage_role(manager_dict, mock_target)
        assert result == False


# ============================================================
# TESTS: SUPER ADMIN LISTING
# ============================================================

class TestSuperAdminListing:
    """Test listing Super Admins across organizations."""
    
    def test_list_superadmins_by_org(self, mock_db, org_user_dict):
        """Should return dict mapping org_id to Super Admin."""
        mock_admin1 = Mock(spec=models.DBUser)
        mock_admin1.organization_id = "ORG-001"
        
        mock_admin2 = Mock(spec=models.DBUser)
        mock_admin2.organization_id = "ORG-002"
        
        mock_db.query.return_value.filter.return_value.all.return_value = [
            mock_admin1, mock_admin2
        ]
        
        result = list_superadmins_by_org(mock_db)
        
        assert result["ORG-001"] == mock_admin1
        assert result["ORG-002"] == mock_admin2


# ============================================================
# INTEGRATION TESTS
# ============================================================

class TestRBACIntegration:
    """Integration tests for complete RBAC workflows."""
    
    def test_complete_user_creation_workflow(self):
        """Test full user creation with all validations."""
        # This would require a real database setup
        # Placeholder for integration test
        pass
    
    def test_complete_role_change_workflow(self):
        """Test full role change with audit trail."""
        # This would require a real database setup
        # Placeholder for integration test
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
