
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from fastapi import HTTPException
from typing import Optional, List, Dict, Any
import uuid, time, json, logging
from datetime import datetime, timedelta

from backend import schemas
from backend import models
from .core import log_audit_event, get_user

logger = logging.getLogger(__name__)

# --- Attendance Helpers ---

def calculate_business_days(start_date_str: str, end_date_str: str, half_day: str = None) -> float:
    """Calculate business days between two dates, accounting for weekends and half-days"""
    try:
        # Handle Zulu time if present
        s_str = start_date_str.replace('Z', '+00:00')
        e_str = end_date_str.replace('Z', '+00:00')
        
        start = datetime.fromisoformat(s_str).date()
        end = datetime.fromisoformat(e_str).date()
        
        days = 0.0
        current = start
        
        while current <= end:
            # Skip weekends (Saturday=5, Sunday=6)
            if current.weekday() < 5:
                days += 1.0
            current += timedelta(days=1)
        
        # Apply half-day adjustment if applicable
        if half_day in ["AM", "PM"] and days > 0:
            days -= 0.5
        
        return float(days)
    except Exception as e:
        logger.error(f"Error calculating business days: {e}")
        return 0.0


# --- Attendance Records ---

def get_attendance_records(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    organization_id: str = None,
    department_id: str = None,
    date: str = None,
):
    query = db.query(models.DBAttendance).join(models.DBEmployee)
    
    if organization_id:
        query = query.filter(models.DBEmployee.organization_id == organization_id)
    if department_id:
        query = query.filter(models.DBEmployee.department_id == department_id)
    if date:
        query = query.filter(models.DBAttendance.date == date)
        
    return query.offset(skip).limit(limit).all()


def search_attendance_records(
    db: Session,
    organization_id: str,
    start_date: str,
    end_date: str,
    department_id: str = None,
    employee_id: str = None
):
    query = db.query(models.DBAttendance).join(models.DBEmployee).filter(
        models.DBEmployee.organization_id == organization_id,
        models.DBAttendance.date >= start_date,
        models.DBAttendance.date <= end_date
    )
    
    if department_id:
        query = query.filter(models.DBEmployee.department_id == department_id)
    if employee_id:
        query = query.filter(models.DBEmployee.id == employee_id)
        
    return query.all()


def validate_bulk_attendance_records(db: Session, records: List[schemas.AttendanceCreate], org_id: str) -> dict:
    """Validate bulk attendance upload"""
    errors = []
    
    # Check duplicate employee IDs in input
    emp_ids = [r.employee_id for r in records]
    if len(emp_ids) != len(set(emp_ids)):
        errors.append("Duplicate employee IDs in input")
        
    # Check all employees exist and belong to org
    db_emps = db.query(models.DBEmployee.id).filter(
        models.DBEmployee.id.in_(emp_ids),
        models.DBEmployee.organization_id == org_id
    ).all()
    found_ids = {e.id for e in db_emps}
    
    missing = set(emp_ids) - found_ids
    if missing:
        errors.append(f"Employees not found in organization: {', '.join(missing)}")
        
    return {"valid": len(errors) == 0, "errors": errors}


