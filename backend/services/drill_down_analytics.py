"""
Drill-Down Analytics Service - Provides detailed data exploration endpoints
Allows users to click metrics and explore underlying data
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from backend.domains.hcm import models as hcm_models
from backend.domains.core import models as core_models
from backend.services.analytics_permissions import AnalyticsPermission, AnalyticsDataFilter
import logging

logger = logging.getLogger(__name__)


class DrillDownAnalyticsService:
    """Service for drill-down analytics and data exploration"""
    
    # ==================== DEPARTMENT DRILL-DOWN ====================
    
    @staticmethod
    def get_department_employees(
        db: Session, organization_id: str, department_id: str, user: dict
    ) -> Dict[str, Any]:
        """Get all employees in a department with details
        
        Args:
            db: Database session
            organization_id: Organization ID
            department_id: Department ID to drill into
            user: User making request (for permission check)
            
        Returns:
            Department employees with metrics
        """
        # Permission check
        if not AnalyticsPermission.can_view_workforce_analytics(user):
            raise PermissionError("Not authorized to view workforce analytics")
        
        # Get department
        department = db.query(core_models.DBDepartment).filter(
            core_models.DBDepartment.id == department_id,
            core_models.DBDepartment.organization_id == organization_id
        ).first()
        
        if not department:
            return {"error": "Department not found"}
        
        # Get employees in department
        employees = db.query(hcm_models.DBEmployee).filter(
            hcm_models.DBEmployee.organization_id == organization_id,
            hcm_models.DBEmployee.department_id == department_id,
            hcm_models.DBEmployee.status == "Active"
        ).all()
        
        # Apply data filter
        employee_data = [
            {
                "id": e.id,
                "code": e.code,
                "name": e.name,
                "designation": e.designation_rel.name if e.designation_rel else "Unassigned",
                "email": e.email,
                "phone": e.phone,
                "gross_salary": float(e.gross_salary) if e.gross_salary else 0,
                "status": e.status,
                "date_of_joining": e.date_of_joining.isoformat() if e.date_of_joining else None,
            }
            for e in employees
        ]
        
        # Apply permission-based filtering
        filtered = AnalyticsDataFilter.filter_employee_data(user, employee_data)
        
        return {
            "department": {
                "id": department.id,
                "name": department.name,
                "code": department.code
            },
            "employee_count": len(filtered),
            "total_payroll": sum(e["gross_salary"] for e in filtered),
            "average_salary": sum(e["gross_salary"] for e in filtered) / len(filtered) if filtered else 0,
            "employees": filtered
        }
    
    @staticmethod
    def get_designation_employees(
        db: Session, organization_id: str, designation_id: str, user: dict
    ) -> Dict[str, Any]:
        """Get all employees with a specific designation
        
        Args:
            db: Database session
            organization_id: Organization ID
            designation_id: Designation ID to drill into
            user: User making request
            
        Returns:
            Designation employees with metrics
        """
        if not AnalyticsPermission.can_view_workforce_analytics(user):
            raise PermissionError("Not authorized")
        
        designation = db.query(hcm_models.DBDesignation).filter(
            hcm_models.DBDesignation.id == designation_id,
            hcm_models.DBDesignation.organization_id == organization_id
        ).first()
        
        if not designation:
            return {"error": "Designation not found"}
        
        employees = db.query(hcm_models.DBEmployee).filter(
            hcm_models.DBEmployee.organization_id == organization_id,
            hcm_models.DBEmployee.designation_id == designation_id,
            hcm_models.DBEmployee.status == "Active"
        ).all()
        
        employee_data = [
            {
                "id": e.id,
                "name": e.name,
                "email": e.email,
                "department": e.department_rel.name if e.department_rel else "Unassigned",
                "gross_salary": float(e.gross_salary) if e.gross_salary else 0,
                "date_of_joining": e.date_of_joining.isoformat() if e.date_of_joining else None,
            }
            for e in employees
        ]
        
        filtered = AnalyticsDataFilter.filter_employee_data(user, employee_data)
        
        return {
            "designation": designation.name,
            "employee_count": len(filtered),
            "average_salary": sum(e["gross_salary"] for e in filtered) / len(filtered) if filtered else 0,
            "salary_range": {
                "min": min(e["gross_salary"] for e in filtered) if filtered else 0,
                "max": max(e["gross_salary"] for e in filtered) if filtered else 0,
            },
            "employees": filtered
        }
    
    # ==================== RECRUITMENT DRILL-DOWN ====================
    
    @staticmethod
    def get_recruitment_stage_candidates(
        db: Session, organization_id: str, stage: str, user: dict
    ) -> Dict[str, Any]:
        """Get all candidates in a specific recruitment stage
        
        Args:
            db: Database session
            organization_id: Organization ID
            stage: Recruitment stage (Applied, Shortlisted, Interview, Offer, Joined)
            user: User making request
            
        Returns:
            Candidates in stage with details
        """
        if not AnalyticsPermission.can_view_recruitment_analytics(user):
            raise PermissionError("Not authorized to view recruitment analytics")
        
        candidates = db.query(hcm_models.DBCandidate).filter(
            hcm_models.DBCandidate.organization_id == organization_id,
            hcm_models.DBCandidate.current_stage == stage
        ).order_by(hcm_models.DBCandidate.applied_date.desc()).all()
        
        candidate_data = [
            {
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "phone": c.phone,
                "position_applied": c.position_applied,
                "applied_date": c.applied_date.isoformat() if c.applied_date else None,
                "current_stage": c.current_stage,
                "days_in_pipeline": (datetime.now() - c.applied_date).days if c.applied_date else 0,
                "rating": c.rating or 0,
                "notes": c.notes or ""
            }
            for c in candidates
        ]
        
        filtered = AnalyticsDataFilter.filter_candidate_data(user, candidate_data)
        
        # Calculate stage metrics
        avg_days = sum(c["days_in_pipeline"] for c in filtered) / len(filtered) if filtered else 0
        
        return {
            "stage": stage,
            "candidate_count": len(filtered),
            "average_days_in_stage": round(avg_days, 1),
            "average_rating": sum(c["rating"] for c in filtered) / len(filtered) if filtered else 0,
            "candidates": filtered
        }
    
    @staticmethod
    def get_position_candidates(
        db: Session, organization_id: str, position: str, user: dict
    ) -> Dict[str, Any]:
        """Get all candidates for a specific position
        
        Args:
            db: Database session
            organization_id: Organization ID
            position: Position/job title
            user: User making request
            
        Returns:
            Candidates for position grouped by stage
        """
        if not AnalyticsPermission.can_view_recruitment_analytics(user):
            raise PermissionError("Not authorized")
        
        candidates = db.query(hcm_models.DBCandidate).filter(
            hcm_models.DBCandidate.organization_id == organization_id,
            hcm_models.DBCandidate.position_applied == position
        ).all()
        
        # Group by stage
        by_stage = {}
        for c in candidates:
            stage = c.current_stage or "Unknown"
            if stage not in by_stage:
                by_stage[stage] = []
            by_stage[stage].append({
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "applied_date": c.applied_date.isoformat() if c.applied_date else None,
                "rating": c.rating or 0,
            })
        
        return {
            "position": position,
            "total_candidates": len(candidates),
            "by_stage": by_stage
        }
    
    # ==================== PAYROLL DRILL-DOWN ====================
    
    @staticmethod
    def get_payroll_by_department(
        db: Session, organization_id: str, period_month: int, period_year: int, user: dict
    ) -> Dict[str, Any]:
        """Get payroll metrics by department for a specific period
        
        Args:
            db: Database session
            organization_id: Organization ID
            period_month: Month (1-12)
            period_year: Year
            user: User making request
            
        Returns:
            Department payroll breakdown
        """
        if not AnalyticsPermission.can_view_payroll_analytics(user):
            raise PermissionError("Not authorized to view payroll analytics")
        
        from sqlalchemy import extract
        
        payroll = db.query(
            core_models.DBDepartment.name,
            func.count(hcm_models.DBPayrollLedger.id).label("count"),
            func.sum(hcm_models.DBPayrollLedger.gross_salary).label("total_gross"),
            func.sum(hcm_models.DBPayrollLedger.total_deductions).label("total_deductions"),
            func.sum(hcm_models.DBPayrollLedger.net_salary).label("total_net"),
            func.avg(hcm_models.DBPayrollLedger.gross_salary).label("avg_gross"),
        ).outerjoin(
            hcm_models.DBEmployee, hcm_models.DBPayrollLedger.employee_id == hcm_models.DBEmployee.id
        ).outerjoin(
            core_models.DBDepartment, hcm_models.DBEmployee.department_id == core_models.DBDepartment.id
        ).filter(
            hcm_models.DBPayrollLedger.organization_id == organization_id,
            extract('month', hcm_models.DBPayrollLedger.period_start_date) == period_month,
            extract('year', hcm_models.DBPayrollLedger.period_start_date) == period_year,
        ).group_by(core_models.DBDepartment.name).all()
        
        return {
            "period": f"{period_month}/{period_year}",
            "by_department": [
                {
                    "department": name or "Unassigned",
                    "employee_count": count,
                    "total_gross_salary": float(total_gross) if total_gross else 0,
                    "total_deductions": float(total_deductions) if total_deductions else 0,
                    "total_net_salary": float(total_net) if total_net else 0,
                    "average_gross": float(avg_gross) if avg_gross else 0,
                }
                for name, count, total_gross, total_deductions, total_net, avg_gross in payroll
            ]
        }
    
    # ==================== TREND ANALYSIS ====================
    
    @staticmethod
    def get_headcount_by_department_trend(
        db: Session, organization_id: str, department_id: str, months: int = 6, user: dict = None
    ) -> Dict[str, Any]:
        """Get headcount trend for a specific department
        
        Args:
            db: Database session
            organization_id: Organization ID
            department_id: Department to analyze
            months: Number of months to analyze
            user: User making request
            
        Returns:
            Monthly headcount trend
        """
        if user and not AnalyticsPermission.can_view_workforce_analytics(user):
            raise PermissionError("Not authorized")
        
        department = db.query(core_models.DBDepartment).filter(
            core_models.DBDepartment.id == department_id
        ).first()
        
        if not department:
            return {"error": "Department not found"}
        
        trends = []
        current_date = datetime.now()
        
        for i in range(months - 1, -1, -1):
            period_date = current_date - timedelta(days=30 * i)
            month_name = period_date.strftime("%b")
            
            count = db.query(hcm_models.DBEmployee).filter(
                hcm_models.DBEmployee.organization_id == organization_id,
                hcm_models.DBEmployee.department_id == department_id,
                hcm_models.DBEmployee.date_of_joining <= period_date,
                hcm_models.DBEmployee.status == "Active"
            ).count()
            
            trends.append({
                "month": month_name,
                "count": count,
                "date": period_date.strftime("%Y-%m-%d")
            })
        
        return {
            "department": department.name,
            "trends": trends
        }
    
    @staticmethod
    def get_salary_distribution(
        db: Session, organization_id: str, department_id: Optional[str] = None, user: dict = None
    ) -> Dict[str, Any]:
        """Get salary distribution analysis
        
        Args:
            db: Database session
            organization_id: Organization ID
            department_id: Optional filter by department
            user: User making request
            
        Returns:
            Salary distribution with statistics
        """
        if user and not AnalyticsPermission.can_view_payroll_analytics(user):
            raise PermissionError("Not authorized")
        
        query = db.query(hcm_models.DBEmployee.gross_salary).filter(
            hcm_models.DBEmployee.organization_id == organization_id,
            hcm_models.DBEmployee.status == "Active"
        )
        
        if department_id:
            query = query.filter(hcm_models.DBEmployee.department_id == department_id)
        
        salaries = [s[0] for s in query.all() if s[0]]
        
        if not salaries:
            return {"error": "No salary data"}
        
        sorted_salaries = sorted(salaries)
        
        return {
            "statistics": {
                "min": min(salaries),
                "max": max(salaries),
                "average": sum(salaries) / len(salaries),
                "median": sorted_salaries[len(sorted_salaries) // 2],
                "std_dev": (sum((s - (sum(salaries) / len(salaries))) ** 2 for s in salaries) / len(salaries)) ** 0.5,
            },
            "count": len(salaries),
            "distribution": {
                "0-50k": len([s for s in salaries if s < 50000]),
                "50k-100k": len([s for s in salaries if 50000 <= s < 100000]),
                "100k-150k": len([s for s in salaries if 100000 <= s < 150000]),
                "150k+": len([s for s in salaries if s >= 150000]),
            }
        }
