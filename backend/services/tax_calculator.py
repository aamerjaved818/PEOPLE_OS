"""Simple tax calculation service for payroll.

This implements a progressive tax calculation using DBTaxSlab entries.
"""
from typing import Optional

from sqlalchemy.orm import Session

from backend.domains.hcm import models as hcm_models


def _select_slabs(db: Session, organization_id: str, tax_year: str):
    return (
        db.query(hcm_models.DBTaxSlab)
        .filter(hcm_models.DBTaxSlab.organization_id == organization_id)
        .filter(hcm_models.DBTaxSlab.tax_year == tax_year)
        .filter(hcm_models.DBTaxSlab.is_active == True)
        .order_by(hcm_models.DBTaxSlab.min_income.asc())
        .all()
    )


def _calculate_gross_tax(annual_income: float, slabs) -> float:
    """Calculate gross tax using slab definition.

    Each slab is expected to have: fixed_tax, tax_rate (percent), excess_over.
    Tax formula: gross_tax = fixed_tax + (annual_income - excess_over) * tax_rate/100
    """
    if not slabs:
        return 0.0

    # Find best matching slab: the one where min_income <= income <= max_income (or max_income is None)
    selected = None
    for slab in slabs:
        if annual_income >= (slab.min_income or 0):
            if slab.max_income is None or annual_income <= slab.max_income:
                selected = slab
                break

    if selected is None:
        # fallback to highest slab
        selected = slabs[-1]

    taxable_excess = max(0.0, annual_income - (selected.excess_over or 0.0))
    gross_tax = (selected.fixed_tax or 0.0) + taxable_excess * ((selected.tax_rate or 0.0) / 100.0)
    return float(round(gross_tax, 2))


def calculate_employee_tax(db: Session, employee_id: str, tax_year: str) -> dict:
    """Calculate annual and monthly tax for an employee.

    Returns a dict compatible with TaxCalculationDetail schema.
    """
    emp = db.query(hcm_models.DBEmployee).filter(hcm_models.DBEmployee.id == employee_id).first()
    if not emp:
        raise ValueError("Employee not found")

    org_id = emp.organization_id

    # Assume gross_salary stored is monthly; compute annual
    monthly_gross = float(emp.gross_salary or 0.0)
    annual_gross = monthly_gross * 12.0

    slabs = _select_slabs(db, org_id, tax_year)
    gross_tax = _calculate_gross_tax(annual_gross, slabs)

    # Placeholder: tax credits and deductions not implemented yet
    total_tax_credits = 0.0
    annual_tax_payable = max(0.0, gross_tax - total_tax_credits)
    monthly_tax = float(round(annual_tax_payable / 12.0, 2))

    return {
        "employeeId": employee_id,
        "taxYear": tax_year,
        "annualGrossIncome": annual_gross,
        "taxableIncome": annual_gross,
        "grossTax": gross_tax,
        "totalTaxCredits": total_tax_credits,
        "annualTaxPayable": annual_tax_payable,
        "monthlyTax": monthly_tax,
    }
