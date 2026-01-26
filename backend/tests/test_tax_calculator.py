"""Unit tests for tax calculator service."""
import pytest
from sqlalchemy.orm import Session

from backend.domains.core.models import DBOrganization
from backend.domains.hcm.models import DBEmployee, DBTaxSlab
from backend.services import tax_calculator


@pytest.fixture
def org(db: Session):
    """Create test organization"""
    org = DBOrganization(id="ORG_TAX_TEST", name="Tax Test Org", code="TAX")
    db.add(org)
    db.commit()
    return org


@pytest.fixture
def employee(db: Session, org):
    """Create test employee with monthly gross salary"""
    emp = DBEmployee(
        id="EMP_TAX_001",
        email="taxtest@example.com",
        name="Tax Test Employee",
        organization_id=org.id,
        status="Active",
        gross_salary=100000.0,  # Monthly: 100,000
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@pytest.fixture
def tax_slabs(db: Session, org):
    """Create tax slabs for 2025-2026"""
    slabs = [
        DBTaxSlab(
            id="SLAB_1",
            organization_id=org.id,
            tax_year="2025-2026",
            min_income=0,
            max_income=500000,
            fixed_tax=0.0,
            tax_rate=0.0,
            excess_over=0.0,
            is_active=True,
        ),
        DBTaxSlab(
            id="SLAB_2",
            organization_id=org.id,
            tax_year="2025-2026",
            min_income=500001,
            max_income=1500000,
            fixed_tax=0.0,
            tax_rate=5.0,  # 5% on excess
            excess_over=500000,
            is_active=True,
        ),
        DBTaxSlab(
            id="SLAB_3",
            organization_id=org.id,
            tax_year="2025-2026",
            min_income=1500001,
            max_income=None,  # No upper limit
            fixed_tax=50000.0,
            tax_rate=10.0,  # 10% on excess
            excess_over=1500000,
            is_active=True,
        ),
    ]
    for slab in slabs:
        db.add(slab)
    db.commit()
    return slabs


def test_tax_calculation_no_slabs(db: Session, employee):
    """Test tax calculation with no tax slabs (should return 0)"""
    result = tax_calculator.calculate_employee_tax(db, employee.id, "2025-2026")
    
    assert result["employeeId"] == employee.id
    assert result["taxYear"] == "2025-2026"
    assert result["annualGrossIncome"] == 1200000.0  # 100,000 * 12
    assert result["grossTax"] == 0.0
    assert result["monthlyTax"] == 0.0


def test_tax_calculation_with_slabs(db: Session, employee, tax_slabs):
    """Test tax calculation with progressive tax slabs"""
    result = tax_calculator.calculate_employee_tax(db, employee.id, "2025-2026")
    
    # Annual income: 100,000 * 12 = 1,200,000
    # Falls in SLAB_2: min=500001, max=1500000, rate=5%, excess_over=500000
    # Tax = 0 + (1,200,000 - 500,000) * 5% = 700,000 * 0.05 = 35,000
    
    assert result["employeeId"] == employee.id
    assert result["taxYear"] == "2025-2026"
    assert result["annualGrossIncome"] == 1200000.0
    assert result["grossTax"] == 35000.0
    assert result["monthlyTax"] == pytest.approx(2916.67, rel=1e-2)  # 35000 / 12


def test_tax_calculation_high_income(db: Session, org, tax_slabs):
    """Test tax calculation for high income employee"""
    # Create employee with high salary
    emp = DBEmployee(
        id="EMP_TAX_HIGH",
        email="high@example.com",
        name="High Income Employee",
        organization_id=org.id,
        status="Active",
        gross_salary=200000.0,  # Monthly: 200,000 = Annual: 2,400,000
    )
    db.add(emp)
    db.commit()
    
    result = tax_calculator.calculate_employee_tax(db, emp.id, "2025-2026")
    
    # Annual income: 200,000 * 12 = 2,400,000
    # Falls in SLAB_3: min=1500001, fixed=50000, rate=10%, excess_over=1500000
    # Tax = 50,000 + (2,400,000 - 1,500,000) * 10% = 50,000 + 90,000 = 140,000
    
    assert result["annualGrossIncome"] == 2400000.0
    assert result["grossTax"] == 140000.0
    assert result["monthlyTax"] == pytest.approx(11666.67, rel=1e-2)  # 140000 / 12


def test_tax_calculation_zero_salary(db: Session, org):
    """Test tax calculation with zero salary"""
    emp = DBEmployee(
        id="EMP_TAX_ZERO",
        email="zero@example.com",
        name="Zero Salary Employee",
        organization_id=org.id,
        status="Active",
        gross_salary=0.0,
    )
    db.add(emp)
    db.commit()
    
    result = tax_calculator.calculate_employee_tax(db, emp.id, "2025-2026")
    
    assert result["annualGrossIncome"] == 0.0
    assert result["grossTax"] == 0.0
    assert result["monthlyTax"] == 0.0


def test_tax_calculation_employee_not_found(db: Session):
    """Test tax calculation for non-existent employee"""
    with pytest.raises(ValueError, match="Employee not found"):
        tax_calculator.calculate_employee_tax(db, "NONEXISTENT", "2025-2026")


def test_tax_calculation_low_income_bracket(db: Session, employee, tax_slabs):
    """Test tax calculation in lowest tax bracket"""
    # Create employee with low salary that falls in SLAB_1
    emp = DBEmployee(
        id="EMP_TAX_LOW",
        email="low@example.com",
        name="Low Income Employee",
        organization_id=employee.organization_id,
        status="Active",
        gross_salary=30000.0,  # Monthly: 30,000 = Annual: 360,000 (< 500,000)
    )
    db.add(emp)
    db.commit()
    
    result = tax_calculator.calculate_employee_tax(db, emp.id, "2025-2026")
    
    # Falls in SLAB_1: 0% tax for income up to 500,000
    assert result["annualGrossIncome"] == 360000.0
    assert result["grossTax"] == 0.0
    assert result["monthlyTax"] == 0.0


def test_tax_slab_selection_boundary(db: Session, org):
    """Test tax slab selection at boundary values"""
    # Create slabs
    slabs = [
        DBTaxSlab(
            id="SLAB_B1",
            organization_id=org.id,
            tax_year="2025-2026",
            min_income=0,
            max_income=500000,
            fixed_tax=0.0,
            tax_rate=0.0,
            excess_over=0.0,
            is_active=True,
        ),
        DBTaxSlab(
            id="SLAB_B2",
            organization_id=org.id,
            tax_year="2025-2026",
            min_income=500001,
            max_income=None,
            fixed_tax=0.0,
            tax_rate=5.0,
            excess_over=500000,
            is_active=True,
        ),
    ]
    for slab in slabs:
        db.add(slab)
    db.commit()
    
    # Create employee exactly at boundary: 500,000 annual income
    emp = DBEmployee(
        id="EMP_BOUNDARY",
        email="boundary@example.com",
        name="Boundary Employee",
        organization_id=org.id,
        status="Active",
        gross_salary=41666.67,  # 41666.67 * 12 ≈ 500,000
    )
    db.add(emp)
    db.commit()
    
    result = tax_calculator.calculate_employee_tax(db, emp.id, "2025-2026")
    
    # Should fall in SLAB_B1 with 0% tax
    assert result["grossTax"] == 0.0


def test_multiple_tax_years(db: Session, employee):
    """Test that different tax years are handled correctly"""
    # Create slabs for 2024-2025
    org_id = employee.organization_id
    slab_2024 = DBTaxSlab(
        id="SLAB_2024",
        organization_id=org_id,
        tax_year="2024-2025",
        min_income=0,
        max_income=None,
        fixed_tax=0.0,
        tax_rate=3.0,
        excess_over=400000,
        is_active=True,
    )
    db.add(slab_2024)
    db.commit()
    
    # Calculate for 2024-2025 (should find the slab)
    result_2024 = tax_calculator.calculate_employee_tax(db, employee.id, "2024-2025")
    
    # Calculate for 2025-2026 (no slab, should return 0)
    result_2025 = tax_calculator.calculate_employee_tax(db, employee.id, "2025-2026")
    
    # 2024-2025: Annual=1,200,000, tax = (1,200,000 - 400,000) * 3% = 24,000
    assert result_2024["grossTax"] == 24000.0
    
    # 2025-2026: No slab, tax = 0
    assert result_2025["grossTax"] == 0.0


def test_tax_calculation_precision(db: Session, org):
    """Test decimal precision in tax calculations"""
    # Create employee with odd salary to test rounding
    emp = DBEmployee(
        id="EMP_PRECISION",
        email="precision@example.com",
        name="Precision Test",
        organization_id=org.id,
        status="Active",
        gross_salary=123456.78,  # Monthly
    )
    db.add(emp)
    
    slab = DBTaxSlab(
        id="SLAB_PRECISION",
        organization_id=org.id,
        tax_year="2025-2026",
        min_income=0,
        max_income=None,
        fixed_tax=0.0,
        tax_rate=7.5,
        excess_over=0.0,
        is_active=True,
    )
    db.add(slab)
    db.commit()
    
    result = tax_calculator.calculate_employee_tax(db, emp.id, "2025-2026")
    
    # Annual: 123456.78 * 12 = 1,481,481.36
    # Tax: 1,481,481.36 * 7.5% = 111,111.10
    expected_annual = 123456.78 * 12
    expected_tax = expected_annual * 0.075
    expected_monthly = round(expected_tax / 12, 2)
    
    assert result["annualGrossIncome"] == pytest.approx(expected_annual, rel=1e-2)
    assert result["grossTax"] == pytest.approx(expected_tax, rel=1e-2)
    assert result["monthlyTax"] == pytest.approx(expected_monthly, rel=1e-2)
