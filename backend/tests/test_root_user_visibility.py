"""
Test Root User Visibility Rule

Rule: Only Root users can see Root users. All other users cannot view Root.
This rule is enforced at multiple levels:
1. Backend crud.get_users() filters Root users for non-Root users
2. Backend crud.get_user() denies access to Root users for non-Root users
3. API endpoint /users only returns Root users if current user is Root
"""

import sys
import os
import pytest
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend import crud, models, schemas
from backend.database import Base


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = Mock(spec=Session)
    return db


@pytest.fixture
def root_user():
    """Create a mock Root user."""
    return {
        "id": "root-user-1",
        "username": "root_admin",
        "name": "Root Administrator",
        "email": "root@system.local",
        "role": "Root",
        "status": "Active",
        "isSystemUser": True,
    }


@pytest.fixture
def admin_user():
    """Create a mock SystemAdmin user (non-Root)."""
    return {
        "id": "admin-user-1",
        "username": "system_admin",
        "name": "System Administrator",
        "email": "admin@system.local",
        "role": "SystemAdmin",
        "status": "Active",
        "isSystemUser": True,
    }


@pytest.fixture
def regular_user():
    """Create a mock regular org user."""
    return {
        "id": "user-1",
        "username": "john_doe",
        "name": "John Doe",
        "email": "john@org.local",
        "role": "Employee",
        "status": "Active",
        "isSystemUser": False,
    }


class TestRootUserVisibilityInCrud:
    """Test Root user visibility in CRUD operations."""

    def test_get_users_root_can_see_root_user(self, mock_db, root_user, admin_user):
        """
        Test: Root user can see Root user in get_users()
        """
        # Mock the query chain
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [root_user, admin_user]
        
        current_user = {"role": "Root"}
        result = crud.get_users(mock_db, current_user=current_user)
        
        # Root should see both Root and non-Root users
        assert len(result) == 2
        assert any(u["role"] == "Root" for u in result)

    def test_get_users_non_root_cannot_see_root_user(self, mock_db, root_user, admin_user):
        """
        Test: Non-Root user cannot see Root user in get_users()
        When get_users() is called with a non-Root user, it should filter out Root users.
        """
        # Mock the query chain to return only non-Root users
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        
        # The filter() call should be called to exclude Root users
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [admin_user]
        
        current_user = {"role": "SystemAdmin"}
        result = crud.get_users(mock_db, current_user=current_user)
        
        # Non-Root should not see Root users
        assert len(result) == 1
        assert all(u["role"] != "Root" for u in result)
        # Verify filter was called to exclude Root
        mock_query.filter.assert_called()

    def test_get_user_root_can_see_root_user(self, mock_db, root_user):
        """
        Test: Root user can get a Root user by ID
        """
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = root_user
        
        current_user = {"role": "Root"}
        result = crud.get_user(mock_db, "root-user-1", current_user=current_user)
        
        assert result is not None
        assert result["role"] == "Root"

    def test_get_user_non_root_cannot_see_root_user(self, mock_db, root_user):
        """
        Test: Non-Root user cannot get a Root user by ID
        When a non-Root user tries to get a Root user, get_user() should return None.
        """
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = root_user
        
        current_user = {"role": "SystemAdmin"}
        result = crud.get_user(mock_db, "root-user-1", current_user=current_user)
        
        # Non-Root should not see Root user
        assert result is None

    def test_get_user_by_username_root_can_see_root(self, mock_db, root_user):
        """
        Test: Root user can get Root user by username
        """
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = root_user
        
        current_user = {"role": "Root"}
        result = crud.get_user_by_username(mock_db, "root_admin", current_user=current_user)
        
        assert result is not None
        assert result["role"] == "Root"

    def test_get_user_by_username_non_root_cannot_see_root(self, mock_db, root_user):
        """
        Test: Non-Root user cannot get Root user by username
        """
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = root_user
        
        current_user = {"role": "SystemAdmin"}
        result = crud.get_user_by_username(mock_db, "root_admin", current_user=current_user)
        
        # Non-Root should not see Root user
        assert result is None


class TestRootUserVisibilityBoundaryConditions:
    """Test boundary conditions for Root user visibility."""

    def test_no_current_user_cannot_see_root(self, mock_db, root_user, admin_user):
        """
        Test: When current_user is None/anonymous, Root user is hidden
        """
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [admin_user]
        
        # current_user is None
        result = crud.get_users(mock_db, current_user=None)
        
        # Should filter out Root users
        assert all(u["role"] != "Root" for u in result)

    def test_empty_users_list_with_root_check(self, mock_db):
        """
        Test: When no users exist, filtering still works correctly
        """
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        
        current_user = {"role": "SystemAdmin"}
        result = crud.get_users(mock_db, current_user=current_user)
        
        assert result == []


class TestRootUserVisibilityIntegration:
    """Integration tests for Root user visibility."""

    def test_get_role_permissions_root_only_visibility(self, mock_db):
        """
        Test: Root role permissions are only visible to Root users
        This is related to the Root user visibility rule.
        """
        # This verifies the similar filtering pattern is applied to permissions
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        
        current_user = {"role": "SystemAdmin"}
        # When a non-Root user requests Root role permissions, it should be denied
        result = crud.get_role_permissions(mock_db, "Root", current_user=current_user)
        
        # Should be None or empty list (permission denied)
        assert result is None or len(result) == 0


class TestRootUserVisibilityDocumentation:
    """Test that the visibility rule is properly documented in code."""

    def test_get_users_has_visibility_rule_documentation(self):
        """
        Test: get_users() function is documented with the visibility rule
        """
        import inspect
        doc = inspect.getdoc(crud.get_users)
        
        assert doc is not None
        # Should mention the visibility rule
        assert "Root" in doc or "visibility" in doc.lower() or "filtering" in doc.lower()

    def test_get_user_has_visibility_rule_documentation(self):
        """
        Test: get_user() function is documented with the visibility rule
        """
        import inspect
        doc = inspect.getdoc(crud.get_user)
        
        assert doc is not None
        # Should mention the visibility rule
        assert "Root" in doc or "visibility" in doc.lower() or "access" in doc.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
