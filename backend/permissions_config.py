"""
RBAC PERMISSION SYSTEM - SINGLE SOURCE OF TRUTH (BACKEND)
==========================================================
Root and Super Admin are SYSTEM DEFAULTS with FULL ACCESS.
All other roles are configurable via System Settings UI.

DO NOT DUPLICATE THIS FILE. Frontend should mirror this structure.
"""

# ============================================================
# SYSTEM DEFAULT ROLES (Built-in - Cannot be modified)
# ============================================================
SYSTEM_ROLES = {"Root", "Super Admin"}

# ============================================================
# DEFAULT_ROLE_PERMISSIONS - Built-in System Defaults
# ============================================================
DEFAULT_ROLE_PERMISSIONS = {
    # SYSTEM DEFAULTS (Built-in - Full Access)
    "Root": ["*"],  # Full System Access - All permissions (system-wide)
    "Super Admin": ["*"],  # Full Organization Access - All permissions (organization-scoped)
    
    # CONFIGURABLE ROLES (Defaults - Can be modified via UI)
    "SystemAdmin": [],  # To be configured via System Settings
    "Business Admin": ["view_employees"],  # Default basic view permission for employees
    "Manager": [],  # To be configured via System Settings
    "User": [],  # To be configured via System Settings
}

# ============================================================
# PRIVILEGED ROLES - Hardcoded High-Privilege Sets
# ============================================================
SYSTEM_ROOT_ROLES = {"Root"}        # Bypass ALL checks + View ALL Orgs
ORG_SUPER_ROLES = {"Super Admin"}    # Bypass ALL checks + View OWN Org

# SUPER_ROLES - Roles with automatic permission bypass (Union)
SUPER_ROLES = SYSTEM_ROOT_ROLES | ORG_SUPER_ROLES

# ============================================================
# ROLE_HIERARCHY - Authority Levels (Higher index = more power)
# ============================================================
ROLE_HIERARCHY = [
    "User",  # Level 0
    "Manager",  # Level 1
    "Business Admin",  # Level 2
    "SystemAdmin",  # Level 3
    "Super Admin",  # Level 4
    "Root",  # Level 5
]


def has_permission(role: str, permission: str) -> bool:
    """
    Check if a role has a specific permission.
    Root and Super Admin always return True (wildcard bypass).
    """
    if role in SUPER_ROLES:
        return True
    
    perms = DEFAULT_ROLE_PERMISSIONS.get(role, [])
    return "*" in perms or permission in perms


def get_role_level(role: str) -> int:
    """Get the hierarchy level of a role (0-5)."""
    try:
        return ROLE_HIERARCHY.index(role)
    except ValueError:
        return -1


def is_higher_role(role_a: str, role_b: str) -> bool:
    """Check if role_a has higher authority than role_b."""
    return get_role_level(role_a) > get_role_level(role_b)
