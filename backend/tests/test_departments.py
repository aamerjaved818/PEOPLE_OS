"""
Tests for Department model and relationships.
"""
import pytest
from backend.domains.core.models import DBOrganization, DBDepartment, DBSubDepartment, DBUser


@pytest.fixture
def test_org(db):
    """Create test organization"""
    org = DBOrganization(
        id="ORG_TEST",
        code="TEST_ORG",
        name="Test Organization",
        email="test@org.com",
        phone="123",
        description="Test"
    )
    db.add(org)
    db.commit()
    return org


def test_create_department(db, test_org):
    """Test creating a department"""
    dept = DBDepartment(
        id="DEPT001",
        code="DEPT001",
        name="Human Resources",
        organization_id=test_org.id,
        isActive=True
    )
    db.add(dept)
    db.commit()
    
    retrieved = db.query(DBDepartment).filter_by(id="DEPT001").first()
    assert retrieved.name == "Human Resources"
    assert retrieved.code == "DEPT001"


def test_department_unique_code(db, test_org):
    """Test that department codes must be unique"""
    dept1 = DBDepartment(
        id="DEPT002",
        code="FINANCE",
        name="Finance",
        organization_id=test_org.id
    )
    db.add(dept1)
    db.commit()
    
    # Attempt duplicate code
    dept2 = DBDepartment(
        id="DEPT003",
        code="FINANCE",
        name="Finance 2",
        organization_id=test_org.id
    )
    db.add(dept2)
    
    with pytest.raises(Exception):
        db.commit()


def test_department_with_hod_manager(db, test_org):
    """Test department with head of department and manager"""
    user1 = DBUser(
        id="USR_HOD",
        username="hod_user",
        password_hash="hash",
        role="HRExecutive"
    )
    user2 = DBUser(
        id="USR_MGR",
        username="mgr_user",
        password_hash="hash",
        role="HRManager"
    )
    db.add(user1)
    db.add(user2)
    db.commit()
    
    dept = DBDepartment(
        id="DEPT004",
        code="QUALITY",
        name="Quality",
        organization_id=test_org.id,
        hod_id=user1.id,
        manager_id=user2.id
    )
    db.add(dept)
    db.commit()
    
    retrieved = db.query(DBDepartment).filter_by(id="DEPT004").first()
    assert retrieved.hod_id == user1.id
    assert retrieved.manager_id == user2.id


def test_subdepartment_relationship(db, test_org):
    """Test sub-department creation and relationship"""
    parent_dept = DBDepartment(
        id="DEPT_PARENT",
        code="PARENT",
        name="Engineering",
        organization_id=test_org.id
    )
    db.add(parent_dept)
    db.commit()
    
    subdept = DBSubDepartment(
        id="SUBDEPT001",
        code="BACKEND",
        name="Backend Team",
        organization_id=test_org.id,
        parent_department_id=parent_dept.id
    )
    db.add(subdept)
    db.commit()
    
    retrieved = db.query(DBSubDepartment).filter_by(id="SUBDEPT001").first()
    assert retrieved.parent_department_id == parent_dept.id


def test_subdepartment_unique_code(db, test_org):
    """Test that sub-department codes are unique"""
    parent = DBDepartment(
        id="DEPT_P2",
        code="PARENT2",
        name="Parent",
        organization_id=test_org.id
    )
    db.add(parent)
    db.commit()
    
    subdept1 = DBSubDepartment(
        id="SD001",
        code="TEAM1",
        name="Team 1",
        organization_id=test_org.id,
        parent_department_id=parent.id
    )
    db.add(subdept1)
    db.commit()
    
    subdept2 = DBSubDepartment(
        id="SD002",
        code="TEAM1",  # Duplicate
        name="Team 2",
        organization_id=test_org.id,
        parent_department_id=parent.id
    )
    db.add(subdept2)
    
    with pytest.raises(Exception):
        db.commit()
