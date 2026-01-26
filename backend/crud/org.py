
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, List
import uuid, time, json, re, logging
from datetime import datetime

from backend import schemas
from backend import models
from .core import log_audit_event, provision_org_admin, ROOT_USER_ID

logger = logging.getLogger(__name__)

# --- Organizations ---

def get_organizations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DBOrganization).offset(skip).limit(limit).all()


def get_organization(db: Session, org_id: str):
    return (
        db.query(models.DBOrganization)
        .filter(models.DBOrganization.id == org_id)
        .first()
    )


def validate_organization_input(org: schemas.OrganizationCreate) -> dict:
    """Validate organization input data"""
    errors = []
    
    # Name validation
    if not org.name or not isinstance(org.name, str) or len(org.name.strip()) == 0:
        errors.append("Organization name is required and cannot be empty")
    elif len(org.name) > 255:
        errors.append("Organization name must be 255 characters or less")
    
    # Email validation if provided
    if org.email:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, org.email):
            errors.append(f"Invalid email format: {org.email}")
    
    # Phone validation if provided
    if org.phone:
        phone_pattern = r'^\+?1?\d{9,15}$'
        if not re.match(phone_pattern, org.phone):
            errors.append(f"Phone must be 9-15 digits (optionally starting with +): {org.phone}")
    
    # Code validation if provided
    if org.code:
        code_pattern = r'^[A-Z0-9-]{2,20}$'
        if not re.match(code_pattern, org.code.upper()):
            errors.append("Code must be 2-20 alphanumeric characters (uppercase/hyphens only)")
    
    # Tax identifier validation if provided (Pakistan: 7 digits)
    tax_id = getattr(org, "tax_id", None) or getattr(org, "tax_identifier", None)
    if tax_id and org.country == "PK":
        if not re.match(r'^\d{7}$', tax_id):
            errors.append("Pakistani Tax ID must be exactly 7 digits")
    
    return {"valid": len(errors) == 0, "errors": errors}


def create_organization(db: Session, org: schemas.OrganizationWithAdminCreate, user_id: str):
    """Create organization with comprehensive validation and audit trail"""
    if isinstance(user_id, dict):
        user_id = user_id.get("id", "UNKNOWN")
    
    # 1. Enforce Code == ID Rule
    final_id = org.id
    if not final_id:
        if org.code:
             final_id = org.code.upper().strip()
        else:
             final_id = f"ORG-{str(uuid.uuid4())[:8].upper()}"
    
    final_code = final_id
    
    org.id = final_id
    org.code = final_code

    # Validate input
    validation = validate_organization_input(org)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail="\n".join(validation["errors"]))
    
    try:
        # Check if organization already exists
        existing = db.query(models.DBOrganization).filter(
            models.DBOrganization.id == final_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Organization with ID '{final_id}' already exists"
            )

        db_org = models.DBOrganization(
            id=final_id,
            code=final_code,  # Enforced Equality
            name=org.name,
            is_active=org.is_active if org.is_active is not None else True,
            enabled_modules=org.enabled_modules,
            # Modern Fields
            tax_identifier=org.tax_identifier,
            registration_number=org.registration_number,
            founded_date=org.founded_date,
            email=org.email,
            phone=org.phone,
            website=org.website,
            address_line1=org.address_line1,
            address_line2=org.address_line2,
            city=org.city,
            state=org.state,
            zip_code=org.zip_code,
            country=org.country,
            logo=org.logo,
            cover_url=org.cover_url,
            industry=org.industry,
            currency=org.currency or "PKR",
            tax_year_end=org.tax_year_end,
            social_links=json.dumps(org.social_links) if org.social_links else None,
            description=org.description,
            system_authority=org.system_authority,
            approval_workflows=org.approval_workflows,
            created_by=user_id,
            updated_by=user_id
        )
        db.add(db_org)
        db.flush() 
        
        # 2. Mandatory Provision of Super Admin
        provision_org_admin(
            db=db, 
            org=db_org, 
            creator_id=user_id,
            admin_username=org.admin_username,
            admin_password=org.admin_password,
            admin_name=org.admin_name,
            admin_email=org.admin_email
        )

        db.commit()
        db.refresh(db_org)
        
        log_audit_event(
            db=db,
            user={"username": user_id, "organization_id": final_id},
            action="ORGANIZATION_CREATED",
            status="success"
        )
        return db_org
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"Failed to create organization: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create organization: {str(e)}")


