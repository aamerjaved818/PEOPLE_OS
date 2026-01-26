"""
Analytics Permission Service - Role-based access control for analytics
Restricts which data users can see based on their role and organization
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class AnalyticsRole(str, Enum):
    """Analytics permission roles"""
    ADMIN = "admin"  # Can see all analytics
    HR_MANAGER = "hr_manager"  # Can see workforce and recruitment analytics
    FINANCE = "finance"  # Can see payroll and cost analytics
    DEPARTMENT_MANAGER = "department_manager"  # Can see own department analytics
    EMPLOYEE = "employee"  # Can see own analytics only


class AnalyticsPermission:
    """Permission check for analytics"""
    
    @staticmethod
    def get_user_analytics_role(user: dict) -> Optional[AnalyticsRole]:
        """Determine user's analytics role from their roles
        
        Args:
            user: User dictionary with 'roles' key
            
        Returns:
            AnalyticsRole or None
        """
        if not user or 'roles' not in user:
            return None
        
        roles = user.get('roles', [])
        if not isinstance(roles, list):
            roles = [roles]
        
        # Map HR roles to analytics roles
        for role in roles:
            if role in ['admin', 'system_admin']:
                return AnalyticsRole.ADMIN
            elif role in ['hr', 'hr_manager', 'hr_admin']:
                return AnalyticsRole.HR_MANAGER
            elif role in ['finance', 'finance_manager', 'accounting']:
                return AnalyticsRole.FINANCE
            elif role in ['manager', 'department_manager']:
                return AnalyticsRole.DEPARTMENT_MANAGER
            elif role in ['employee']:
                return AnalyticsRole.EMPLOYEE
        
        return None
    
    @staticmethod
    def can_view_dashboard(user: dict) -> bool:
        """Check if user can view analytics dashboard"""
        role = AnalyticsPermission.get_user_analytics_role(user)
        
        # Anyone with a defined role can view dashboard
        if role in [AnalyticsRole.ADMIN, AnalyticsRole.HR_MANAGER, AnalyticsRole.FINANCE, AnalyticsRole.DEPARTMENT_MANAGER]:
            return True
        
        # Employees can view their own analytics
        if role == AnalyticsRole.EMPLOYEE:
            return True
        
        return False
    
    @staticmethod
    def can_view_workforce_analytics(user: dict) -> bool:
        """Check if user can view workforce analytics"""
        role = AnalyticsPermission.get_user_analytics_role(user)
        
        if role in [AnalyticsRole.ADMIN, AnalyticsRole.HR_MANAGER]:
            return True
        
        # Department managers can see only their department
        if role == AnalyticsRole.DEPARTMENT_MANAGER:
            return True
        
        return False
    
    @staticmethod
    def can_view_recruitment_analytics(user: dict) -> bool:
        """Check if user can view recruitment analytics"""
        role = AnalyticsPermission.get_user_analytics_role(user)
        
        if role in [AnalyticsRole.ADMIN, AnalyticsRole.HR_MANAGER]:
            return True
        
        return False
    
    @staticmethod
    def can_view_payroll_analytics(user: dict) -> bool:
        """Check if user can view payroll analytics"""
        role = AnalyticsPermission.get_user_analytics_role(user)
        
        if role in [AnalyticsRole.ADMIN, AnalyticsRole.FINANCE]:
            return True
        
        return False
    
    @staticmethod
    def can_view_engagement_analytics(user: dict) -> bool:
        """Check if user can view engagement analytics"""
        role = AnalyticsPermission.get_user_analytics_role(user)
        
        if role in [AnalyticsRole.ADMIN, AnalyticsRole.HR_MANAGER]:
            return True
        
        # Department managers can see their department
        if role == AnalyticsRole.DEPARTMENT_MANAGER:
            return True
        
        return False
    
    @staticmethod
    def can_download_reports(user: dict) -> bool:
        """Check if user can download reports"""
        role = AnalyticsPermission.get_user_analytics_role(user)
        
        if role in [AnalyticsRole.ADMIN, AnalyticsRole.HR_MANAGER, AnalyticsRole.FINANCE]:
            return True
        
        # Department managers can download department reports
        if role == AnalyticsRole.DEPARTMENT_MANAGER:
            return True
        
        return False
    
    @staticmethod
    def can_view_employee_details(user: dict, target_employee_id: str, target_org_id: str, 
                                  target_department_id: Optional[str] = None) -> bool:
        """Check if user can view specific employee details
        
        Args:
            user: User dictionary
            target_employee_id: Employee ID to view
            target_org_id: Organization ID
            target_department_id: Optional department ID of target employee
            
        Returns:
            True if user can view employee details
        """
        role = AnalyticsPermission.get_user_analytics_role(user)
        user_id = user.get('id')
        
        if role == AnalyticsRole.ADMIN:
            return True
        
        if role == AnalyticsRole.HR_MANAGER:
            return True
        
        if role == AnalyticsRole.DEPARTMENT_MANAGER:
            # Can see employees in own department
            user_department = user.get('department_id')
            if user_department and user_department == target_department_id:
                return True
        
        if role == AnalyticsRole.EMPLOYEE:
            # Can only see own data
            return user_id == target_employee_id
        
        return False


class AnalyticsDataFilter:
    """Filters analytics data based on user permissions"""
    
    @staticmethod
    def filter_department_distribution(user: dict, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter department distribution based on permissions
        
        Args:
            user: User with role
            data: Department distribution data
            
        Returns:
            Filtered data
        """
        role = AnalyticsPermission.get_user_analytics_role(user)
        
        if role in [AnalyticsRole.ADMIN, AnalyticsRole.HR_MANAGER]:
            return data
        
        if role == AnalyticsRole.DEPARTMENT_MANAGER:
            # Only return user's department
            user_dept = user.get('department')
            return [d for d in data if d.get('name') == user_dept]
        
        return []
    
    @staticmethod
    def filter_employee_data(user: dict, employees: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter employee list based on permissions
        
        Args:
            user: User with role
            employees: List of employee data
            
        Returns:
            Filtered employee list
        """
        role = AnalyticsPermission.get_user_analytics_role(user)
        
        if role in [AnalyticsRole.ADMIN, AnalyticsRole.HR_MANAGER]:
            return employees
        
        if role == AnalyticsRole.DEPARTMENT_MANAGER:
            # Only return employees from user's department
            user_dept = user.get('department_id')
            return [e for e in employees if e.get('department_id') == user_dept]
        
        if role == AnalyticsRole.EMPLOYEE:
            # Only return own employee record
            user_id = user.get('id')
            return [e for e in employees if e.get('id') == user_id]
        
        return []
    
    @staticmethod
    def filter_candidate_data(user: dict, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter candidate list based on permissions
        
        Args:
            user: User with role
            candidates: List of candidate data
            
        Returns:
            Filtered candidate list
        """
        role = AnalyticsPermission.get_user_analytics_role(user)
        
        if role in [AnalyticsRole.ADMIN, AnalyticsRole.HR_MANAGER]:
            return candidates
        
        # Other roles cannot see recruitment data
        return []
    
    @staticmethod
    def filter_payroll_data(user: dict, payroll_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter payroll records based on permissions
        
        Args:
            user: User with role
            payroll_records: List of payroll data
            
        Returns:
            Filtered payroll list
        """
        role = AnalyticsPermission.get_user_analytics_role(user)
        
        if role in [AnalyticsRole.ADMIN, AnalyticsRole.FINANCE]:
            return payroll_records
        
        # Other roles cannot see payroll data
        return []


class AnalyticsPermissionMiddleware:
    """Middleware to enforce analytics permissions"""
    
    @staticmethod
    def check_analytics_access(user: dict, analytics_type: str) -> bool:
        """Check if user has access to specific analytics type
        
        Args:
            user: User dictionary
            analytics_type: Type of analytics ('dashboard', 'workforce', 'recruitment', 'payroll', 'engagement')
            
        Returns:
            True if access granted
        """
        if analytics_type == 'dashboard':
            return AnalyticsPermission.can_view_dashboard(user)
        
        if analytics_type == 'workforce':
            return AnalyticsPermission.can_view_workforce_analytics(user)
        
        if analytics_type == 'recruitment':
            return AnalyticsPermission.can_view_recruitment_analytics(user)
        
        if analytics_type == 'payroll':
            return AnalyticsPermission.can_view_payroll_analytics(user)
        
        if analytics_type == 'engagement':
            return AnalyticsPermission.can_view_engagement_analytics(user)
        
        return False
    
    @staticmethod
    def log_access(user: dict, analytics_type: str, allowed: bool):
        """Log analytics access for audit trail
        
        Args:
            user: User accessing analytics
            analytics_type: Type of analytics accessed
            allowed: Whether access was allowed
        """
        user_id = user.get('id', 'unknown')
        user_role = AnalyticsPermission.get_user_analytics_role(user)
        
        if allowed:
            logger.info(f"Analytics access granted: user={user_id}, role={user_role}, type={analytics_type}")
        else:
            logger.warning(f"Analytics access denied: user={user_id}, role={user_role}, type={analytics_type}")
