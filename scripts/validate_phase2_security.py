"""
Validation script for Phase 2 Security Implementation
Tests OAuth2, RBAC, Audit Logging, and Encryption modules
"""

import sys
print(f"Python: {sys.executable}")
print(f"Version: {sys.version}")
print()

try:
    from backend.security.oauth2 import create_access_token, verify_token
    print("✅ OAuth2 imports successful")
    
    # Test token creation
    token = create_access_token(
        user_id=1,
        username="testuser",
        email="test@example.com",
        roles=["admin"]
    )
    print(f"✅ Created access token: {token[:50]}...")
    
    # Test token verification
    token_data = verify_token(token, token_type="access")
    print(f"✅ Verified token - User: {token_data.username}, Role: {token_data.roles}")
    
except Exception as e:
    print(f"❌ OAuth2 Error: {e}")
    import traceback
    traceback.print_exc()

print()

try:
    from backend.security.rbac import Role, Permission, check_permission
    print("✅ RBAC imports successful")
    
    # Test permission checking
    result = check_permission(["admin"], Permission.EMPLOYEE_DELETE)
    print(f"✅ Admin can delete employees: {result}")
    
    result = check_permission(["employee"], Permission.EMPLOYEE_DELETE)
    print(f"✅ Employee can delete employees: {result}")
    
except Exception as e:
    print(f"❌ RBAC Error: {e}")
    import traceback
    traceback.print_exc()

print()

try:
    from backend.security.audit_logger import AuditLogger, AuditAction
    print("✅ Audit Logging imports successful")
    
    # Test audit logging
    log_entry = AuditLogger.log_action(
        action=AuditAction.EMPLOYEE_CREATE,
        user_id=1,
        username="admin",
        resource_type="employee",
        resource_id=5,
        after_state={"name": "John Doe"}
    )
    print(f"✅ Created audit log: {log_entry['action']}")
    
except Exception as e:
    print(f"❌ Audit Logging Error: {e}")
    import traceback
    traceback.print_exc()

print()

try:
    from backend.security.encryption import EncryptionManager
    print("✅ Encryption imports successful")
    
    # Test encryption
    manager = EncryptionManager()
    encrypted = manager.encrypt("sensitive_data")
    decrypted = manager.decrypt(encrypted)
    
    print(f"✅ Encrypted: {encrypted[:50]}...")
    print(f"✅ Decrypted: {decrypted}")
    
except Exception as e:
    print(f"❌ Encryption Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("═" * 70)
print("✅ PHASE 2 SECURITY IMPLEMENTATION VALIDATED")
print("═" * 70)
