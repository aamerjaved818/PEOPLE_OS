"""
Role-Based Access Control (RBAC) module for peopleOS eBusiness Suite

Provides role definitions, permission management, and access control.
"""

from enum import Enum
from typing import List, Dict, Set
from fastapi import HTTPException, status


class Role(str, Enum):
    """User roles in PeopleOS"""

    ADMIN = "admin"
    HR_MANAGER = "hr_manager"
    DEPARTMENT_MANAGER = "department_manager"
    EMPLOYEE = "employee"
    VIEWER = "viewer"


class Permission(str, Enum):
    """Permissions in PeopleOS"""

    # Employee management
    EMPLOYEE_VIEW = "employee:view"
    EMPLOYEE_CREATE = "employee:create"
    EMPLOYEE_UPDATE = "employee:update"
    EMPLOYEE_DELETE = "employee:delete"

    # Department management
    DEPARTMENT_VIEW = "department:view"
    DEPARTMENT_CREATE = "department:create"
    DEPARTMENT_UPDATE = "department:update"
    DEPARTMENT_DELETE = "department:delete"

    # Organization management
    ORG_VIEW = "org:view"
    ORG_CREATE = "org:create"
    ORG_UPDATE = "org:update"
    ORG_DELETE = "org:delete"

    # Job architecture
    JOB_LEVEL_VIEW = "job_level:view"
    JOB_LEVEL_CREATE = "job_level:create"
    JOB_LEVEL_UPDATE = "job_level:update"
    JOB_LEVEL_DELETE = "job_level:delete"

    # Shift management
    SHIFT_VIEW = "shift:view"
    SHIFT_CREATE = "shift:create"
    SHIFT_UPDATE = "shift:update"
    SHIFT_DELETE = "shift:delete"

    # System administration
    SYSTEM_CONFIG = "system:config"
    AUDIT_LOG_VIEW = "audit:view"
    BACKUP_MANAGE = "backup:manage"


class RBACManager:
    """Manages role-based access control"""

    # Define permissions per role
    ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
        Role.ADMIN: set(Permission),  # Admin has all permissions
        Role.HR_MANAGER: {
            Permission.EMPLOYEE_VIEW,
            Permission.EMPLOYEE_CREATE,
            Permission.EMPLOYEE_UPDATE,
            Permission.EMPLOYEE_DELETE,
            Permission.DEPARTMENT_VIEW,
            Permission.DEPARTMENT_CREATE,
            Permission.DEPARTMENT_UPDATE,
            Permission.DEPARTMENT_DELETE,
            Permission.ORG_VIEW,
            Permission.JOB_LEVEL_VIEW,
            Permission.SHIFT_VIEW,
            Permission.SHIFT_CREATE,
            Permission.SHIFT_UPDATE,
            Permission.AUDIT_LOG_VIEW,
        },
        Role.DEPARTMENT_MANAGER: {
            Permission.EMPLOYEE_VIEW,
            Permission.EMPLOYEE_UPDATE,
            Permission.DEPARTMENT_VIEW,
            Permission.DEPARTMENT_UPDATE,
            Permission.JOB_LEVEL_VIEW,
            Permission.SHIFT_VIEW,
            Permission.SHIFT_CREATE,
            Permission.SHIFT_UPDATE,
        },
        Role.EMPLOYEE: {
            Permission.EMPLOYEE_VIEW,  # Own profile only
            Permission.DEPARTMENT_VIEW,
            Permission.ORG_VIEW,
            Permission.JOB_LEVEL_VIEW,
            Permission.SHIFT_VIEW,
        },
        Role.VIEWER: {
            Permission.EMPLOYEE_VIEW,
            Permission.DEPARTMENT_VIEW,
            Permission.ORG_VIEW,
            Permission.JOB_LEVEL_VIEW,
            Permission.SHIFT_VIEW,
        },
    }

    @staticmethod
    def get_role_permissions(role: Role) -> Set[Permission]:
        """Get all permissions for a role"""
        return RBACManager.ROLE_PERMISSIONS.get(role, set())

    @staticmethod
    def has_permission(roles: List[str], permission: Permission) -> bool:
        """Check if any role has the required permission"""
        for role_str in roles:
            try:
                role = Role(role_str)
                permissions = RBACManager.get_role_permissions(role)
                if permission in permissions:
                    return True
            except ValueError:
                continue
        return False

    @staticmethod
    def require_permission(permission: Permission):
        """Dependency for checking permission"""
        from .oauth2 import TokenData
        from fastapi import Depends
        from .oauth2 import get_current_user

        async def check_permission_dependency(
            current_user: TokenData = Depends(get_current_user),
        ) -> TokenData:
            if not RBACManager.has_permission(current_user.roles, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User does not have permission: {permission}",
                )
            return current_user

        return check_permission_dependency


# Convenience functions
def check_permission(roles: List[str], permission: Permission) -> bool:
    """Check if user has permission"""
    return RBACManager.has_permission(roles, permission)


def require_permission(permission: Permission):
    """Require a specific permission"""
    return RBACManager.require_permission(permission)


def get_user_roles(roles: List[str]) -> List[Role]:
    """Get Role enums from role strings"""
    return [Role(r) for r in roles if r in [role.value for role in Role]]
