
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, List, Dict, Any
import uuid, time, json, logging
from datetime import datetime

from backend import schemas
from backend import models
from .core import log_audit_event

logger = logging.getLogger(__name__)

# --- Salary Component CRUD ---

def get_salary_components(db: Session, organization_id: str, active_only: bool = True, skip: int = 0, limit: int = 100):
    """Get salary components for organization"""
    query = db.query(models.DBSalaryComponent).filter(
        models.DBSalaryComponent.organization_id == organization_id
    )
    if active_only:
        query = query.filter(models.DBSalaryComponent.is_active == True)
    return query.order_by(models.DBSalaryComponent.display_order).offset(skip).limit(limit).all()


def create_salary_component(db: Session, component: schemas.SalaryComponentCreate, user_id: str):
    """Create a new salary component"""
    db_component = models.DBSalaryComponent(
        id=f"SC-{int(time.time() * 1000)}",
        organization_id=component.organization_id,
        code=component.code.upper(),
        name=component.name,
        description=component.description,
        component_type=component.component_type,
        calculation_type=component.calculation_type,
        percentage_of=component.percentage_of,
        default_amount=component.default_amount,
        is_taxable=component.is_taxable,
        is_statutory=component.is_statutory,
        is_active=component.is_active,
        display_order=component.display_order,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    return db_component


def update_salary_component(db: Session, component_id: str, component: schemas.SalaryComponentCreate, user_id: str):
    """Update salary component"""
    db_component = db.query(models.DBSalaryComponent).filter(
        models.DBSalaryComponent.id == component_id
    ).first()
    if not db_component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    for key, value in component.dict(exclude_unset=True).items():
        if key == "code": value = value.upper()
        if hasattr(db_component, key):
            setattr(db_component, key, value)
            
    db_component.updated_by = user_id
    db.commit()
    db.refresh(db_component)
    return db_component


def delete_salary_component(db: Session, component_id: str):
    """Delete salary component"""
    db_component = db.query(models.DBSalaryComponent).filter(
        models.DBSalaryComponent.id == component_id
    ).first()
    if not db_component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    # Soft delete prefered or hard delete? Logic was Deactivate.
    db_component.is_active = False
    db.commit()
    return {"success": True, "message": "Component deactivated"}


# --- Tax Slab CRUD ---

def get_tax_slabs(db: Session, organization_id: str, tax_year: str = None, skip: int = 0, limit: int = 100):
    """Get tax slabs"""
    query = db.query(models.DBTaxSlab).filter(
        models.DBTaxSlab.organization_id == organization_id,
        models.DBTaxSlab.is_active == True
    )
    if tax_year:
        query = query.filter(models.DBTaxSlab.tax_year == tax_year)
    return query.order_by(models.DBTaxSlab.min_income).offset(skip).limit(limit).all()


def create_tax_slab(db: Session, slab: schemas.TaxSlabCreate, user_id: str):
    """Create tax slab"""
    db_slab = models.DBTaxSlab(
        id=f"TS-{int(time.time() * 1000)}",
        organization_id=slab.organization_id,
        tax_year=slab.tax_year,
        min_income=slab.min_income,
        max_income=slab.max_income,
        fixed_tax=slab.fixed_tax,
        tax_rate=slab.tax_rate,
        excess_over=slab.excess_over,
        is_active=slab.is_active,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(db_slab)
    db.commit()
    db.refresh(db_slab)
    return db_slab


def calculate_income_tax(db: Session, organization_id: str, annual_income: float, tax_year: str):
    """Calculate income tax based on tax slabs"""
    slabs = get_tax_slabs(db, organization_id, tax_year)
    
    if not slabs:
        return 0.0
    
    for slab in slabs:
        max_income = slab.max_income or float('inf')
        if slab.min_income <= annual_income <= max_income:
            excess = max(0, annual_income - slab.excess_over)
            tax = slab.fixed_tax + (excess * slab.tax_rate / 100)
            return tax
    
    return 0.0


# --- Payroll Settings ---

def get_payroll_settings(db: Session, organization_id: str):
    db_settings = (
        db.query(models.DBPayrollSettings)
        .filter(models.DBPayrollSettings.organization_id == organization_id)
        .first()
    )
    if not db_settings:
        # Create default if missing
        db_settings = models.DBPayrollSettings(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            created_by="system",
            calculation_method="Per Month",
            custom_formulas='{"staff": "", "worker": ""}',
            overtime_rules="{}",
            currency="PKR",
            tax_year_start="July",
            allow_negative_salary=False,
            pay_frequency="Monthly",
            pay_day=1,
            tax_calculation_method="Annualized",
            eobi_enabled=True,
            social_security_enabled=True,
            overtime_enabled=True,
            overtime_rate=1.5,
        )
        db.add(db_settings)
        db.commit()
        db.refresh(db_settings)

    # Manual Mapping to Schema
    return schemas.PayrollSettings(
        id=db_settings.id,
        organizationId=db_settings.organization_id,
        calculationMethod=db_settings.calculation_method,
        customFormulas=(
            json.loads(db_settings.custom_formulas)
            if db_settings.custom_formulas
            else {}
        ),
        overtime=(
            json.loads(db_settings.overtime_rules) if db_settings.overtime_rules else {}
        ),
        # Base fields
        currency=db_settings.currency or "PKR",
        taxYearStart=db_settings.tax_year_start or "July",
        allowNegativeSalary=db_settings.allow_negative_salary,
        payFrequency=db_settings.pay_frequency or "Monthly",
        payDay=db_settings.pay_day,
        taxCalculationMethod=db_settings.tax_calculation_method or "Annualized",
        eobiEnabled=db_settings.eobi_enabled,
        socialSecurityEnabled=db_settings.social_security_enabled,
        overtimeEnabled=db_settings.overtime_enabled,
        overtimeRate=db_settings.overtime_rate,
        created_at=db_settings.created_at,
        updated_at=db_settings.updated_at,
        created_by=db_settings.created_by,
        updated_by=db_settings.updated_by,
    )


def save_payroll_settings(
    db: Session, settings: schemas.PayrollSettingsCreate, user_id: str
):
    db_settings = (
        db.query(models.DBPayrollSettings)
        .filter(models.DBPayrollSettings.organization_id == settings.organization_id)
        .first()
    )

    if not db_settings:
        db_settings = models.DBPayrollSettings(
            id=str(uuid.uuid4()),
            organization_id=settings.organization_id,
            created_by=user_id,
        )
        db.add(db_settings)

    # Update logic
    db_settings.calculation_method = settings.calculationMethod
    db_settings.custom_formulas = json.dumps(settings.customFormulas)
    db_settings.overtime_rules = json.dumps(settings.overtime)

    # Update Standard Fields
    db_settings.currency = settings.currency
    db_settings.tax_year_start = settings.taxYearStart
    db_settings.allow_negative_salary = settings.allowNegativeSalary
    db_settings.pay_frequency = settings.payFrequency
    db_settings.pay_day = settings.payDay
    db_settings.tax_calculation_method = settings.taxCalculationMethod
    db_settings.eobi_enabled = settings.eobiEnabled
    db_settings.social_security_enabled = settings.socialSecurityEnabled
    db_settings.overtime_enabled = settings.overtimeEnabled
    db_settings.overtime_rate = settings.overtimeRate

    db_settings.updated_by = user_id
    db.commit()
    db.refresh(db_settings)

    return get_payroll_settings(db, settings.organization_id)


# --- Employee Salary Structure ---

def get_employee_salary_structure(db: Session, employee_id: str):
    """Get employee's salary structure"""
    structures = db.query(models.DBEmployeeSalaryStructure).filter(
        models.DBEmployeeSalaryStructure.employee_id == employee_id,
        models.DBEmployeeSalaryStructure.is_active == True
    ).all()
    
    # Enrich with component details
    for s in structures:
        if s.component:
            s.component_name = s.component.name
            s.component_type = s.component.component_type
    
    return structures


def set_employee_salary_structure(db: Session, structure: schemas.EmployeeSalaryStructureCreate, user_id: str):
    """Add or update employee salary component"""
    # Check if already exists
    existing = db.query(models.DBEmployeeSalaryStructure).filter(
        models.DBEmployeeSalaryStructure.employee_id == structure.employee_id,
        models.DBEmployeeSalaryStructure.component_id == structure.component_id,
        models.DBEmployeeSalaryStructure.is_active == True
    ).first()
    
    if existing:
        existing.amount = structure.amount
        existing.percentage = structure.percentage
        existing.effective_from = structure.effective_from
        existing.effective_to = structure.effective_to
        existing.updated_by = user_id
        db.commit()
        db.refresh(existing)
        return existing
    
    db_structure = models.DBEmployeeSalaryStructure(
        employee_id=structure.employee_id,
        component_id=structure.component_id,
        amount=structure.amount,
        percentage=structure.percentage,
        effective_from=structure.effective_from,
        effective_to=structure.effective_to,
        is_active=structure.is_active,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_structure)
    db.commit()
    db.refresh(db_structure)
    return db_structure


# --- Payroll Run ---

def get_payroll_runs(db: Session, organization_id: str, skip: int = 0, limit: int = 50):
    """Get all payroll runs for an organization"""
    return db.query(models.DBPayrollRun).filter(
        models.DBPayrollRun.organization_id == organization_id
    ).order_by(
        models.DBPayrollRun.period_year.desc(),
        models.DBPayrollRun.period_month.desc()
    ).offset(skip).limit(limit).all()


def create_payroll_run(db: Session, run: schemas.PayrollRunCreate, user_id: str):
    """Create a new payroll run (draft)"""
    existing = db.query(models.DBPayrollRun).filter(
        models.DBPayrollRun.organization_id == run.organization_id,
        models.DBPayrollRun.period_month == run.period_month,
        models.DBPayrollRun.period_year == run.period_year
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Payroll run already exists for {run.period_month} {run.period_year}")
    
    db_run = models.DBPayrollRun(
        id=f"PR-{int(time.time() * 1000)}",
        organization_id=run.organization_id,
        period_month=run.period_month,
        period_year=run.period_year,
        status="Draft",
        notes=run.notes,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    return db_run


def process_payroll_run(db: Session, run_id: str, user_id: str):
    """Process payroll for all active employees"""
    run = db.query(models.DBPayrollRun).filter(models.DBPayrollRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found")
    
    if run.status not in ["Draft", "Processing"]:
        raise HTTPException(status_code=400, detail=f"Cannot process payroll in '{run.status}' status")
    
    run.status = "Processing"
    db.commit()
    
    # Get all active employees
    employees = db.query(models.DBEmployee).filter(
        models.DBEmployee.organization_id == run.organization_id,
        models.DBEmployee.status == "Active"
    ).all()
    
    total_gross = 0.0
    total_deductions = 0.0
    total_net = 0.0
    processed = 0
    
    for emp in employees:
        payslip = _calculate_employee_payroll(db, emp, run)
        
        total_gross += payslip.gross_salary
        total_deductions += payslip.total_deductions
        total_net += payslip.net_salary
        processed += 1
    
    # Update run totals
    run.status = "Processed"
    run.total_employees = len(employees)
    run.processed_employees = processed
    run.total_gross = total_gross
    run.total_deductions = total_deductions
    run.total_net = total_net
    run.processed_at = datetime.now().isoformat()
    run.processed_by = user_id
    run.updated_by = user_id
    
    db.commit()
    db.refresh(run)
    return run


def _calculate_employee_payroll(db: Session, employee, run):
    """Calculate payroll for a single employee"""
    basic = employee.gross_salary or 0.0
    house_rent = getattr(employee, 'house_rent', 0.0) or 0.0
    medical = 0.0
    transport = 0.0
    other_allowances = 0.0
    
    # Get custom salary structure
    structures = get_employee_salary_structure(db, employee.id)
    for s in structures:
        if s.component and s.component.component_type == "earning":
            if s.component.code == "MEDICAL":
                medical = s.amount
            elif s.component.code == "TRANSPORT":
                transport = s.amount
            else:
                other_allowances += s.amount
    
    gross = basic + house_rent + medical + transport + other_allowances
    
    # Deductions
    annual_income = gross * 12
    tax_year = f"{run.period_year}-{int(run.period_year) + 1}"
    
    # Use standard calc for now, enhanced is separate
    annual_tax = calculate_income_tax(db, run.organization_id, annual_income, tax_year)
    monthly_tax = annual_tax / 12
    
    eobi = 0.0
    if employee.eobi_status:
        eobi = min(gross * 0.01, 250)
    
    social_security = 0.0
    if employee.social_security_status:
        social_security = gross * 0.05
    
    loan = 0.0
    other_deductions = 0.0
    for s in structures:
        if s.component and s.component.component_type == "deduction":
            if s.component.code == "LOAN":
                loan = s.amount
            else:
                other_deductions += s.amount
    
    total_deductions = monthly_tax + eobi + social_security + loan + other_deductions
    net = gross - total_deductions
    
    # Upsert Ledger
    existing = db.query(models.DBPayrollLedger).filter(
        models.DBPayrollLedger.employee_id == employee.id,
        models.DBPayrollLedger.period_month == run.period_month,
        models.DBPayrollLedger.period_year == run.period_year
    ).first()
    
    if existing:
        payslip = existing
    else:
        payslip = models.DBPayrollLedger(
            organization_id=run.organization_id,
            employee_id=employee.id,
            payroll_run_id=run.id,
            period_month=run.period_month,
            period_year=run.period_year,
            created_by=run.created_by
        )
        db.add(payslip)
    
    payslip.basic_salary = basic
    payslip.house_rent = house_rent
    payslip.medical_allowance = medical
    payslip.transport_allowance = transport
    payslip.other_allowances = other_allowances
    payslip.gross_salary = gross
    payslip.income_tax = monthly_tax
    payslip.eobi_deduction = eobi
    payslip.social_security = social_security
    payslip.loan_deduction = loan
    payslip.other_deductions = other_deductions
    payslip.total_deductions = total_deductions
    payslip.net_salary = net
    payslip.status = "Processed"
    payslip.updated_by = run.updated_by
    
    db.commit()
    db.refresh(payslip)
    return payslip


def finalize_payroll_run(db: Session, run_id: str, user_id: str, payment_mode: str = "Bank Transfer"):
    """Finalize and mark payroll as paid"""
    run = db.query(models.DBPayrollRun).filter(models.DBPayrollRun.id == run_id).first()
    if not run: raise HTTPException(404, "Payroll run not found")
    if run.status != "Processed": raise HTTPException(400, "Payroll must be processed first")
    
    # Update payslips
    db.query(models.DBPayrollLedger).filter(
        models.DBPayrollLedger.payroll_run_id == run_id
    ).update({
        "status": "Paid",
        "payment_date": datetime.now().isoformat(),
        "payment_mode": payment_mode,
        "updated_by": user_id
    })
    
    run.status = "Paid"
    run.paid_at = datetime.now().isoformat()
    run.paid_by = user_id
    run.updated_by = user_id
    
    db.commit()
    db.refresh(run)
    return run


def get_payroll_run_details(db: Session, run_id: str, skip: int = 0, limit: int = 100):
    payslips = db.query(models.DBPayrollLedger).filter(
        models.DBPayrollLedger.payroll_run_id == run_id
    ).offset(skip).limit(limit).all()
    
    for p in payslips:
        if p.employee:
            p.employee_name = p.employee.name
            p.employee_code = p.employee.employee_code
    return payslips


def get_employee_payslip(db: Session, employee_id: str, period_month: str, period_year: str):
    payslip = db.query(models.DBPayrollLedger).filter(
        models.DBPayrollLedger.employee_id == employee_id,
        models.DBPayrollLedger.period_month == period_month,
        models.DBPayrollLedger.period_year == period_year
    ).first()
    
    if not payslip:
        raise HTTPException(404, "Payslip not found")
    
    if payslip.employee:
        payslip.employee_name = payslip.employee.name
        payslip.employee_code = payslip.employee.employee_code
    return payslip


def get_my_payslips(db: Session, employee_id: str, year: int = None, month: str = None, skip: int = 0, limit: int = 100):
    query = db.query(models.DBPayrollLedger).filter(
        models.DBPayrollLedger.employee_id == employee_id
    )
    if year:
        query = query.filter(models.DBPayrollLedger.period_year == str(year))
    if month:
        query = query.filter(models.DBPayrollLedger.period_month == month)
    
    return query.order_by(
        models.DBPayrollLedger.period_year.desc(),
        models.DBPayrollLedger.period_month.desc()
    ).offset(skip).limit(limit).all()


# --- Enhanced Calc / Tax Deductions ---

def get_tax_deduction_types(db: Session, organization_id: str, active_only: bool = True):
    query = db.query(models.DBTaxDeductionType).filter(
        models.DBTaxDeductionType.organization_id == organization_id
    )
    if active_only: query = query.filter(models.DBTaxDeductionType.is_active == True)
    return query.order_by(models.DBTaxDeductionType.display_order).all()

def create_tax_deduction_type(db: Session, deduction_type: schemas.TaxDeductionTypeCreate, user_id: str):
    db_type = models.DBTaxDeductionType(
        id=f"TDT-{int(time.time() * 1000)}",
        organization_id=deduction_type.organization_id,
        code=deduction_type.code.upper(),
        name=deduction_type.name,
        section=deduction_type.section,
        description=deduction_type.description,
        deduction_type=deduction_type.deduction_type,
        max_income_limit=deduction_type.max_income_limit,
        calc_percentage=deduction_type.calc_percentage,
        calc_income_percentage=deduction_type.calc_income_percentage,
        calc_per_unit_limit=deduction_type.calc_per_unit_limit,
        calc_max_limit=deduction_type.calc_max_limit,
        requires_document=deduction_type.requires_document,
        requires_ntn=deduction_type.requires_ntn,
        is_active=deduction_type.is_active,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_type)
    db.commit()
    db.refresh(db_type)
    return db_type

def get_employee_tax_deductions(db: Session, employee_id: str, tax_year: str):
    deductions = db.query(models.DBEmployeeTaxDeduction).filter(
        models.DBEmployeeTaxDeduction.employee_id == employee_id,
        models.DBEmployeeTaxDeduction.tax_year == tax_year
    ).all()
    for d in deductions:
        if d.deduction_type:
            d.deduction_type_name = d.deduction_type.name
            d.deduction_section = d.deduction_type.section
    return deductions

def create_employee_tax_deduction(db: Session, deduction: schemas.EmployeeTaxDeductionCreate, user_id: str):
    db_deduction = models.DBEmployeeTaxDeduction(
        employee_id=deduction.employee_id,
        deduction_type_id=deduction.deduction_type_id,
        tax_year=deduction.tax_year,
        claimed_amount=deduction.claimed_amount,
        number_of_children=deduction.number_of_children,
        institution_name=deduction.institution_name,
        institution_ntn=deduction.institution_ntn,
        status="Pending",
        created_by=user_id,
        updated_by=user_id
    )
    db.add(db_deduction)
    db.commit()
    db.refresh(db_deduction)
    return db_deduction

def delete_employee_tax_deduction(db: Session, deduction_id: int):
    deduction = db.query(models.DBEmployeeTaxDeduction).filter(
        models.DBEmployeeTaxDeduction.id == deduction_id
    ).first()
    if not deduction: raise HTTPException(404, "Tax deduction not found")
    db.delete(deduction)
    db.commit()
    return {"success": True}

def calculate_section_60d(taxable_income: float, tuition_paid: float, num_children: int) -> float:
    if taxable_income >= 1_500_000: return 0.0
    if num_children <= 0 or tuition_paid <= 0: return 0.0
    
    option1 = tuition_paid * 0.05
    option2 = taxable_income * 0.25
    option3 = 60_000 * num_children
    return min(option1, option2, option3)

def calculate_enhanced_income_tax(
    db: Session, 
    organization_id: str, 
    employee_id: str,
    annual_income: float, 
    tax_year: str
) -> dict:
    deductions = get_employee_tax_deductions(db, employee_id, tax_year)
    
    section_60d_amount = 0.0
    other_allowances = 0.0
    charitable_credit = 0.0
    insurance_credit = 0.0
    
    for d in deductions:
        if d.status != "Approved": continue
        amount = d.approved_amount or d.claimed_amount
        if d.deduction_type:
            section = d.deduction_type.section
            d_type = d.deduction_type.deduction_type
            
            if section == "60D":
                section_60d_amount = calculate_section_60d(annual_income, amount, d.number_of_children or 0)
            elif d_type == "allowance":
                other_allowances += amount
            elif d_type == "credit":
                if section == "62": charitable_credit += amount * 0.35
                elif section == "64": insurance_credit += amount * 0.20
    
    total_allowances = section_60d_amount + other_allowances
    taxable_income = max(0, annual_income - total_allowances)
    
    gross_tax = calculate_income_tax(db, organization_id, taxable_income, tax_year)
    
    total_credits = charitable_credit + insurance_credit
    annual_tax = max(0, gross_tax - total_credits)
    monthly_tax = annual_tax / 12
    
    return {
        "employee_id": employee_id,
        "tax_year": tax_year,
        "annual_gross_income": annual_income,
        "section_60d_tuition": section_60d_amount,
        "other_allowances": other_allowances,
        "total_deductible_allowances": total_allowances,
        "taxable_income": taxable_income,
        "gross_tax": gross_tax,
        "charitable_donation_credit": charitable_credit,
        "insurance_credit": insurance_credit,
        "total_tax_credits": total_credits,
        "annual_tax_payable": annual_tax,
        "monthly_tax": monthly_tax
    }
