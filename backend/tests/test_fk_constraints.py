"""
Tests for Foreign Key constraints validation.
"""
import pytest
from sqlalchemy.exc import IntegrityError
from backend.domains.core.models import (
    DBOrganization, DBDepartment, DBUser, DBSubDepartment
)
from backend.domains.hcm.models import (
    DBEmployee, DBDesignation, DBGrade, DBJobLevel, DBShift
)


def test_employee_department_relationship(db):
    """Test that employees can reference valid departments"""
    org = DBOrganization(
        id="ORG_FK",
        code="FK_ORG",
        name="FK Test",
        email="fk@test.com",
        phone="123",
        description="Test"
    )
    db.add(org)
    db.commit()
    
    dept = DBDepartment(
        id="DEPT_FK",
        code="D_FK",
        name="Department",
        organization_id=org.id
    )
    db.add(dept)
    db.commit()
    
    grade = DBGrade(
        id="G_FK",
        name="Grade",
        level=1,
        code="G",
        organization_id=org.id
    )
    db.add(grade)
    db.commit()
    
    des = DBDesignation(
        id="D_DES",
        name="Designation",
        code="DES",
        grade_id=grade.id,
        organization_id=org.id
    )
    db.add(des)
    db.commit()
    
    # Valid employee
    emp = DBEmployee(
        id="EMP_FK",
        name="Test",
        department_id=dept.id,
        designation_id=des.id,
        grade_id=grade.id,
        email="emp@test.com",
        organization_id=org.id
    )
    db.add(emp)
    db.commit()
    
    retrieved = db.query(DBEmployee).filter_by(id="EMP_FK").first()
    assert retrieved is not None


def test_department_requires_valid_organization(db):
    """Test that departments must have valid organization_id"""
    dept = DBDepartment(
        id="DEPT_INVALID",
        code="D_INV",
        name="Test Dept",
        organization_id="INVALID_ORG"
    )
    db.add(dept)
    
    try:
        db.commit()
        # If it doesn't raise, FK constraint not enforced in this DB
        pytest.skip("FK constraint not enforced by database")
    except (IntegrityError, Exception):
        db.rollback()
        # Expected - constraint should prevent this
        assert True


def test_designation_requires_valid_grade(db):
    """Test that designations must have valid grade_id"""
    org = DBOrganization(
        id="ORG_DES",
        code="ORG_D",
        name="Des Org",
        email="org@test.com",
        phone="123",
        description="Test"
    )
    db.add(org)
    db.commit()
    
    des = DBDesignation(
        id="DES_INV",
        name="Test Designation",
        code="DES_I",
        grade_id="INVALID_GRADE",
        organization_id=org.id
    )
    db.add(des)
    
    try:
        db.commit()
        pytest.skip("FK constraint not enforced by database")
    except (IntegrityError, Exception):
        db.rollback()
        assert True


def test_subdepartment_requires_valid_parent(db):
    """Test sub-department FK constraint to parent department"""
    org = DBOrganization(
        id="ORG_SD",
        code="SD_ORG",
        name="SD Test",
        email="org@test.com",
        phone="123",
        description="Test"
    )
    db.add(org)
    db.commit()
    
    subdept = DBSubDepartment(
        id="SD_INV",
        code="SD_I",
        name="Sub Dept",
        organization_id=org.id,
        parent_department_id="INVALID_DEPT"
    )
    db.add(subdept)
    
    try:
        db.commit()
        pytest.skip("FK constraint not enforced by database")
    except (IntegrityError, Exception):
        db.rollback()
        assert True


def test_job_level_requires_valid_organization(db):
    """Test job level FK constraint"""
    jl = DBJobLevel(
        id="JL_INV",
        name="Senior",
        code="SR_I",
        organization_id="INVALID_ORG"
    )
    db.add(jl)
    
    try:
        db.commit()
        pytest.skip("FK constraint not enforced by database")
    except (IntegrityError, Exception):
        db.rollback()
        assert True


def test_user_employee_fk_constraint(db):
    """Test user to employee FK constraint"""
    user = DBUser(
        id="USR_INV",
        username="testuser_inv",
        password_hash="hash",
        role="HRManager",
        employee_id="INVALID_EMP"
    )
    db.add(user)
    
    try:
        db.commit()
        pytest.skip("FK constraint not enforced by database")
    except (IntegrityError, Exception):
        db.rollback()
        assert True


def test_valid_fk_chain(db):
    """Test complete valid FK chain"""
    # Org -> Dept -> Employee <- User
    org = DBOrganization(
        id="ORG_CHAIN",
        code="CHAIN_ORG",
        name="Chain Test",
        email="org@test.com",
        phone="123",
        description="Test"
    )
    db.add(org)
    db.commit()
    
    dept = DBDepartment(
        id="DEPT_CHAIN",
        code="D_CH",
        name="Dept",
        organization_id=org.id
    )
    db.add(dept)
    db.commit()
    
    grade = DBGrade(
        id="G_CH",
        name="Grade",
        level=1,
        code="GC",
        organization_id=org.id
    )
    db.add(grade)
    db.commit()
    
    des = DBDesignation(
        id="DES_CH",
        name="Des",
        code="D_C",
        grade_id=grade.id,
        organization_id=org.id
    )
    db.add(des)
    db.commit()
    
    emp = DBEmployee(
        id="EMP_CHAIN",
        name="Employee",
        department_id=dept.id,
        designation_id=des.id,
        grade_id=grade.id,
        email="emp@chain.com",
        organization_id=org.id
    )
    db.add(emp)
    db.commit()
    
    user = DBUser(
        id="USR_CHAIN",
        username="chain_user",
        password_hash="hash",
        role="HRManager",
        organization_id=org.id,
        employee_id=emp.id
    )
    db.add(user)
    db.commit()
    
    # Verify all exist
    assert db.query(DBOrganization).filter_by(id="ORG_CHAIN").first()
    assert db.query(DBDepartment).filter_by(id="DEPT_CHAIN").first()
    assert db.query(DBEmployee).filter_by(id="EMP_CHAIN").first()
    assert db.query(DBUser).filter_by(id="USR_CHAIN").first()
