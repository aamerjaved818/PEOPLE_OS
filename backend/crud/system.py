
from sqlalchemy.orm import Session
from . import core, org, payroll
from .. import schemas, models
from typing import Optional

def get_initial_data(db: Session, organization_id: Optional[str] = None, current_user: dict = None) -> schemas.InitialData:
    # 1. System Flags
    system_flags = core.get_system_flags(db, organization_id) if organization_id else None
    
    # 2. Users
    users = core.get_users(db, current_user=current_user)
    
    # 3. Structural Data
    plants = org.get_plants(db, organization_id=organization_id)
    departments = org.get_departments(db, organization_id=organization_id)
    sub_departments = org.get_sub_departments(db, organization_id=organization_id)
    designations = org.get_designations(db, organization_id=organization_id)
    grades = org.get_grades(db, organization_id=organization_id)
    shifts = org.get_shifts(db, organization_id=organization_id)
    job_levels = org.get_job_levels(db, organization_id=organization_id)
    holidays = org.get_holidays(db, organization_id=organization_id)
    banks = org.get_banks(db, organization_id=organization_id)
    positions = org.get_positions(db, organization_id=organization_id)
    
    # 4. Payroll Settings
    payroll_settings = None
    if organization_id:
        # Assuming get_payroll_settings exists or we query directly
        payroll_settings = db.query(models.DBPayrollSettings).filter(models.DBPayrollSettings.organization_id == organization_id).first()
    
    # 5. RBAC Permissions
    role_permissions_list = core.get_role_permissions_list(db, current_user=current_user)
    role_permissions = {}
    for rp in role_permissions_list:
        if rp.role not in role_permissions:
            role_permissions[rp.role] = []
        role_permissions[rp.role].append(rp.permission)
        
    # 6. Current User Profile
    current_user_profile = None
    if current_user:
        db_user = db.query(models.DBUser).filter(models.DBUser.id == current_user["id"]).first()
        if db_user:
            current_user_profile = db_user

    return schemas.InitialData(
        systemFlags=system_flags,
        payrollSettings=payroll_settings,
        users=users,
        plants=plants,
        departments=departments,
        subDepartments=sub_departments,
        designations=designations,
        grades=grades,
        shifts=shifts,
        jobLevels=job_levels,
        holidays=holidays,
        banks=banks,
        positions=positions,
        rolePermissions=role_permissions,
        currentUser=current_user_profile
    )