def update_organization(
    db: Session, org_id: str, org: schemas.OrganizationUpdate, user_id: str
):
    try:
        db_org = (
            db.query(models.DBOrganization)
            .filter(models.DBOrganization.id == org_id)
            .first()
        )
        if db_org:
            if org.name is not None:
                db_org.name = org.name
            if org.is_active is not None:
                db_org.is_active = org.is_active
            if org.head_id is not None:
                db_org.head_id = org.head_id
    
            if org.email is not None: db_org.email = org.email
            if org.phone is not None: db_org.phone = org.phone
            if org.website is not None: db_org.website = org.website
            if org.address_line1 is not None: db_org.address_line1 = org.address_line1
            if org.address_line2 is not None: db_org.address_line2 = org.address_line2
            if org.city is not None: db_org.city = org.city
            if org.state is not None: db_org.state = org.state
            if org.zip_code is not None: db_org.zip_code = org.zip_code
            if org.country is not None: db_org.country = org.country
    
            if org.logo is not None: db_org.logo = org.logo
            if org.cover_url is not None: db_org.cover_url = org.cover_url
    
            if org.industry is not None: db_org.industry = org.industry
            if org.currency is not None: db_org.currency = org.currency
            if org.tax_year_end is not None: db_org.tax_year_end = org.tax_year_end
            if org.description is not None: db_org.description = org.description
    
            if org.tax_identifier is not None: db_org.tax_identifier = org.tax_identifier
            if org.registration_number is not None: db_org.registration_number = org.registration_number
            if org.founded_date is not None: db_org.founded_date = org.founded_date
            
            if org.enabled_modules is not None: db_org.enabled_modules = org.enabled_modules
            if org.system_authority is not None: db_org.system_authority = org.system_authority
            if org.approval_workflows is not None: db_org.approval_workflows = org.approval_workflows
            
            if org.social_links is not None:
                db_org.social_links = json.dumps(org.social_links)

            db_org.updated_by = user_id
            db.commit()
            db.refresh(db_org)
            
            log_audit_event(
                db=db,
                user={"username": user_id, "organization_id": org_id},
                action="ORGANIZATION_UPDATED",
                status="success",
                details=f"Updated properties for {org_id}"
            )
            
        return db_org
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update organization {org_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update organization: {str(e)}")


def delete_organization(db: Session, org_id: str, current_user_id: Optional[str] = None):
    # Find organization
    db_org = db.query(models.DBOrganization).filter(
        models.DBOrganization.id == org_id
    ).first()
    
    if not db_org:
        raise HTTPException(status_code=404, detail=f"Organization '{org_id}' not found")
    
    # Root Bypass Check
    is_root = False
    if current_user_id:
        if current_user_id == ROOT_USER_ID:
            is_root = True
        else:
            user = db.query(models.DBUser).filter(models.DBUser.id == current_user_id).first()
            if user and user.role and user.role.lower() == "root":
                is_root = True

    # Security check: Prevent deleting organizations with active users
    active_users = db.query(models.DBUser).filter(
        models.DBUser.organization_id == org_id,
        models.DBUser.is_active == True
    ).count()
    
    if not is_root and active_users > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete organization with {active_users} active users. Deactivate users first."
        )
    
    try:
        if is_root:
            logger.warning(f"Root User forcing delete of Organization {org_id}. Initiating Cascade Delete...")
            db.query(models.DBUser).filter(models.DBUser.organization_id == org_id).delete(synchronize_session=False)
            db.query(models.DBDepartment).filter(models.DBDepartment.organization_id == org_id).delete(synchronize_session=False)
            db.query(models.DBPosition).filter(models.DBPosition.organization_id == org_id).delete(synchronize_session=False)
            db.commit() 

        db.delete(db_org)
        db.commit()
        return {"ok": True, "message": f"Organization {org_id} deleted successfully."}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete organization: {str(e)}")


