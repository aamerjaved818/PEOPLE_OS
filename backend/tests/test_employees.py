"""
Tests for Employee management and relationships.
"""
import pytest
from backend.domains.core.models import (
    DBOrganization, DBDepartment, DBHRPlant, DBSubDepartment
)
from backend.domains.hcm.models import (
    DBEmployee, DBDesignation, DBGrade, DBJobLevel, DBShift
)


@pytest.fixture
def test_org(db):
    """Create test organization"""
    org = DBOrganization(
        id="ORG_EMP",
        code="EMP_ORG",
        name="Employee Test Org",
        email="emp@org.com",
        phone="123",
        description="Test"
    )
    db.add(org)
    db.commit()
    return org


@pytest.fixture
def test_dept(db, test_org):
    """Create test department"""
    dept = DBDepartment(
        id="DEPT_EMP",
        code="DEMPT",
        name="Test Department",
        organization_id=test_org.id
    )
    db.add(dept)
    db.commit()
    return dept


@pytest.fixture
def test_grade(db, test_org):
    """Create test grade"""
    grade = DBGrade(
        id="GRADE001",
        name="Grade 1",
        level=1,
        code="G1",
        organization_id=test_org.id
    )
    db.add(grade)
    db.commit()
    return grade


@pytest.fixture
def test_designation(db, test_org, test_grade, test_dept):
    """Create test designation"""
    des = DBDesignation(
        id="DES001",
        name="Manager",
        code="MGR",
        grade_id=test_grade.id,
        department_id=test_dept.id,
        organization_id=test_org.id
    )
    db.add(des)
    db.commit()
    return des


def test_create_employee(db, test_org, test_dept, test_grade, test_designation):
    """Test creating an employee"""
    emp = DBEmployee(
        id="EMP001",
        name="John Doe",
        email="john@test.com",
        department_id=test_dept.id,
        designation_id=test_designation.id,
        grade_id=test_grade.id,
        organization_id=test_org.id,
        status="Active"
    )
    db.add(emp)
    db.commit()
    
    retrieved = db.query(DBEmployee).filter_by(id="EMP001").first()
    assert retrieved.name == "John Doe"
    assert retrieved.email == "john@test.com"


def test_employee_unique_email(db, test_org, test_dept, test_grade, test_designation):
    """Test that employee emails are unique"""
    emp1 = DBEmployee(
        id="EMP002",
        name="Jane Doe",
        email="jane@test.com",
        department_id=test_dept.id,
        designation_id=test_designation.id,
        grade_id=test_grade.id,
        organization_id=test_org.id
    )
    db.add(emp1)
    db.commit()
    
    # Attempt duplicate email
    emp2 = DBEmployee(
        id="EMP003",
        name="Jane Smith",
        email="jane@test.com",
        department_id=test_dept.id,
        designation_id=test_designation.id,
        grade_id=test_grade.id,
        organization_id=test_org.id
    )
    db.add(emp2)
    
    with pytest.raises(Exception):
        db.commit()


def test_employee_personal_details(db, test_org, test_dept, test_grade, test_designation):
    """Test employee with personal details"""
    emp = DBEmployee(
        id="EMP004",
        name="Test Employee",
        email="test@emp.com",
        department_id=test_dept.id,
        designation_id=test_designation.id,
        grade_id=test_grade.id,
        organization_id=test_org.id,
        date_of_birth="1990-01-15",
        cnic="12345-6789012-3",
        gender="Male",
        marital_status="Single",
        religion="Islam"
    )
    db.add(emp)
    db.commit()
    
    retrieved = db.query(DBEmployee).filter_by(id="EMP004").first()
    assert retrieved.date_of_birth == "1990-01-15"
    assert retrieved.cnic == "12345-6789012-3"


