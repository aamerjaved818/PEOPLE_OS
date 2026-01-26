"""
Tests for HCM models (Job Levels, Grades, Designations, Shifts).
"""
import pytest
from backend.domains.core.models import DBOrganization, DBDepartment
from backend.domains.hcm.models import (
    DBJobLevel, DBGrade, DBDesignation, DBShift, DBCandidate
)


@pytest.fixture
def test_org(db):
    """Create test organization"""
    org = DBOrganization(
        id="ORG_HCM",
        code="HCM_ORG",
        name="HCM Test Org",
        email="hcm@org.com",
        phone="123",
        description="Test"
    )
    db.add(org)
    db.commit()
    return org


def test_create_job_level(db, test_org):
    """Test creating a job level"""
    jl = DBJobLevel(
        id="JL001",
        name="Senior Management",
        code="SM",
        organization_id=test_org.id,
        is_active=True
    )
    db.add(jl)
    db.commit()
    
    retrieved = db.query(DBJobLevel).filter_by(id="JL001").first()
    assert retrieved.name == "Senior Management"


def test_job_level_unique_code(db, test_org):
    """Test that job level codes are unique"""
    jl1 = DBJobLevel(
        id="JL002",
        name="Middle Management",
        code="MM",
        organization_id=test_org.id
    )
    db.add(jl1)
    db.commit()
    
    jl2 = DBJobLevel(
        id="JL003",
        name="Another Middle",
        code="MM",  # Duplicate code
        organization_id=test_org.id
    )
    db.add(jl2)
    
    with pytest.raises(Exception):
        db.commit()


def test_create_grade(db, test_org):
    """Test creating a grade"""
    grade = DBGrade(
        id="GRADE001",
        name="Grade A",
        level=1,
        code="GA",
        organization_id=test_org.id,
        is_active=True
    )
    db.add(grade)
    db.commit()
    
    retrieved = db.query(DBGrade).filter_by(id="GRADE001").first()
    assert retrieved.name == "Grade A"
    assert retrieved.level == 1


def test_grade_with_job_level(db, test_org):
    """Test grade associated with job level"""
    jl = DBJobLevel(
        id="JL004",
        name="Executive",
        code="EX",
        organization_id=test_org.id
    )
    db.add(jl)
    db.commit()
    
    grade = DBGrade(
        id="GRADE002",
        name="Grade B",
        level=2,
        code="GB",
        job_level_id=jl.id,
        organization_id=test_org.id
    )
    db.add(grade)
    db.commit()
    
    retrieved = db.query(DBGrade).filter_by(id="GRADE002").first()
    assert retrieved.job_level_id == jl.id


def test_create_designation(db, test_org):
    """Test creating a designation"""
    grade = DBGrade(
        id="GRADE003",
        name="Grade C",
        level=3,
        code="GC",
        organization_id=test_org.id
    )
    db.add(grade)
    db.commit()
    
    des = DBDesignation(
        id="DES001",
        name="Software Engineer",
        code="SE",
        grade_id=grade.id,
        organization_id=test_org.id,
        is_active=True
    )
    db.add(des)
    db.commit()
    
    retrieved = db.query(DBDesignation).filter_by(id="DES001").first()
    assert retrieved.name == "Software Engineer"


def test_designation_with_department(db, test_org):
    """Test designation associated with department"""
    dept = DBDepartment(
        id="DEPT_HCM",
        code="HCM_D",
        name="HCM Department",
        organization_id=test_org.id
    )
    db.add(dept)
    db.commit()
    
    grade = DBGrade(
        id="GRADE004",
        name="Grade D",
        level=4,
        code="GD",
        organization_id=test_org.id
    )
    db.add(grade)
    db.commit()
    
    des = DBDesignation(
        id="DES002",
        name="HR Manager",
        code="HRM",
        grade_id=grade.id,
        department_id=dept.id,
        organization_id=test_org.id
    )
    db.add(des)
    db.commit()
    
    retrieved = db.query(DBDesignation).filter_by(id="DES002").first()
    assert retrieved.department_id == dept.id


def test_designation_unique_code(db, test_org):
    """Test that designation codes are unique"""
    grade = DBGrade(
        id="GRADE005",
        name="Grade E",
        level=5,
        code="GE",
        organization_id=test_org.id
    )
    db.add(grade)
    db.commit()
    
    des1 = DBDesignation(
        id="DES003",
        name="Designer 1",
        code="D1",
        grade_id=grade.id,
        organization_id=test_org.id
    )
    db.add(des1)
    db.commit()
    
    des2 = DBDesignation(
        id="DES004",
        name="Designer 2",
        code="D1",  # Duplicate
        grade_id=grade.id,
        organization_id=test_org.id
    )
    db.add(des2)
    
    with pytest.raises(Exception):
        db.commit()


def test_create_shift(db, test_org):
    """Test creating a shift"""
    shift = DBShift(
        id="SHIFT001",
        name="Morning",
        code="MRN",
        type="Fixed",
        start_time="08:00",
        end_time="16:00",
        grace_period=10,
        break_duration=60,
        work_days="Mon-Fri",
        organization_id=test_org.id,
        isActive=True
    )
    db.add(shift)
    db.commit()
    
    retrieved = db.query(DBShift).filter_by(id="SHIFT001").first()
    assert retrieved.name == "Morning"
    assert retrieved.start_time == "08:00"


def test_shift_unique_code(db, test_org):
    """Test that shift codes are unique"""
    shift1 = DBShift(
        id="SHIFT002",
        name="Evening",
        code="EVE",
        start_time="16:00",
        end_time="23:59",
        organization_id=test_org.id
    )
    db.add(shift1)
    db.commit()
    
    shift2 = DBShift(
        id="SHIFT003",
        name="Another Evening",
        code="EVE",  # Duplicate
        start_time="17:00",
        end_time="00:00",
        organization_id=test_org.id
    )
    db.add(shift2)
    
    with pytest.raises(Exception):
        db.commit()


def test_create_candidate(db, test_org):
    """Test creating a candidate"""
    cand = DBCandidate(
        id="CAND001",
        name="John Applicant",
        email="john@candidate.com",
        phone="1234567890",
        position_applied="Software Engineer",
        applied_date="2026-01-15",
        organization_id=test_org.id,
        current_stage="Interview",
        score=85
    )
    db.add(cand)
    db.commit()
    
    retrieved = db.query(DBCandidate).filter_by(id="CAND001").first()
    assert retrieved.name == "John Applicant"
    assert retrieved.position_applied == "Software Engineer"