# --- Plants (Locations) & Divisions ---

def get_plants(db: Session, organization_id: Optional[str] = None):
    query = db.query(models.DBHRPlant)
    if organization_id:
        query = query.filter(models.DBHRPlant.organization_id == organization_id)
    return query.all()

def get_plant(db: Session, plant_id: str):
    return db.query(models.DBHRPlant).filter(models.DBHRPlant.id == plant_id).first()

def create_plant(db: Session, plant: schemas.PlantCreate, user_id: str):
    # 1. Validate organization exists
    org = db.query(models.DBOrganization).filter(
        models.DBOrganization.id == plant.organization_id
    ).first()
    
    if not org:
        raise HTTPException(
            status_code=404,
            detail=f"Organization '{plant.organization_id}' not found"
        )
    
    clean_code = plant.code.upper() if plant.code else f"PLANT-{str(uuid.uuid4())[:8]}"
    plant_id = clean_code
    
    existing = db.query(models.DBHRPlant).filter(
        models.DBHRPlant.code == clean_code,
        models.DBHRPlant.organization_id == plant.organization_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Plant code '{clean_code}' already exists in this organization"
        )

    db_plant = models.DBHRPlant(
        id=plant_id,
        name=plant.name,
        location=plant.location,
        code=clean_code,
        head_of_plant=plant.head_of_plant,
        contact_number=plant.contact_number,
        is_active=plant.is_active if plant.is_active is not None else True,
        current_sequence=plant.current_sequence,
        organization_id=plant.organization_id,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_plant)
    db.flush()

    # Create Divisions
    for div in plant.divisions:
        db_div = models.DBPlantDivision(
            id=str(uuid.uuid4()),
            plant_id=db_plant.id,
            name=div.name,
            code=div.code,
            is_active=div.is_active if div.is_active is not None else True,
            created_by=user_id,
            updated_by=user_id
        )
        db.add(db_div)

    try:
        db.commit()
        db.refresh(db_plant)
        
        log_audit_event(
            db=db,
            user={"username": user_id, "organization_id": plant.organization_id},
            action="PLANT_CREATED",
            status="success"
        )
        return db_plant
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create plant: {str(e)}")

def update_plant(db: Session, plant_id: str, plant: schemas.PlantCreate, user_id: str):
    db_plant = get_plant(db, plant_id)
    if not db_plant:
        return None

    db_plant.name = plant.name
    db_plant.location = plant.location
    db_plant.code = plant.code
    db_plant.head_of_plant = plant.head_of_plant
    db_plant.contact_number = plant.contact_number
    db_plant.is_active = plant.is_active
    db_plant.updated_by = user_id
    
    # Simple Division Updates (create/update)
    existing_divs = {d.id: d for d in db_plant.plant_divisions}
    processed_ids = set()

    for div_data in plant.divisions:
        if div_data.id and div_data.id in existing_divs:
            existing_div = existing_divs[div_data.id]
            existing_div.name = div_data.name
            existing_div.code = div_data.code
            existing_div.is_active = div_data.is_active
            existing_div.updated_by = user_id
            processed_ids.add(div_data.id)
        else:
            new_div = models.DBPlantDivision(
                id=str(uuid.uuid4()),
                plant_id=db_plant.id,
                name=div_data.name,
                code=div_data.code,
                is_active=div_data.is_active,
                created_by=user_id,
                updated_by=user_id
            )
            db.add(new_div)
    
    try:
        db.commit()
        db.refresh(db_plant)
        return db_plant
    except Exception as e:
        db.rollback()
        raise e