def test_employee_financial_details(db, test_org, test_dept, test_grade, test_designation):
    """Test employee with financial details"""
    emp = DBEmployee(
        id="EMP005",
        name="Financial Employee",
        email="fin@emp.com",
        department_id=test_dept.id,
        designation_id=test_designation.id,
        grade_id=test_grade.id,
        organization_id=test_org.id,
        gross_salary=50000.0,
        payment_mode="Bank Transfer",
        bank_account="1234567890",
        bank_name="Test Bank"
    )
    db.add(emp)
    db.commit()
    
    retrieved = db.query(DBEmployee).filter_by(id="EMP005").first()
    assert retrieved.gross_salary == 50000.0
    assert retrieved.bank_name == "Test Bank"


def test_employee_line_manager_self_reference(db, test_org, test_dept, test_grade, test_designation):
    """Test employee with line manager (self-reference FK)"""
    # Create manager
    manager = DBEmployee(
        id="EMP_MGR",
        name="Manager",
        email="manager@test.com",
        department_id=test_dept.id,
        designation_id=test_designation.id,
        grade_id=test_grade.id,
        organization_id=test_org.id
    )
    db.add(manager)
    db.commit()
    
    # Create employee with manager
    emp = DBEmployee(
        id="EMP006",
        name="Team Member",
        email="member@test.com",
        department_id=test_dept.id,
        designation_id=test_designation.id,
        grade_id=test_grade.id,
        organization_id=test_org.id,
        line_manager_id=manager.id
    )
    db.add(emp)
    db.commit()
    
    retrieved = db.query(DBEmployee).filter_by(id="EMP006").first()
    assert retrieved.line_manager_id == manager.id


def test_employee_with_subdepartment(db, test_org, test_dept, test_grade, test_designation):
    """Test employee with sub-department"""
    subdept = DBSubDepartment(
        id="SUBDEPT001",
        code="SD001",
        name="Backend Team",
        organization_id=test_org.id,
        department_id=test_dept.id
    )
    db.add(subdept)
    db.commit()
    
    emp = DBEmployee(
        id="EMP007",
        name="Dev Employee",
        email="dev@test.com",
        department_id=test_dept.id,
        designation_id=test_designation.id,
        grade_id=test_grade.id,
        organization_id=test_org.id,
        sub_department_id=subdept.id
    )
    db.add(emp)
    db.commit()
    
    retrieved = db.query(DBEmployee).filter_by(id="EMP007").first()
    assert retrieved.sub_department_id == subdept.id


def test_employee_with_shift(db, test_org, test_dept, test_grade, test_designation):
    """Test employee assigned to a shift"""
    shift = DBShift(
        id="SHIFT001",
        name="Morning Shift",
        code="MS",
        start_time="08:00",
        end_time="16:00",
        organization_id=test_org.id
    )
    db.add(shift)
    db.commit()
    
    emp = DBEmployee(
        id="EMP008",
        name="Shift Employee",
        email="shift@test.com",
        department_id=test_dept.id,
        designation_id=test_designation.id,
        grade_id=test_grade.id,
        organization_id=test_org.id,
        shift_id=shift.id
    )
    db.add(emp)
    db.commit()
    
    retrieved = db.query(DBEmployee).filter_by(id="EMP008").first()
    assert retrieved.shift_id == shift.id


def test_employee_with_plant(db, test_org, test_dept, test_grade, test_designation):
    """Test employee assigned to a plant/location"""
    plant = DBHRPlant(
        id="PLANT001",
        name="Main Factory",
        location="Karachi",
        code="MF",
        organization_id=test_org.id
    )
    db.add(plant)
    db.commit()
    
    emp = DBEmployee(
        id="EMP009",
        name="Plant Employee",
        email="plant@test.com",
        department_id=test_dept.id,
        designation_id=test_designation.id,
        grade_id=test_grade.id,
        organization_id=test_org.id,
        plant_id=plant.id
    )
    db.add(emp)
    db.commit()
    
    retrieved = db.query(DBEmployee).filter_by(id="EMP009").first()
    assert retrieved.plant_id == plant.id
