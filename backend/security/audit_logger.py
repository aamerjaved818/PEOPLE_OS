"""
Audit logging module for peopleOS eBusiness Suite

Provides comprehensive audit trail for all sensitive operations.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.orm import Session

# Configure audit logger
audit_logger = logging.getLogger("audit")


class AuditAction(str, Enum):
    """Types of auditable actions"""

    # User management
    USER_LOGIN = "user:login"
    USER_LOGOUT = "user:logout"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_ROLE_CHANGE = "user:role_change"

    # Employee management
    EMPLOYEE_CREATE = "employee:create"
    EMPLOYEE_UPDATE = "employee:update"
    EMPLOYEE_DELETE = "employee:delete"

    # Department management
    DEPARTMENT_CREATE = "department:create"
    DEPARTMENT_UPDATE = "department:update"
    DEPARTMENT_DELETE = "department:delete"

    # Organization management
    ORG_UPDATE = "org:update"

    # Job management
    JOB_LEVEL_UPDATE = "job_level:update"

    # Security
    PERMISSION_CHANGE = "permission:change"
    ENCRYPTION_KEY_ROTATE = "encryption:key_rotate"

    # System
    SYSTEM_CONFIG = "system:config"
    BACKUP_CREATE = "backup:create"


class AuditLogger:
    """Centralized audit logging"""

    @staticmethod
    def log_action(
        action: AuditAction,
        user_id: int,
        username: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> None:
        """
        Log an auditable action.

        Args:
            action: Type of action performed
            user_id: ID of user performing action
            username: Username of user performing action
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            before_state: State before change (for updates/deletes)
            after_state: State after change (for creates/updates)
            details: Additional details
            ip_address: IP address of requester
        """
        timestamp = datetime.utcnow()

        log_entry = {
            "timestamp": timestamp.isoformat(),
            "action": action.value,
            "user_id": user_id,
            "username": username,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "before_state": before_state,
            "after_state": after_state,
            "details": details,
            "ip_address": ip_address,
        }

        # Log to structured logger
        audit_logger.info(json.dumps(log_entry))

        return log_entry

    @staticmethod
    def log_user_login(user_id: int, username: str, ip_address: Optional[str] = None) -> None:
        """Log user login"""
        AuditLogger.log_action(
            action=AuditAction.USER_LOGIN,
            user_id=user_id,
            username=username,
            resource_type="user",
            resource_id=user_id,
            ip_address=ip_address,
        )

    @staticmethod
    def log_employee_create(
        user_id: int, username: str, employee_id: int, employee_data: Dict[str, Any]
    ) -> None:
        """Log employee creation"""
        AuditLogger.log_action(
            action=AuditAction.EMPLOYEE_CREATE,
            user_id=user_id,
            username=username,
            resource_type="employee",
            resource_id=employee_id,
            after_state=employee_data,
            details=f"Created employee: {employee_data.get('name')}",
        )

    @staticmethod
    def log_employee_update(
        user_id: int,
        username: str,
        employee_id: int,
        before_state: Dict[str, Any],
        after_state: Dict[str, Any],
    ) -> None:
        """Log employee update"""
        # Calculate changes
        changes = {}
        for key in after_state:
            if before_state.get(key) != after_state.get(key):
                changes[key] = {
                    "before": before_state.get(key),
                    "after": after_state.get(key),
                }

        AuditLogger.log_action(
            action=AuditAction.EMPLOYEE_UPDATE,
            user_id=user_id,
            username=username,
            resource_type="employee",
            resource_id=employee_id,
            before_state=before_state,
            after_state=after_state,
            details=f"Updated fields: {', '.join(changes.keys())}",
        )

    @staticmethod
    def log_employee_delete(
        user_id: int, username: str, employee_id: int, employee_data: Dict[str, Any]
    ) -> None:
        """Log employee deletion"""
        AuditLogger.log_action(
            action=AuditAction.EMPLOYEE_DELETE,
            user_id=user_id,
            username=username,
            resource_type="employee",
            resource_id=employee_id,
            before_state=employee_data,
            details=f"Deleted employee: {employee_data.get('name')}",
        )

    @staticmethod
    def log_permission_change(
        user_id: int, username: str, target_user_id: int, old_roles: list, new_roles: list
    ) -> None:
        """Log permission/role change"""
        AuditLogger.log_action(
            action=AuditAction.USER_ROLE_CHANGE,
            user_id=user_id,
            username=username,
            resource_type="user",
            resource_id=target_user_id,
            before_state={"roles": old_roles},
            after_state={"roles": new_roles},
            details=f"Role changed from {old_roles} to {new_roles}",
        )


# Setup audit logging to file
def setup_audit_logging(log_file: str = "logs/audit.log") -> None:
    """Configure audit logging to file"""
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    audit_logger.addHandler(handler)
    audit_logger.setLevel(logging.INFO)