def delete_plant(db: Session, plant_id: str):
    db_plant = get_plant(db, plant_id)
    if db_plant:
        db.delete(db_plant)
        db.commit()
    return db_plant


# --- Departments ---

def get_departments(db: Session, skip: int = 0, limit: int = 100, organization_id: str = None):
    query = db.query(models.DBDepartment)
    if organization_id:
        query = query.filter(models.DBDepartment.organization_id == organization_id)
    return query.offset(skip).limit(limit).all()


def create_department(db: Session, dept: schemas.DepartmentCreate, user_id: str):
    if isinstance(user_id, dict):
        user_id = user_id.get("id", "UNKNOWN")
    
    org = db.query(models.DBOrganization).filter(
        models.DBOrganization.id == dept.organization_id
    ).first()
    
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization '{dept.organization_id}' not found")
    
    clean_code = dept.code.upper() if dept.code else f"DEPT-{str(uuid.uuid4())[:8]}"
    
    existing = db.query(models.DBDepartment).filter(
        models.DBDepartment.code == clean_code,
        models.DBDepartment.organization_id == dept.organization_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=409, detail=f"Department code '{clean_code}' already exists")
    
    dept_id = clean_code

    db_dept = models.DBDepartment(
        id=dept_id,
        code=clean_code,
        name=dept.name,
        isActive=dept.is_active if dept.is_active is not None else True,
        organization_id=dept.organization_id,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    
    log_audit_event(
        db=db,
        user={"username": user_id, "organization_id": dept.organization_id},
        action="DEPARTMENT_CREATED",
        status="success"
    )
    
    return db_dept


def update_department(db: Session, dept_id: str, dept: schemas.DepartmentCreate, user_id: str):
    db_dept = db.query(models.DBDepartment).filter(models.DBDepartment.id == dept_id).first()
    if db_dept:
        db_dept.code = dept.code
        db_dept.name = dept.name
        db_dept.is_active = dept.is_active
        db_dept.organization_id = dept.organization_id
        db_dept.updated_by = user_id
        db.commit()
        db.refresh(db_dept)
    return db_dept


def delete_department(db: Session, dept_id: str):
    db_dept = db.query(models.DBDepartment).filter(models.DBDepartment.id == dept_id).first()
    if db_dept:
        db.delete(db_dept)
        db.commit()
    return db_dept


# --- SubDepartments ---

def get_sub_departments(db: Session, organization_id: str = None):
    query = db.query(models.DBSubDepartment)
    if organization_id:
        query = query.filter(models.DBSubDepartment.organization_id == organization_id)
    return query.all()


def create_sub_department(db: Session, sub: schemas.SubDepartmentCreate, user_id: str):
    sub_code = sub.code
    if not sub_code:
        parent = db.query(models.DBDepartment).filter(models.DBDepartment.id == sub.parent_department_id).first()
        parent_code = parent.code if parent else "DEPT"
        count = db.query(models.DBSubDepartment).filter(models.DBSubDepartment.parent_department_id == sub.parent_department_id).count()
        sub_code = f"{parent_code}-{str(count + 1).zfill(2)}"
    
    db_sub = models.DBSubDepartment(
        id=sub.id or str(uuid.uuid4()),
        code=sub_code.upper(),
        name=sub.name,
        parent_department_id=sub.parent_department_id,
        is_active=sub.is_active,
        organization_id=sub.organization_id,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub


def update_sub_department(db: Session, sub_id: str, sub: schemas.SubDepartmentCreate, user_id: str):
    db_sub = db.query(models.DBSubDepartment).filter(models.DBSubDepartment.id == sub_id).first()
    if db_sub:
        db_sub.code = sub.code
        db_sub.name = sub.name
        db_sub.parent_department_id = sub.parent_department_id
        db_sub.is_active = sub.is_active
        db_sub.organization_id = sub.organization_id
        db_sub.updated_by = user_id
        db.commit()
        db.refresh(db_sub)
    return db_sub


def delete_sub_department(db: Session, sub_id: str):
    db_sub = db.query(models.DBSubDepartment).filter(models.DBSubDepartment.id == sub_id).first()
    if db_sub:
        db.delete(db_sub)
        db.commit()
    return db_sub


# --- Grades ---

def get_grades(db: Session, organization_id: str = None):
    query = db.query(models.DBGrade)
    if organization_id:
        query = query.filter(models.DBGrade.organization_id == organization_id)
    return query.all()


def create_grade(db: Session, grade: schemas.GradeCreate, user_id: str):
    generated_id = grade.id if grade.id else f"GRD-{int(time.time())}"
    code = getattr(grade, "code", None) or f"G-{grade.level}-{generated_id[-4:]}"

    db_grade = models.DBGrade(
        id=generated_id,
        name=grade.name,
        level=grade.level,
        is_active=grade.is_active,
        organization_id=grade.organization_id,
        job_level_id=grade.job_level_id,
        created_by=user_id,
        updated_by=user_id,
        code=code,
    )
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    return db_grade


def update_grade(db: Session, grade_id: str, grade: schemas.GradeCreate, user_id: str):
    db_grade = db.query(models.DBGrade).filter(models.DBGrade.id == grade_id).first()
    if db_grade:
        db_grade.name = grade.name
        db_grade.level = grade.level
        db_grade.is_active = grade.is_active
        db_grade.organization_id = grade.organization_id
        db_grade.job_level_id = grade.job_level_id
        db_grade.updated_by = user_id
        db.commit()
        db.refresh(db_grade)
    return db_grade


def delete_grade(db: Session, grade_id: str):
    db_grade = db.query(models.DBGrade).filter(models.DBGrade.id == grade_id).first()
    if not db_grade:
        return None

    # Foreign Key checks handled by DB or app logic. 
    # Provided implementation includes checks for Designations, Employees, Positions
    designations = db.query(models.DBDesignation).filter(models.DBDesignation.grade_id == grade_id).first()
    if designations:
        raise HTTPException(status_code=400, detail=f"Cannot delete Grade '{db_grade.name}': Assigned to designation.")

    employees = db.query(models.DBEmployee).filter(models.DBEmployee.grade_id == grade_id).first()
    if employees:
        raise HTTPException(status_code=400, detail=f"Cannot delete Grade '{db_grade.name}': Assigned to employee.")

    positions = db.query(models.DBPosition).filter(models.DBPosition.grade_id == grade_id).first()
    if positions:
        raise HTTPException(status_code=400, detail=f"Cannot delete Grade '{db_grade.name}': Assigned to position.")

    db.delete(db_grade)
    db.commit()
    return db_grade


# --- Designations ---

def get_designations(db: Session, organization_id: str = None):
    query = db.query(models.DBDesignation)
    if organization_id:
        query = query.filter(models.DBDesignation.organization_id == organization_id)
    return query.all()


def create_designation(db: Session, desig: schemas.DesignationCreate, user_id: str, org_id: str = None):
    generated_id = desig.id if desig.id else f"DSG-{int(time.time())}"
    code = getattr(desig, "code", None) or f"DSG-{generated_id}"
    final_org_id = org_id or desig.organization_id
    dept_id = desig.department_id if desig.department_id else None
    grade_id = desig.grade_id if desig.grade_id else None

    db_desig = models.DBDesignation(
        id=generated_id,
        name=desig.name,
        grade_id=grade_id,
        department_id=dept_id,
        is_active=desig.is_active,
        organization_id=final_org_id,
        created_by=user_id,
        updated_by=user_id,
        code=code,
    )
    db.add(db_desig)
    db.commit()
    db.refresh(db_desig)
    return db_desig


def update_designation(db: Session, desig_id: str, desig: schemas.DesignationCreate, user_id: str):
    db_desig = db.query(models.DBDesignation).filter(models.DBDesignation.id == desig_id).first()
    if db_desig:
        db_desig.name = desig.name
        db_desig.grade_id = desig.grade_id
        db_desig.department_id = desig.department_id
        db_desig.is_active = desig.is_active
        db_desig.organization_id = desig.organization_id
        db_desig.updated_by = user_id
        db.commit()
        db.refresh(db_desig)
    return db_desig


def delete_designation(db: Session, desig_id: str):
    db_desig = db.query(models.DBDesignation).filter(models.DBDesignation.id == desig_id).first()
    if db_desig:
        db.delete(db_desig)
        db.commit()
    return db_desig


# --- Shifts ---

def get_shifts(db: Session, organization_id: str = None):
    query = db.query(models.DBShift)
    if organization_id:
        query = query.filter(models.DBShift.organization_id == organization_id)
    return query.all()


def create_shift(db: Session, shift: schemas.ShiftCreate, user_id: str):
    existing = db.query(models.DBShift).filter(
        models.DBShift.code == shift.code,
        models.DBShift.organization_id == shift.organization_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Shift code '{shift.code}' exists.")

    db_shift = models.DBShift(
        id=shift.id if shift.id else f"SHF-{int(time.time())}",
        name=shift.name,
        code=shift.code,
        type=shift.type,
        start_time=shift.start_time,
        end_time=shift.end_time,
        grace_period=shift.grace_period,
        break_duration=shift.break_duration,
        work_days=",".join(shift.work_days) if shift.work_days else "",
        color=shift.color,
        description=shift.description,
        isActive=shift.is_active,
        organization_id=shift.organization_id,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(db_shift)
    db.commit()
    db.refresh(db_shift)
    return db_shift


def update_shift(db: Session, shift_id: str, shift: schemas.ShiftCreate, user_id: str):
    db_shift = db.query(models.DBShift).filter(models.DBShift.id == shift_id).first()
    if db_shift:
        if db_shift.code != shift.code:
            existing = db.query(models.DBShift).filter(
                models.DBShift.code == shift.code,
                models.DBShift.organization_id == shift.organization_id,
                models.DBShift.id != shift_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"Shift code '{shift.code}' exists.")

        db_shift.name = shift.name
        db_shift.code = shift.code
        db_shift.type = shift.type
        db_shift.start_time = shift.start_time
        db_shift.end_time = shift.end_time
        db_shift.grace_period = shift.grace_period
        db_shift.break_duration = shift.break_duration
        db_shift.work_days = ",".join(shift.work_days) if shift.work_days else ""
        db_shift.color = shift.color
        db_shift.description = shift.description
        db_shift.isActive = shift.is_active
        db_shift.organization_id = shift.organization_id
        db_shift.updated_by = user_id
        db.commit()
        db.refresh(db_shift)
    return db_shift


def delete_shift(db: Session, shift_id: str):
    db_shift = db.query(models.DBShift).filter(models.DBShift.id == shift_id).first()
    if db_shift:
        db.delete(db_shift)
        db.commit()
    return db_shift


# --- Job Levels ---

def get_job_levels(db: Session, organization_id: str = None):
    query = db.query(models.DBJobLevel)
    if organization_id:
        query = query.filter(models.DBJobLevel.organization_id == organization_id)
    return query.all()


def create_job_level(db: Session, job_level: schemas.JobLevelCreate, user_id: str):
    clean_code = job_level.code.upper() if job_level.code else f"JL-{int(time.time())}"
    level_id = clean_code

    db_level = models.DBJobLevel(
        id=level_id,
        name=job_level.name,
        code=clean_code,
        description=job_level.description,
        is_active=job_level.is_active,
        organization_id=job_level.organization_id,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(db_level)
    db.commit()
    db.refresh(db_level)
    return db_level


def update_job_level(db: Session, level_id: str, job_level: schemas.JobLevelCreate, user_id: str):
    db_level = db.query(models.DBJobLevel).filter(models.DBJobLevel.id == level_id).first()
    if db_level:
        db_level.name = job_level.name
        db_level.code = job_level.code
        db_level.description = job_level.description
        db_level.is_active = job_level.is_active
        db_level.updated_by = user_id
        db.commit()
        db.refresh(db_level)
    return db_level

def delete_job_level(db: Session, job_level_id: str):
    db_job_level = db.query(models.DBJobLevel).filter(models.DBJobLevel.id == job_level_id).first()
    if not db_job_level:
        return False
        
    grades = db.query(models.DBGrade).filter(models.DBGrade.job_level_id == job_level_id).all()
    if grades:
        grade_ids = [g.id for g in grades]
        designations = db.query(models.DBDesignation).filter(models.DBDesignation.grade_id.in_(grade_ids)).first()
        if designations:
            raise HTTPException(status_code=400, detail=f"Cannot delete Job Level '{db_job_level.name}': grades are assigned.")
            
        employees = db.query(models.DBEmployee).filter(models.DBEmployee.grade_id.in_(grade_ids)).first()
        if employees:
            raise HTTPException(status_code=400, detail=f"Cannot delete Job Level '{db_job_level.name}': grades are assigned.")
            
        positions = db.query(models.DBPosition).filter(models.DBPosition.grade_id.in_(grade_ids)).first()
        if positions:
            raise HTTPException(status_code=400, detail=f"Cannot delete Job Level '{db_job_level.name}': grades are assigned.")

    db.delete(db_job_level)
    db.commit()
    return True


# --- Positions ---

def get_positions(db: Session, organization_id: str = None):
    query = db.query(models.DBPosition)
    if organization_id:
        query = query.filter(models.DBPosition.organization_id == organization_id)
    return query.all()


def create_position(db: Session, position: schemas.PositionCreate, user_id: str):
    db_pos = models.DBPosition(
        id=position.id if position.id else f"POS-{int(time.time())}",
        title=position.title,
        department_id=position.department_id,
        grade_id=position.grade_id,
        designation_id=position.designation_id,
        reports_to=position.reports_to,
        description=position.description,
        is_active=position.is_active,
        organization_id=position.organization_id,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(db_pos)
    db.commit()
    db.refresh(db_pos)
    return db_pos


def update_position(db: Session, position_id: str, position: schemas.PositionCreate, user_id: str):
    db_pos = db.query(models.DBPosition).filter(models.DBPosition.id == position_id).first()
    if db_pos:
        db_pos.title = position.title
        db_pos.department_id = position.department_id
        db_pos.grade_id = position.grade_id
        db_pos.designation_id = position.designation_id
        db_pos.reports_to = position.reports_to
        db_pos.description = position.description
        db_pos.is_active = position.is_active
        db_pos.updated_by = user_id
        db.commit()
        db.refresh(db_pos)
    return db_pos


def delete_position(db: Session, position_id: str):
    db_pos = db.query(models.DBPosition).filter(models.DBPosition.id == position_id).first()
    if db_pos:
        db.delete(db_pos)
        db.commit()
    return db_pos


# --- Holidays ---

def get_holidays(db: Session, organization_id: str = None):
    query = db.query(models.DBHoliday)
    if organization_id:
        query = query.filter(models.DBHoliday.organization_id == organization_id)
    return query.all()


def create_holiday(db: Session, holiday: schemas.HolidayCreate, user_id: str):
    db_holiday = models.DBHoliday(
        id=holiday.id if holiday.id else f"HOL-{int(time.time())}",
        name=holiday.name,
        date=holiday.date,
        type=holiday.type,
        is_recurring=holiday.is_recurring,
        description=holiday.description,
        organization_id=holiday.organization_id,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(db_holiday)
    db.commit()
    db.refresh(db_holiday)
    return db_holiday


def update_holiday(db: Session, holiday_id: str, holiday: schemas.HolidayCreate, user_id: str):
    db_holiday = db.query(models.DBHoliday).filter(models.DBHoliday.id == holiday_id).first()
    if db_holiday:
        db_holiday.name = holiday.name
        db_holiday.date = holiday.date
        db_holiday.type = holiday.type
        db_holiday.is_recurring = holiday.is_recurring
        db_holiday.description = holiday.description
        db_holiday.updated_by = user_id
        db.commit()
        db.refresh(db_holiday)
    return db_holiday


def delete_holiday(db: Session, holiday_id: str):
    db_holiday = db.query(models.DBHoliday).filter(models.DBHoliday.id == holiday_id).first()
    if db_holiday:
        db.delete(db_holiday)
        db.commit()
    return db_holiday


# --- Banks ---

def get_banks(db: Session, organization_id: str = None):
    query = db.query(models.DBBank)
    if organization_id:
        query = query.filter(models.DBBank.organization_id == organization_id)
    return query.all()


def create_bank(db: Session, bank: schemas.BankCreate, user_id: str):
    db_bank = models.DBBank(
        id=bank.id if bank.id else f"BNK-{int(time.time())}",
        bank_name=bank.bank_name,
        account_number=bank.account_number,
        account_title=bank.account_title,
        branch=bank.branch,
        iban=bank.iban,
        swift_code=bank.swift_code,
        currency=bank.currency,
        is_active=bank.is_active,
        organization_id=bank.organization_id,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(db_bank)
    db.commit()
    db.refresh(db_bank)
    return db_bank


def update_bank(db: Session, bank_id: str, bank: schemas.BankCreate, user_id: str):
    db_bank = db.query(models.DBBank).filter(models.DBBank.id == bank_id).first()
    if db_bank:
        db_bank.bank_name = bank.bank_name
        db_bank.account_number = bank.account_number
        db_bank.account_title = bank.account_title
        db_bank.branch = bank.branch
        db_bank.iban = bank.iban
        db_bank.swift_code = bank.swift_code
        db_bank.currency = bank.currency
        db_bank.is_active = bank.is_active
        db_bank.updated_by = user_id
        db.commit()
        db.refresh(db_bank)
    return db_bank


def delete_bank(db: Session, bank_id: str):
    db_bank = db.query(models.DBBank).filter(models.DBBank.id == bank_id).first()
    if db_bank:
        db.delete(db_bank)
        db.commit()
    return db_bank


# --- Employment Levels ---

def get_employment_levels(db: Session, organization_id: Optional[str] = None):
    query = db.query(models.DBEmploymentLevel).filter(models.DBEmploymentLevel.is_active == True)
    if organization_id:
        query = query.filter(models.DBEmploymentLevel.organization_id == organization_id)
    return query.all()

def create_employment_level(db: Session, level: schemas.EmploymentLevelCreate, user_id: str):
    db_level = models.DBEmploymentLevel(
        id=str(uuid.uuid4()),
        name=level.name,
        code=level.code,
        description=level.description,
        is_active=level.is_active,
        organization_id=level.organization_id,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_level)
    try:
        db.commit()
        db.refresh(db_level)
        return db_level
    except Exception as e:
        db.rollback()
        raise e

def update_employment_level(db: Session, level_id: str, level: schemas.EmploymentLevelCreate, user_id: str):
    db_level = db.query(models.DBEmploymentLevel).filter(models.DBEmploymentLevel.id == level_id).first()
    if db_level:
        db_level.name = level.name
        db_level.code = level.code
        db_level.description = level.description
        db_level.is_active = level.is_active
        db_level.updated_by = user_id
        db.commit()
        db.refresh(db_level)
    return db_level

def delete_employment_level(db: Session, level_id: str):
    db_level = db.query(models.DBEmploymentLevel).filter(models.DBEmploymentLevel.id == level_id).first()
    if db_level:
        db_level.is_active = False
        db_level.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_level)
    return db_level
