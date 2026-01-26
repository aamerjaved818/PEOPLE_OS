"""
Security tests for OAuth2, RBAC, audit logging, and encryption.

Tests cover:
- JWT token generation and validation
- Refresh token mechanism
- Role-based access control
- Permission checking
- Audit logging
- Data encryption/decryption
"""

import pytest
from datetime import datetime, timedelta
from jose import JWTError

from backend.security.oauth2 import (
    create_access_token,
    create_refresh_token,
    verify_token,
    refresh_access_token,
    Token,
)
from backend.security.rbac import (
    Role,
    Permission,
    RBACManager,
    check_permission,
    get_user_roles,
)
from backend.security.audit_logger import (
    AuditLogger,
    AuditAction,
)
from backend.security.encryption import (
    EncryptionManager,
    encrypt_field,
    decrypt_field,
    EncryptionManager,
)


# ══════════════════════════════════════════════════════════════════════════════
# OAuth2/JWT Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestJWTTokenGeneration:
    """Test JWT token generation"""

    def test_create_access_token(self):
        """Test creating access token"""
        token = create_access_token(
            user_id=1,
            username="testuser",
            email="test@example.com",
            roles=["employee"],
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        """Test creating refresh token"""
        token = create_refresh_token(user_id=1, username="testuser")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_access_token_contains_user_data(self):
        """Test that access token contains user data"""
        token = create_access_token(
            user_id=1,
            username="testuser",
            email="test@example.com",
            roles=["employee", "manager"],
        )
        token_data = verify_token(token, token_type="access")
        assert token_data.user_id == 1
        assert token_data.username == "testuser"
        assert token_data.email == "test@example.com"
        assert "employee" in token_data.roles
        assert "manager" in token_data.roles

    def test_token_has_expiration(self):
        """Test that token has expiration time"""
        token = create_access_token(
            user_id=1,
            username="testuser",
            email="test@example.com",
            roles=[],
        )
        token_data = verify_token(token, token_type="access")
        assert token_data.exp is not None
        assert token_data.exp > datetime.utcnow()

    def test_token_type_validation(self):
        """Test that token type is validated"""
        access_token = create_access_token(
            user_id=1,
            username="testuser",
            email="test@example.com",
            roles=[],
        )
        # Should fail to validate as refresh token
        with pytest.raises(Exception):
            verify_token(access_token, token_type="refresh")


class TestTokenRefresh:
    """Test refresh token functionality"""

    def test_refresh_access_token(self):
        """Test refreshing access token with refresh token"""
        refresh_token = create_refresh_token(user_id=1, username="testuser")
        new_tokens = refresh_access_token(
            refresh_token=refresh_token,
            user_id=1,
            username="testuser",
            email="test@example.com",
            roles=["employee"],
        )
        assert isinstance(new_tokens, Token)
        assert new_tokens.access_token != refresh_token
        assert new_tokens.refresh_token != refresh_token
        assert new_tokens.token_type == "bearer"

    def test_new_access_token_valid(self):
        """Test that new access token from refresh is valid"""
        refresh_token = create_refresh_token(user_id=1, username="testuser")
        new_tokens = refresh_access_token(
            refresh_token=refresh_token,
            user_id=1,
            username="testuser",
            email="test@example.com",
            roles=["employee"],
        )
        token_data = verify_token(new_tokens.access_token, token_type="access")
        assert token_data.user_id == 1
        assert token_data.username == "testuser"

    def test_invalid_refresh_token_rejected(self):
        """Test that invalid refresh token is rejected"""
        with pytest.raises(Exception):
            refresh_access_token(
                refresh_token="invalid-token",
                user_id=1,
                username="testuser",
                email="test@example.com",
                roles=["employee"],
            )


# ══════════════════════════════════════════════════════════════════════════════
# RBAC Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestRoleDefinitions:
    """Test role definitions"""

    def test_all_roles_defined(self):
        """Test that all roles are defined"""
        roles = [r.value for r in Role]
        assert "admin" in roles
        assert "hr_manager" in roles
        assert "department_manager" in roles
        assert "employee" in roles
        assert "viewer" in roles

    def test_all_permissions_defined(self):
        """Test that all permissions are defined"""
        permissions = [p.value for p in Permission]
        assert "employee:view" in permissions
        assert "employee:create" in permissions
        assert "employee:delete" in permissions
        assert "audit:view" in permissions


class TestRBACPermissions:
    """Test RBAC permission checking"""

    def test_admin_has_all_permissions(self):
        """Test that admin has all permissions"""
        assert check_permission(["admin"], Permission.EMPLOYEE_CREATE)
        assert check_permission(["admin"], Permission.SYSTEM_CONFIG)
        assert check_permission(["admin"], Permission.AUDIT_LOG_VIEW)

    def test_hr_manager_has_correct_permissions(self):
        """Test HR manager permissions"""
        assert check_permission(["hr_manager"], Permission.EMPLOYEE_CREATE)
        assert check_permission(["hr_manager"], Permission.DEPARTMENT_UPDATE)
        assert check_permission(["hr_manager"], Permission.AUDIT_LOG_VIEW)

    def test_employee_has_limited_permissions(self):
        """Test employee has limited permissions"""
        assert check_permission(["employee"], Permission.EMPLOYEE_VIEW)
        assert check_permission(["employee"], Permission.DEPARTMENT_VIEW)
        assert not check_permission(["employee"], Permission.EMPLOYEE_DELETE)
        assert not check_permission(["employee"], Permission.SYSTEM_CONFIG)

    def test_multiple_roles_union_permissions(self):
        """Test that multiple roles grant union of permissions"""
        roles = ["employee", "department_manager"]
        assert check_permission(roles, Permission.EMPLOYEE_VIEW)
        assert check_permission(roles, Permission.SHIFT_CREATE)

    def test_invalid_role_ignored(self):
        """Test that invalid roles are ignored"""
        roles = ["invalid_role", "employee"]
        assert check_permission(roles, Permission.EMPLOYEE_VIEW)

    def test_empty_roles_no_permissions(self):
        """Test that empty roles have no permissions"""
        assert not check_permission([], Permission.EMPLOYEE_VIEW)


class TestRBACManager:
    """Test RBACManager class"""

    def test_get_role_permissions(self):
        """Test getting permissions for a role"""
        admin_perms = RBACManager.get_role_permissions(Role.ADMIN)
        assert Permission.EMPLOYEE_CREATE in admin_perms
        assert Permission.SYSTEM_CONFIG in admin_perms
        assert len(admin_perms) > 0

    def test_has_permission_method(self):
        """Test has_permission method"""
        assert RBACManager.has_permission(["admin"], Permission.EMPLOYEE_DELETE)
        assert not RBACManager.has_permission(["viewer"], Permission.EMPLOYEE_DELETE)

    def test_get_user_roles(self):
        """Test getting Role enums from strings"""
        roles = get_user_roles(["admin", "employee"])
        assert Role.ADMIN in roles
        assert Role.EMPLOYEE in roles


# ══════════════════════════════════════════════════════════════════════════════
# Audit Logging Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestAuditLogging:
    """Test audit logging functionality"""

    def test_log_employee_create(self):
        """Test logging employee creation"""
        employee_data = {"name": "John Doe", "email": "john@example.com"}
        log_entry = AuditLogger.log_action(
            action=AuditAction.EMPLOYEE_CREATE,
            user_id=1,
            username="admin",
            resource_type="employee",
            resource_id=5,
            after_state=employee_data,
            details="Created new employee",
        )
        assert log_entry["action"] == AuditAction.EMPLOYEE_CREATE.value
        assert log_entry["user_id"] == 1
        assert log_entry["resource_id"] == 5
        assert log_entry["after_state"] == employee_data

    def test_log_employee_update(self):
        """Test logging employee update"""
        before = {"name": "John Doe", "email": "john@example.com"}
        after = {"name": "John Smith", "email": "john@example.com"}
        log_entry = AuditLogger.log_action(
            action=AuditAction.EMPLOYEE_UPDATE,
            user_id=1,
            username="admin",
            resource_type="employee",
            resource_id=5,
            before_state=before,
            after_state=after,
        )
        assert log_entry["before_state"] == before
        assert log_entry["after_state"] == after

    def test_log_employee_delete(self):
        """Test logging employee deletion"""
        employee_data = {"name": "John Doe"}
        log_entry = AuditLogger.log_action(
            action=AuditAction.EMPLOYEE_DELETE,
            user_id=1,
            username="admin",
            resource_type="employee",
            resource_id=5,
            before_state=employee_data,
        )
        assert log_entry["action"] == AuditAction.EMPLOYEE_DELETE.value
        assert log_entry["before_state"] == employee_data

    def test_log_role_change(self):
        """Test logging role changes"""
        log_entry = AuditLogger.log_action(
            action=AuditAction.USER_ROLE_CHANGE,
            user_id=1,
            username="admin",
            resource_type="user",
            resource_id=3,
            before_state={"roles": ["employee"]},
            after_state={"roles": ["employee", "manager"]},
        )
        assert log_entry["action"] == AuditAction.USER_ROLE_CHANGE.value

    def test_audit_entry_has_timestamp(self):
        """Test that audit entries have timestamps"""
        log_entry = AuditLogger.log_action(
            action=AuditAction.USER_LOGIN,
            user_id=1,
            username="testuser",
            resource_type="user",
            resource_id=1,
        )
        assert "timestamp" in log_entry
        assert log_entry["timestamp"] is not None


# ══════════════════════════════════════════════════════════════════════════════
# Encryption Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestEncryption:
    """Test encryption and decryption"""

    def test_encrypt_string(self):
        """Test encrypting a string"""
        manager = EncryptionManager()
        encrypted = manager.encrypt("sensitive_data")
        assert encrypted != "sensitive_data"
        assert isinstance(encrypted, str)

    def test_decrypt_string(self):
        """Test decrypting a string"""
        manager = EncryptionManager()
        original = "sensitive_data"
        encrypted = manager.encrypt(original)
        decrypted = manager.decrypt(encrypted)
        assert decrypted == original

    def test_encrypt_none_returns_none(self):
        """Test that encrypting None returns None"""
        manager = EncryptionManager()
        assert manager.encrypt(None) is None

    def test_decrypt_none_returns_none(self):
        """Test that decrypting None returns None"""
        manager = EncryptionManager()
        assert manager.decrypt(None) is None

    def test_encrypt_different_values_different_results(self):
        """Test that different values encrypt differently"""
        manager = EncryptionManager()
        encrypted1 = manager.encrypt("data1")
        encrypted2 = manager.encrypt("data2")
        assert encrypted1 != encrypted2

    def test_same_value_encrypts_differently_each_time(self):
        """Test that same value encrypts to different results (due to IV)"""
        manager = EncryptionManager()
        encrypted1 = manager.encrypt("data")
        encrypted2 = manager.encrypt("data")
        # Different encryption result due to random IV
        assert encrypted1 != encrypted2
        # But both decrypt to same value
        assert manager.decrypt(encrypted1) == manager.decrypt(encrypted2)

    def test_encrypt_integer(self):
        """Test encrypting an integer"""
        manager = EncryptionManager()
        encrypted = manager.encrypt(12345)
        decrypted = manager.decrypt(encrypted)
        assert decrypted == "12345"

    def test_function_encrypt_decrypt(self):
        """Test module-level encrypt/decrypt functions"""
        encrypted = encrypt_field("data")
        decrypted = decrypt_field(encrypted)
        assert decrypted == "data"

    def test_generate_key(self):
        """Test generating new encryption key"""
        key = EncryptionManager.generate_key()
        assert isinstance(key, str)
        assert len(key) > 0

    def test_different_keys_different_encryption(self):
        """Test that different keys produce different encryption"""
        manager1 = EncryptionManager("key1")
        manager2 = EncryptionManager("key2")

        encrypted1 = manager1.encrypt("data")
        encrypted2 = manager2.encrypt("data")

        # Different encryption
        assert encrypted1 != encrypted2

        # Each can only decrypt its own
        assert manager1.decrypt(encrypted1) == "data"
        assert manager2.decrypt(encrypted2) == "data"

        # Cross-decryption fails
        with pytest.raises(ValueError):
            manager1.decrypt(encrypted2)


# ══════════════════════════════════════════════════════════════════════════════
# Integration Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestSecurityIntegration:
    """Integration tests combining multiple security features"""

    def test_authenticated_user_with_rbac(self):
        """Test authenticated user with RBAC"""
        token = create_access_token(
            user_id=1,
            username="manager",
            email="manager@example.com",
            roles=["hr_manager"],
        )
        token_data = verify_token(token, token_type="access")
        assert check_permission(token_data.roles, Permission.EMPLOYEE_CREATE)

    def test_audit_logs_encrypted_data(self):
        """Test that sensitive data can be encrypted in audit logs"""
        manager = EncryptionManager()
        sensitive_data = "SSN-123-45-6789"
        encrypted = manager.encrypt(sensitive_data)

        log_entry = AuditLogger.log_action(
            action=AuditAction.EMPLOYEE_CREATE,
            user_id=1,
            username="admin",
            resource_type="employee",
            resource_id=5,
            after_state={"ssn": encrypted},
        )
        assert log_entry["after_state"]["ssn"] != sensitive_data
        assert manager.decrypt(log_entry["after_state"]["ssn"]) == sensitive_data

    def test_permission_denied_flow(self):
        """Test permission denied scenario"""
        token = create_access_token(
            user_id=5,
            username="employee",
            email="emp@example.com",
            roles=["employee"],
        )
        token_data = verify_token(token, token_type="access")
        assert not check_permission(token_data.roles, Permission.EMPLOYEE_DELETE)

        # Audit the unauthorized attempt
        AuditLogger.log_action(
            action=AuditAction.EMPLOYEE_DELETE,
            user_id=token_data.user_id,
            username=token_data.username,
            resource_type="employee",
            resource_id=10,
            details="Unauthorized delete attempt",
        )
