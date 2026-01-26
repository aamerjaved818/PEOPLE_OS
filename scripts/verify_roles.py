from backend.permissions_config import DEFAULT_ROLE_PERMISSIONS, ROLE_HIERARCHY

print("--- Role Compliance Verification ---")

expected_roles = {
    "SystemService": ["*"],
    "Auditor": ["view_audit_logs", "view_reports"]
}

all_passed = True

for role, expected_perms in expected_roles.items():
    if role not in DEFAULT_ROLE_PERMISSIONS:
        print(f"❌ {role} NOT found in DEFAULT_ROLE_PERMISSIONS")
        all_passed = False
    else:
        actual_perms = DEFAULT_ROLE_PERMISSIONS[role]
        if actual_perms == expected_perms:
            print(f"✅ {role} correctly defined with permissions: {actual_perms}")
        else:
            print(f"⚠️ {role} defined but permissions mismatch. Expected {expected_perms}, got {actual_perms}")
            all_passed = False

    if role not in ROLE_HIERARCHY:
        print(f"❌ {role} NOT found in ROLE_HIERARCHY")
        all_passed = False
    else:
        print(f"✅ {role} correctly present in hierarchy at index {ROLE_HIERARCHY.index(role)}")

if all_passed:
    print("\n✅ Verification PASSED: All roles compliant.")
else:
    print("\n❌ Verification FAILED: Role definitions incorrect.")
