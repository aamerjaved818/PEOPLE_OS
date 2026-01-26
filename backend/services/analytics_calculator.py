"""
Analytics Calculator Service - Computes real business metrics
Replaces placeholder data with actual calculations from database
"""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from backend.domains.hcm import models as hcm_models
from backend.domains.core import models as core_models
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class AnalyticsCalculator:
    """Calculates real business metrics from database"""

    # ==================== HEADCOUNT METRICS ====================
    
    @staticmethod
    def calculate_total_employees(db: Session, organization_id: str, status: str = "Active") -> int:
        """Get total active employees in organization"""
        return db.query(hcm_models.DBEmployee).filter(
            hcm_models.DBEmployee.organization_id == organization_id,
            hcm_models.DBEmployee.status == status
        ).count()

    @staticmethod
    def calculate_employees_by_department(
        db: Session, organization_id: str, status: str = "Active"
    ) -> List[Dict[str, Any]]:
        """Get employee distribution by department"""
        dept_dist = db.query(
            core_models.DBDepartment.name,
            func.count(hcm_models.DBEmployee.id).label("count")
        ).join(
            hcm_models.DBEmployee, hcm_models.DBEmployee.department_id == core_models.DBDepartment.id
        ).filter(
            hcm_models.DBEmployee.organization_id == organization_id,
            hcm_models.DBEmployee.status == status
        ).group_by(core_models.DBDepartment.name).order_by(func.count(hcm_models.DBEmployee.id).desc()).all()
        
        return [{"name": name, "value": count} for name, count in dept_dist]

    @staticmethod
    def calculate_employees_by_gender(
        db: Session, organization_id: str, status: str = "Active"
    ) -> List[Dict[str, Any]]:
        """Get employee distribution by gender"""
        gender_dist = db.query(
            hcm_models.DBEmployee.gender,
            func.count(hcm_models.DBEmployee.id).label("count")
        ).filter(
            hcm_models.DBEmployee.organization_id == organization_id,
            hcm_models.DBEmployee.status == status
        ).group_by(hcm_models.DBEmployee.gender).all()
        
        return [{"name": gender or "Not Specified", "value": count} for gender, count in gender_dist]

    @staticmethod
    def calculate_employees_by_grade(
        db: Session, organization_id: str, status: str = "Active"
    ) -> List[Dict[str, Any]]:
        """Get employee distribution by designation/grade"""
        grade_dist = db.query(
            hcm_models.DBDesignation.name,
            func.count(hcm_models.DBEmployee.id).label("count")
        ).outerjoin(
            hcm_models.DBDesignation, hcm_models.DBEmployee.designation_id == hcm_models.DBDesignation.id
        ).filter(
            hcm_models.DBEmployee.organization_id == organization_id,
            hcm_models.DBEmployee.status == status
        ).group_by(hcm_models.DBDesignation.name).order_by(func.count(hcm_models.DBEmployee.id).desc()).all()
        
        return [{"name": name or "Unassigned", "value": count} for name, count in grade_dist]

    @staticmethod
    def calculate_headcount_trends(
        db: Session, organization_id: str, months: int = 6
    ) -> List[Dict[str, Any]]:
        """Calculate monthly headcount trends based on join dates"""
        trends = []
        current_date = datetime.now()
        
        for i in range(months - 1, -1, -1):
            period_date = current_date - relativedelta(months=i)
            month_name = period_date.strftime("%b")
            
            # Count employees who joined before this date and haven't left
            headcount = db.query(hcm_models.DBEmployee).filter(
                hcm_models.DBEmployee.organization_id == organization_id,
                hcm_models.DBEmployee.date_of_joining <= period_date,
                hcm_models.DBEmployee.status == "Active"
            ).count()
            
            trends.append({
                "name": month_name,
                "count": headcount,
                "liability": round(headcount * 0.25, 1)  # Gratuity liability estimation
            })
        
        return trends

    @staticmethod
    def calculate_new_hires(db: Session, organization_id: str, period_days: int = 30) -> int:
        """Calculate number of new hires in last N days"""
        cutoff_date = datetime.now() - timedelta(days=period_days)
        return db.query(hcm_models.DBEmployee).filter(
            hcm_models.DBEmployee.organization_id == organization_id,
            hcm_models.DBEmployee.date_of_joining >= cutoff_date
        ).count()

    @staticmethod
    def calculate_average_tenure(db: Session, organization_id: str) -> Dict[str, Any]:
        """Calculate average tenure in days and years"""
        employees = db.query(hcm_models.DBEmployee.date_of_joining).filter(
            hcm_models.DBEmployee.organization_id == organization_id,
            hcm_models.DBEmployee.status == "Active"
        ).all()
        
        if not employees:
            return {"avg_days": 0, "avg_years": 0}
        
        today = datetime.now()
        tenures = [(today - emp[0]).days for emp in employees if emp[0]]
        avg_days = sum(tenures) / len(tenures) if tenures else 0
        avg_years = avg_days / 365.25 if avg_days else 0
        
        return {
            "avg_days": round(avg_days),
            "avg_years": round(avg_years, 1)
        }

    # ==================== TURNOVER METRICS ====================

    @staticmethod
    def calculate_turnover_rate(db: Session, organization_id: str, period_months: int = 12) -> Dict[str, Any]:
        """Calculate annualized turnover rate"""
        cutoff_date = datetime.now() - relativedelta(months=period_months)
        
        # Employees who left in the period
        left_employees = db.query(hcm_models.DBEmployee).filter(
            hcm_models.DBEmployee.organization_id == organization_id,
            hcm_models.DBEmployee.status == "Terminated",
            hcm_models.DBEmployee.separation_date >= cutoff_date
        ).count()
        
        # Average headcount during period
        active_employees = db.query(hcm_models.DBEmployee).filter(
            hcm_models.DBEmployee.organization_id == organization_id,
            hcm_models.DBEmployee.status == "Active"
        ).count()
        
        total_employees = db.query(hcm_models.DBEmployee).filter(
            hcm_models.DBEmployee.organization_id == organization_id
        ).count()
        
        avg_headcount = (active_employees + total_employees) / 2 if total_employees > 0 else 1
        turnover_rate = (left_employees / avg_headcount * 100) if avg_headcount > 0 else 0
        
        return {
            "left_count": left_employees,
            "turnover_rate": round(turnover_rate, 1),
            "period_months": period_months
        }

    @staticmethod
    def calculate_termination_by_department(
        db: Session, organization_id: str, period_months: int = 12
    ) -> List[Dict[str, Any]]:
        """Calculate terminations by department"""
        cutoff_date = datetime.now() - relativedelta(months=period_months)
        
        terminations = db.query(
            core_models.DBDepartment.name,
            func.count(hcm_models.DBEmployee.id).label("count")
        ).join(
            hcm_models.DBEmployee, hcm_models.DBEmployee.department_id == core_models.DBDepartment.id
        ).filter(
            hcm_models.DBEmployee.organization_id == organization_id,
            hcm_models.DBEmployee.status == "Terminated",
            hcm_models.DBEmployee.separation_date >= cutoff_date
        ).group_by(core_models.DBDepartment.name).all()
        
        return [{"name": name, "value": count} for name, count in terminations]

    @staticmethod
    def calculate_retention_rate(db: Session, organization_id: str) -> float:
        """Calculate overall retention rate as percentage"""
        total = db.query(hcm_models.DBEmployee).filter(
            hcm_models.DBEmployee.organization_id == organization_id
        ).count()
        
        if total == 0:
            return 100.0
        
        active = db.query(hcm_models.DBEmployee).filter(
            hcm_models.DBEmployee.organization_id == organization_id,
            hcm_models.DBEmployee.status == "Active"
        ).count()
        
        return round((active / total * 100), 1)

    # ==================== RECRUITMENT METRICS ====================

    @staticmethod
    def calculate_recruitment_funnel(
        db: Session, organization_id: str
    ) -> List[Dict[str, Any]]:
        """Get candidate distribution by stage"""
        stages = db.query(
            hcm_models.DBCandidate.current_stage,
            func.count(hcm_models.DBCandidate.id).label("count")
        ).filter(
            hcm_models.DBCandidate.organization_id == organization_id
        ).group_by(hcm_models.DBCandidate.current_stage).order_by(
            func.count(hcm_models.DBCandidate.id).desc()
        ).all()
        
        return [{"name": stage or "Unknown", "value": count} for stage, count in stages]

    @staticmethod
    def calculate_funnel_conversion_rates(
        db: Session, organization_id: str
    ) -> Dict[str, float]:
        """Calculate stage-to-stage conversion rates"""
        stages = ["Applied", "Shortlisted", "Interview", "Offer", "Joined"]
        conversions = {}
        
        for i in range(len(stages) - 1):
            current = db.query(hcm_models.DBCandidate).filter(
                hcm_models.DBCandidate.organization_id == organization_id,
                hcm_models.DBCandidate.current_stage == stages[i]
            ).count()
            
            next_stage = db.query(hcm_models.DBCandidate).filter(
                hcm_models.DBCandidate.organization_id == organization_id,
                hcm_models.DBCandidate.current_stage == stages[i + 1]
            ).count()
            
            conversion_rate = (next_stage / current * 100) if current > 0 else 0
            conversions[f"{stages[i]}_to_{stages[i+1]}"] = round(conversion_rate, 1)
        
        return conversions

    @staticmethod
    def calculate_open_positions(db: Session, organization_id: str) -> int:
        """Count open job positions"""
        return db.query(hcm_models.DBJobOpening).filter(
            hcm_models.DBJobOpening.organization_id == organization_id,
            hcm_models.DBJobOpening.status == "Open"
        ).count()

    @staticmethod
    def calculate_average_time_to_hire(db: Session, organization_id: str) -> Dict[str, Any]:
        """Calculate average days from application to hire"""
        candidates = db.query(
            func.datediff(
                hcm_models.DBCandidate.hired_date,
                hcm_models.DBCandidate.applied_date
            ).label("days_to_hire")
        ).filter(
            hcm_models.DBCandidate.organization_id == organization_id,
            hcm_models.DBCandidate.current_stage == "Joined",
            hcm_models.DBCandidate.hired_date.isnot(None)
        ).all()
        
        if not candidates:
            return {"avg_days": 0, "total_hired": 0}
        
        days = [c[0] for c in candidates if c[0]]
        avg = sum(days) / len(days) if days else 0
        
        return {
            "avg_days": round(avg),
            "total_hired": len(days)
        }

    # ==================== PAYROLL METRICS ====================

    @staticmethod
    def calculate_payroll_summary(
        db: Session, organization_id: str, period_month: Optional[int] = None,
        period_year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Calculate payroll metrics for a period"""
        if period_month is None:
            period_month = datetime.now().month
        if period_year is None:
            period_year = datetime.now().year
        
        payroll_ledger = db.query(hcm_models.DBPayrollLedger).filter(
            hcm_models.DBPayrollLedger.organization_id == organization_id,
            extract('month', hcm_models.DBPayrollLedger.period_start_date) == period_month,
            extract('year', hcm_models.DBPayrollLedger.period_start_date) == period_year
        ).all()
        
        total_gross = sum(p.gross_salary for p in payroll_ledger if p.gross_salary)
        total_deductions = sum(p.total_deductions for p in payroll_ledger if p.total_deductions)
        total_net = sum(p.net_salary for p in payroll_ledger if p.net_salary)
        
        count = len(payroll_ledger)
        avg_gross = total_gross / count if count > 0 else 0
        avg_net = total_net / count if count > 0 else 0
        
        return {
            "period_month": period_month,
            "period_year": period_year,
            "total_employees_processed": count,
            "total_gross_salary": round(total_gross, 2),
            "total_deductions": round(total_deductions, 2),
            "total_net_salary": round(total_net, 2),
            "average_gross_salary": round(avg_gross, 2),
            "average_net_salary": round(avg_net, 2)
        }

    @staticmethod
    def calculate_salary_by_designation(
        db: Session, organization_id: str
    ) -> List[Dict[str, Any]]:
        """Calculate average salary by designation"""
        salaries = db.query(
            hcm_models.DBDesignation.name,
            func.avg(hcm_models.DBEmployee.gross_salary).label("avg_salary"),
            func.count(hcm_models.DBEmployee.id).label("count")
        ).outerjoin(
            hcm_models.DBDesignation, hcm_models.DBEmployee.designation_id == hcm_models.DBDesignation.id
        ).filter(
            hcm_models.DBEmployee.organization_id == organization_id,
            hcm_models.DBEmployee.status == "Active"
        ).group_by(hcm_models.DBDesignation.name).all()
        
        return [
            {
                "name": name or "Unassigned",
                "avg_salary": round(float(salary), 2),
                "count": count
            }
            for name, salary, count in salaries
        ]

    @staticmethod
    def calculate_cost_of_employment(db: Session, organization_id: str) -> Dict[str, Any]:
        """Calculate total cost of employment (salary + benefits + payroll taxes)"""
        employees = db.query(hcm_models.DBEmployee).filter(
            hcm_models.DBEmployee.organization_id == organization_id,
            hcm_models.DBEmployee.status == "Active"
        ).all()
        
        total_gross = sum(e.gross_salary or 0 for e in employees)
        total_employees = len(employees)
        
        # Estimate payroll taxes at 20% of gross (varies by country)
        payroll_tax_rate = 0.20
        estimated_tax = total_gross * payroll_tax_rate
        
        total_coe = total_gross + estimated_tax
        coe_per_employee = total_coe / total_employees if total_employees > 0 else 0
        
        return {
            "total_gross_salary": round(total_gross, 2),
            "estimated_payroll_tax": round(estimated_tax, 2),
            "total_cost_of_employment": round(total_coe, 2),
            "cost_per_employee": round(coe_per_employee, 2),
            "active_employees": total_employees
        }

    # ==================== DASHBOARD SUMMARY ====================

    @staticmethod
    def calculate_dashboard_metrics(db: Session, organization_id: str) -> Dict[str, Any]:
        """Calculate all key metrics for dashboard"""
        try:
            total_active = AnalyticsCalculator.calculate_total_employees(db, organization_id, "Active")
            total_all = AnalyticsCalculator.calculate_total_employees(db, organization_id, None)
            
            # Headcount metrics
            headcount_trends = AnalyticsCalculator.calculate_headcount_trends(db, organization_id, 6)
            current_headcount = headcount_trends[-1]['count'] if headcount_trends else 0
            previous_headcount = headcount_trends[-2]['count'] if len(headcount_trends) > 1 else current_headcount
            headcount_change_pct = (
                ((current_headcount - previous_headcount) / previous_headcount * 100)
                if previous_headcount > 0 else 0
            )
            
            # Turnover metrics
            turnover_data = AnalyticsCalculator.calculate_turnover_rate(db, organization_id, 12)
            retention_rate = AnalyticsCalculator.calculate_retention_rate(db, organization_id)
            
            # Recruitment metrics
            open_positions = AnalyticsCalculator.calculate_open_positions(db, organization_id)
            total_candidates = db.query(hcm_models.DBCandidate).filter(
                hcm_models.DBCandidate.organization_id == organization_id
            ).count()
            
            # Payroll metrics
            payroll_summary = AnalyticsCalculator.calculate_payroll_summary(db, organization_id)
            coe = AnalyticsCalculator.calculate_cost_of_employment(db, organization_id)
            
            return {
                # Real calculated metrics
                "workforce_velocity": f"{round(headcount_change_pct, 1)}%",  # Month-over-month growth
                "retention_vector": f"{retention_rate}%",  # Overall retention rate
                "turnover_rate": f"{turnover_data['turnover_rate']}%",  # Annualized turnover
                "cost_per_employee": f"${coe['cost_per_employee']:,.0f}",  # Real COE calculation
                
                # Workforce data
                "total_active_employees": total_active,
                "total_employees": total_all,
                "new_hires_30d": AnalyticsCalculator.calculate_new_hires(db, organization_id, 30),
                
                # Recruitment data
                "total_candidates": total_candidates,
                "open_positions": open_positions,
                
                # Distributions
                "department_distribution": AnalyticsCalculator.calculate_employees_by_department(db, organization_id),
                "gender_distribution": AnalyticsCalculator.calculate_employees_by_gender(db, organization_id),
                "designation_distribution": AnalyticsCalculator.calculate_employees_by_grade(db, organization_id),
                
                # Trends
                "headcount_trends": headcount_trends,
                "recruitment_funnel": AnalyticsCalculator.calculate_recruitment_funnel(db, organization_id),
                
                # Payroll
                "payroll_summary": payroll_summary,
                "total_monthly_payroll": payroll_summary['total_gross_salary'],
            }
        except Exception as e:
            logger.error(f"Error calculating dashboard metrics: {str(e)}", exc_info=True)
            raise
