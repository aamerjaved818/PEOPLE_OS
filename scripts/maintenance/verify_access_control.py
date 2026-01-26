
import sys
import os

# Add parent directory to path
sys.path.append(os.getcwd())

from backend import permissions_config

def verify_access_design():
    print("--- Verifying Access Control Redesign ---")
    
    # 1. Verify Definitions
    print("1. Checking Role Definitions...")
    
    system_roots = permissions_config.SYSTEM_ROOT_ROLES
    org_supers = permissions_config.ORG_SUPER_ROLES
    super_roles = permissions_config.SUPER_ROLES
    
    print(f"   SYSTEM_ROOT_ROLES: {system_roots}")
    print(f"   ORG_SUPER_ROLES:    {org_supers}")
    print(f"   SUPER_ROLES:      {super_roles}")
    
    errors = []
    
    if "Root" not in system_roots:
        errors.append("❌ Root is MISSING from SYSTEM_ROOT_ROLES")
    else:
        print("   ✅ Root is in SYSTEM_ROOT_ROLES")
        
    if "Super Admin" not in org_supers:
        errors.append("❌ Super Admin is MISSING from ORG_SUPER_ROLES")
    else:
        print("   ✅ Super Admin is in ORG_SUPER_ROLES")
        
    if "Super Admin" in system_roots:
        errors.append("❌ Super Admin LEAKED into SYSTEM_ROOT_ROLES (Security Risk!)")
    else:
        print("   ✅ Super Admin is correctly excluded from SYSTEM_ROOT_ROLES")

    # 2. Verify Logic Simulation
    print("\n2. Simulating Access Logic...")
    
    # Simulation: Root User
    root_role = "Root"
    root_can_view_all = (root_role in system_roots)
    print(f"   [Simulation] Root 'can_view_all_orgs': {root_can_view_all}")
    if not root_can_view_all:
        errors.append("❌ Root failed System Full Access check")
        
    # Simulation: Super Admin User
    admin_role = "Super Admin"
    admin_can_view_all = (admin_role in system_roots)
    print(f"   [Simulation] Super Admin 'can_view_all_orgs': {admin_can_view_all}")
    if admin_can_view_all:
        errors.append("❌ Super Admin INCORRECTLY granted System Full Access")
        
    # Simulation: Permission Bypass
    root_bypass = (root_role in super_roles)
    admin_bypass = (admin_role in super_roles)
    
    print(f"   [Simulation] Root Permission Bypass: {root_bypass}")
    print(f"   [Simulation] Super Admin Permission Bypass: {admin_bypass}")
    
    if not root_bypass: errors.append("❌ Root failed Permission Bypass")
    if not admin_bypass: errors.append("❌ Super Admin failed Permission Bypass")

    print("-" * 30)
    if errors:
        print("VERIFICATION FAILED:")
        for e in errors:
            print(e)
    else:
        print("VERIFICATION SUCCESS: Access Control Design is Correct.")

if __name__ == "__main__":
    verify_access_design()