def upsert_attendance_record(db: Session, record: schemas.AttendanceCreate, user_id: str):
    """Create or update attendance for a specific date"""
    existing = db.query(models.DBAttendance).filter(
        models.DBAttendance.employee_id == record.employee_id,
        models.DBAttendance.date == record.date
    ).first()
    
    if existing:
        existing.status = record.status
        existing.check_in = record.check_in
        existing.check_out = record.check_out
        existing.overtime_hours = record.overtime_hours
        existing.updated_by = user_id
        db.commit()
        db.refresh(existing)
        return existing
    
    db_record = models.DBAttendance(
        id=f"ATT-{int(time.time() * 1000)}-{str(uuid.uuid4())[:4]}",
        employee_id=record.employee_id,
        date=record.date,
        status=record.status,
        check_in=record.check_in,
        check_out=record.check_out,
        overtime_hours=record.overtime_hours,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def bulk_create_attendance(db: Session, records: List[schemas.AttendanceCreate], user_id: str) -> dict:
    """Process multiple attendance records in single transaction"""
    results = []
    for rec in records:
        try:
            res = upsert_attendance_record(db, rec, user_id)
            results.append(res)
        except Exception as e:
            logger.error(f"Failed to upsert attendance for {rec.employee_id}: {e}")
            
    return {"count": len(results), "status": "processed"}

def get_attendance_stats(db: Session, organization_id: str):
    today = datetime.now().date()
    today_str = today.isoformat()
    
    total_employees = db.query(models.DBEmployee).filter(
        models.DBEmployee.organization_id == organization_id,
        models.DBEmployee.status == "Active"
    ).count()
    
    today_active = db.query(models.DBAttendance).join(models.DBEmployee).filter(
        models.DBEmployee.organization_id == organization_id,
        models.DBAttendance.date == today_str,
        models.DBAttendance.status == "Present"
    ).count()
    
    late_arrivals = db.query(models.DBAttendance).join(models.DBEmployee).filter(
        models.DBEmployee.organization_id == organization_id,
        models.DBAttendance.date == today_str,
        models.DBAttendance.status == "Late"
    ).count()
    
    absent = db.query(models.DBAttendance).join(models.DBEmployee).filter(
        models.DBEmployee.organization_id == organization_id,
        models.DBAttendance.date == today_str,
        models.DBAttendance.status == "Absent"
    ).count()
    
    # Calculate on leave (simplified check)
    on_leave = db.query(models.DBLeaveRequest).join(models.DBEmployee).filter(
        models.DBEmployee.organization_id == organization_id,
        models.DBLeaveRequest.status == "Approved",
        models.DBLeaveRequest.start_date <= today_str,
        models.DBLeaveRequest.end_date >= today_str
    ).count()
    
    return {
        "total_employees": total_employees,
        "present_today": today_active + late_arrivals,
        "late_today": late_arrivals,
        "on_leave": on_leave,
        "absent_today": absent
    }


# --- Overtime ---

def create_overtime_request(db: Session, ot: schemas.OvertimeRequestCreate, user_id: str):
    db_ot = models.DBOvertimeRequest(
        id=f"OT-{int(time.time() * 1000)}",
        employee_id=ot.employee_id,
        date=ot.date,
        hours=ot.hours,
        reason=ot.reason,
        status="Pending",
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_ot)
    db.commit()
    db.refresh(db_ot)
    return db_ot

def get_overtime_requests(db: Session, skip: int = 0, limit: int = 100, employee_id: str = None, status: str = None):
    query = db.query(models.DBOvertimeRequest)
    if employee_id:
        query = query.filter(models.DBOvertimeRequest.employee_id == employee_id)
    if status:
        query = query.filter(models.DBOvertimeRequest.status == status)
    return query.offset(skip).limit(limit).all()

def update_overtime_status(db: Session, ot_id: str, status: str, user_id: str):
    db_ot = db.query(models.DBOvertimeRequest).filter(models.DBOvertimeRequest.id == ot_id).first()
    if db_ot:
        db_ot.status = status
        db_ot.approved_by = user_id if status == "Approved" else None
        db_ot.updated_by = user_id
        db.commit()
        db.refresh(db_ot)
    return db_ot


# --- Leaves ---

def get_leaves(db: Session, organization_id: str, skip: int = 0, limit: int = 100):
    query = db.query(models.DBLeaveRequest).join(models.DBEmployee).filter(
        models.DBEmployee.organization_id == organization_id
    )
    return query.offset(skip).limit(limit).all()

def get_leave_requests(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    employee_id: str = None,
    status: str = None,
):
    query = db.query(models.DBLeaveRequest)
    if employee_id:
        query = query.filter(models.DBLeaveRequest.employee_id == employee_id)
    if status:
        query = query.filter(models.DBLeaveRequest.status == status)
    
    requests = query.offset(skip).limit(limit).all()
    for req in requests:
        if req.employee:
            req.employee_name = req.employee.name
    return requests

def create_leave_request(
    db: Session, leave: schemas.LeaveRequestCreate, user_id: str
):
    db_leave = models.DBLeaveRequest(
        id=f"LR-{int(time.time())}", 
        employee_id=leave.employee_id,
        type=leave.type,
        start_date=leave.start_date,
        end_date=leave.end_date,
        days=leave.days,
        reason=leave.reason,
        status="Pending",
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave

def get_leave_types(db: Session, organization_id: str):
    """Get all leave types for an organization"""
    return db.query(models.DBLeaveType).filter(
        models.DBLeaveType.organization_id == organization_id,
        models.DBLeaveType.is_active == True
    ).all()

def create_leave_type(db: Session, leave_type: schemas.LeaveTypeCreate, user_id: str):
    """Create a new leave type"""
    db_leave_type = models.DBLeaveType(
        id=f"LT-{uuid.uuid4().hex[:8].upper()}",
        organization_id=leave_type.organization_id,
        code=leave_type.code.upper(),
        name=leave_type.name,
        description=leave_type.description,
        days_per_year=leave_type.days_per_year,
        carry_forward_allowed=leave_type.carry_forward_allowed,
        carry_forward_max=leave_type.carry_forward_max,
        requires_approval=leave_type.requires_approval,
        requires_document=leave_type.requires_document,
        min_days_notice=leave_type.min_days_notice,
        is_active=leave_type.is_active,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_leave_type)
    db.commit()
    db.refresh(db_leave_type)
    return db_leave_type

def validate_leave_request(db: Session, leave_req: schemas.LeaveRequestCreate, employee_id: str = None) -> dict:
    """Validate leave request against balance, overlaps, and business rules"""
    emp_id = employee_id or leave_req.employee_id
    errors = []
    warnings = []
    
    # Check for overlapping leave requests
    overlaps = db.query(models.DBLeaveRequest).filter(
        models.DBLeaveRequest.employee_id == emp_id,
        models.DBLeaveRequest.status.in_(["Pending", "Approved"]),
        models.DBLeaveRequest.start_date <= leave_req.end_date,
        models.DBLeaveRequest.end_date >= leave_req.start_date
    ).count()
    
    if overlaps > 0:
        errors.append("Leave request overlaps with existing leave")
    
    # Check balance
    current_year = datetime.now().year
    balance = db.query(models.DBLeaveBalance).filter(
        models.DBLeaveBalance.employee_id == emp_id,
        models.DBLeaveBalance.year == current_year
    ).first()
    
    if balance and leave_req.type != "Unpaid":
        if leave_req.type == "Annual":
            carry = getattr(balance, 'annual_carry_forward', 0.0)
            available = balance.annual_total + carry - balance.annual_used
            if leave_req.days > available:
                errors.append(f"Insufficient annual leave balance (Available: {available}, Requested: {leave_req.days})")
        elif leave_req.type == "Sick":
            available = balance.sick_total - balance.sick_used
            if leave_req.days > available:
                errors.append(f"Insufficient sick leave balance (Available: {available}, Requested: {leave_req.days})")
        elif leave_req.type == "Casual":
            available = balance.casual_total - balance.casual_used
            if leave_req.days > available:
                errors.append(f"Insufficient casual leave balance (Available: {available}, Requested: {leave_req.days})")
    
    # Check minimum notice requirement
    if leave_req.leave_type_id:
        leave_type = db.query(models.DBLeaveType).filter(
            models.DBLeaveType.id == leave_req.leave_type_id
        ).first()
        
        if leave_type and leave_type.min_days_notice > 0:
            try:
                today = datetime.now().date()
                start = datetime.fromisoformat(leave_req.start_date.replace('Z', '+00:00')).date()
                notice_days = (start - today).days
                if notice_days < leave_type.min_days_notice:
                    errors.append(f"Minimum {leave_type.min_days_notice} days notice required (Only {notice_days} days notice given)")
            except (ValueError, AttributeError):
                warnings.append("Could not validate notice requirement - invalid date format")
    
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def create_leave_request_enhanced(
    db: Session, leave: schemas.LeaveRequestCreate, user_id: str
):
    """Enhanced leave request creation with validation and auto-calculated days"""
    # Auto-calculate business days if not provided
    if not leave.days or leave.days <= 0:
        leave.days = calculate_business_days(leave.start_date, leave.end_date, leave.half_day)
    
    validation = validate_leave_request(db, leave)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail={"errors": validation["errors"]})
    
    db_leave = models.DBLeaveRequest(
        id=f"LR-{int(time.time() * 1000)}",
        organization_id=leave.organization_id,
        employee_id=leave.employee_id,
        leave_type_id=leave.leave_type_id,
        type=leave.type,
        start_date=leave.start_date,
        end_date=leave.end_date,
        days=leave.days,
        half_day=leave.half_day,
        reason=leave.reason,
        document_url=leave.document_url,
        status="Pending",
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    
    if db_leave.employee:
        db_leave.employee_name = db_leave.employee.name
    
    return db_leave


def approve_leave_request(
    db: Session, leave_id: str, approver_id: str, approval: schemas.LeaveApproval
):
    """Approve or reject a leave request with balance management"""
    db_leave = db.query(models.DBLeaveRequest).filter(models.DBLeaveRequest.id == leave_id).first()
    if not db_leave: raise HTTPException(404, "Leave request not found")
    if db_leave.status != "Pending": raise HTTPException(400, f"Leave request already {db_leave.status}")
    
    db_leave.status = approval.status
    db_leave.approved_by = approver_id
    db_leave.approved_at = datetime.now().isoformat()
    db_leave.updated_by = approver_id
    
    if approval.status == "Rejected":
        db_leave.rejection_reason = approval.rejection_reason
    elif approval.status == "Approved":
        current_year = datetime.now().year
        balance = db.query(models.DBLeaveBalance).filter(
            models.DBLeaveBalance.employee_id == db_leave.employee_id,
            models.DBLeaveBalance.year == current_year
        ).first()
        
        if not balance and db_leave.organization_id:
            balance = models.DBLeaveBalance(
                organization_id=db_leave.organization_id,
                employee_id=db_leave.employee_id,
                year=current_year,
                annual_total=14.0, sick_total=10.0, casual_total=10.0,
                annual_used=0.0, sick_used=0.0, casual_used=0.0, unpaid_used=0.0,
                created_by="System"
            )
            db.add(balance)
        
        if balance:
            if db_leave.type == "Annual": balance.annual_used += db_leave.days
            elif db_leave.type == "Sick": balance.sick_used += db_leave.days
            elif db_leave.type == "Casual": balance.casual_used += db_leave.days
            elif db_leave.type == "Unpaid": balance.unpaid_used += db_leave.days
    
    db.commit()
    db.refresh(db_leave)
    
    if db_leave.employee: db_leave.employee_name = db_leave.employee.name
    if db_leave.approver: db_leave.approver_name = db_leave.approver.name
    
    return db_leave

def get_leave_balances(db: Session, year: int = 2025):
    balances = db.query(models.DBLeaveBalance).filter(models.DBLeaveBalance.year == year).all()
    results = []
    for b in balances:
        total = b.annual_total + b.sick_total + b.casual_total
        used = b.annual_used + b.sick_used + b.casual_used
        annual_carry = getattr(b, 'annual_carry_forward', 0.0)
        annual_available = b.annual_total + annual_carry - b.annual_used
        
        obj = schemas.LeaveBalance(
            id=b.id,
            organization_id=getattr(b, 'organization_id', None),
            employee_id=b.employee_id,
            year=b.year,
            annual_total=b.annual_total,
            annual_used=b.annual_used,
            annual_carry_forward=annual_carry,
            sick_total=b.sick_total,
            sick_used=b.sick_used,
            casual_total=b.casual_total,
            casual_used=b.casual_used,
            unpaid_used=b.unpaid_used,
            name=b.employee.name if b.employee else "Unknown",
            total=total,
            used=used,
            annual=f"{int(b.annual_used)}/{int(b.annual_total)}",
            annual_available=annual_available,
        )
        results.append(obj)
    return results

def carry_forward_leave_balances(db: Session, from_year: int, to_year: int, organization_id: str):
    balances = db.query(models.DBLeaveBalance).filter(
        models.DBLeaveBalance.year == from_year,
        models.DBLeaveBalance.organization_id == organization_id
    ).all()
    
    annual_type = db.query(models.DBLeaveType).filter(
        models.DBLeaveType.organization_id == organization_id,
        models.DBLeaveType.code == "ANNUAL",
        models.DBLeaveType.is_active == True
    ).first()
    
    count = 0
    for balance in balances:
        unused_annual = balance.annual_total - balance.annual_used
        
        if annual_type and annual_type.carry_forward_allowed and unused_annual > 0:
            carry_amount = min(unused_annual, annual_type.carry_forward_max)
            
            next_balance = db.query(models.DBLeaveBalance).filter(
                models.DBLeaveBalance.employee_id == balance.employee_id,
                models.DBLeaveBalance.year == to_year
            ).first()
            
            if not next_balance:
                next_balance = models.DBLeaveBalance(
                    organization_id=organization_id,
                    employee_id=balance.employee_id,
                    year=to_year,
                    annual_total=14.0, 
                    annual_carry_forward=carry_amount,
                    annual_used=0.0,
                    sick_total=10.0, sick_used=0.0,
                    casual_total=10.0, casual_used=0.0,
                    unpaid_used=0.0,
                    created_by="System"
                )
                db.add(next_balance)
            else:
                next_balance.annual_carry_forward = carry_amount
            count += 1
            
    db.commit()
    return {"message": f"Carried forward balances for {count} employees from {from_year} to {to_year}"}

def get_team_leave_calendar(db: Session, manager_id: str, start_date: str, end_date: str):
    team_members = db.query(models.DBEmployee).filter(models.DBEmployee.line_manager_id == manager_id).all()
    team_ids = [e.id for e in team_members]
    if not team_ids: return []
    
    team_leaves = db.query(models.DBLeaveRequest).filter(
        models.DBLeaveRequest.employee_id.in_(team_ids),
        models.DBLeaveRequest.status == "Approved",
        models.DBLeaveRequest.start_date <= end_date,
        models.DBLeaveRequest.end_date >= start_date
    ).all()
    
    results = []
    for leave in team_leaves:
        results.append({
            "id": leave.id,
            "employee_id": leave.employee_id,
            "employee_name": leave.employee.name if leave.employee else "Unknown",
            "type": leave.type,
            "start_date": leave.start_date,
            "end_date": leave.end_date,
            "days": leave.days,
            "half_day": leave.half_day,
            "reason": leave.reason
        })
    return results
