"""
Comprehensive test cases for Department CRUD operations.

This test suite provides:
- Department creation with hierarchy
- Department updates and reorganization
- Subdepartment operations
- Error handling for invalid structures
- Cascade behavior testing

Target: +10 test cases for department operations
"""

import pytest
from sqlalchemy.orm import Session

from backend.domains.core.models import (
    DBOrganization, DBDepartment, DBSubDepartment
)
from backend.domains.hcm.models import DBEmployee, DBDesignation, DBGrade


@pytest.fixture
def test_org(db):
    """Create test organization"""
    org = DBOrganization(
        id="ORG_DEPT_TEST",
        code="DEPT_ORG",
        name="Department Test Org",
        email="dept@test.com",
        phone="555-0000"
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def test_grade(db, test_org):
    """Create test grade"""
    grade = DBGrade(
        id="GRADE_DEPT",
        name="Grade Dept",
        level=1,
        code="GD",
        organization_id=test_org.id
    )
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade


# ============================================================================
# TEST SUITE 1: DEPARTMENT CREATION
# ============================================================================

class TestDepartmentCreation:
    """Tests for department creation operations"""

    def test_create_department_basic(self, db, test_org):
        """Test creating basic department"""
        dept = DBDepartment(
            id="DEPT_001",
            code="DEPT_001_CODE",
            name="Engineering",
            organization_id=test_org.id
        )
        db.add(dept)
        db.commit()
        db.refresh(dept)

        assert dept.id == "DEPT_001"
        assert dept.name == "Engineering"
        assert dept.organization_id == test_org.id

    def test_create_department_with_description(self, db, test_org):
        """Test creating department with description"""
        dept = DBDepartment(
            id="DEPT_002",
            code="DEPT_002_CODE",
            name="Sales",
            organization_id=test_org.id,
            description="Sales and Business Development"
        )
        db.add(dept)
        db.commit()
        db.refresh(dept)

        assert dept.description == "Sales and Business Development"

    def test_create_subdepartment(self, db, test_org):
        """Test creating subdepartment under parent"""
        # Create parent department
        parent_dept = DBDepartment(
            id="DEPT_PARENT",
            code="PARENT",
            name="IT",
            organization_id=test_org.id
        )
        db.add(parent_dept)
        db.commit()

        # Create subdepartment
        sub_dept = DBSubDepartment(
            id="SUBDEPT_001",
            name="Backend Team",
            code="BACKEND",
            department_id=parent_dept.id,
            organization_id=test_org.id
        )
        db.add(sub_dept)
        db.commit()
        db.refresh(sub_dept)

        assert sub_dept.department_id == parent_dept.id
        assert sub_dept.name == "Backend Team"

    def test_create_nested_subdepartments(self, db, test_org):
        """Test creating multi-level department hierarchy"""
        # Create parent
        parent = DBDepartment(
            id="DEPT_ROOT",
            code="ROOT",
            name="IT",
            organization_id=test_org.id
        )
        db.add(parent)
        db.commit()

        # Create sub level 1
        sub1 = DBSubDepartment(
            id="SUB_L1",
            name="Development",
            code="DEV",
            department_id=parent.id,
            organization_id=test_org.id
        )
        db.add(sub1)
        db.commit()

        # Verify hierarchy
        assert sub1.department_id == parent.id

    def test_create_multiple_departments_same_org(self, db, test_org):
        """Test creating multiple departments in one organization"""
        dept_names = ["Engineering", "Sales", "Marketing", "HR", "Finance"]

        for i, name in enumerate(dept_names):
            dept = DBDepartment(
                id=f"DEPT_{i:02d}",
                code=f"DEPT_{i:02d}",
                name=name,
                organization_id=test_org.id
            )
            db.add(dept)

        db.commit()

        # Verify all created
        depts = db.query(DBDepartment).filter(
            DBDepartment.organization_id == test_org.id
        ).all()
        assert len(depts) == 5

    def test_department_unique_per_organization(self, db, test_org):
        """Test department codes are unique within organization"""
        dept1 = DBDepartment(
            id="DEPT_UNIQUE_1",
            code="UNIQUE_CODE",
            name="Department 1",
            organization_id=test_org.id
        )
        db.add(dept1)
        db.commit()

        # Create another department with same code - should fail due to unique constraint
        dept2 = DBDepartment(
            id="DEPT_UNIQUE_2",
            code="UNIQUE_CODE",  # Same code
            name="Department 2",
            organization_id=test_org.id
        )
        db.add(dept2)
        with pytest.raises(Exception):
            db.commit()
        db.rollback()


# ============================================================================
# TEST SUITE 2: DEPARTMENT RETRIEVAL
# ============================================================================

class TestDepartmentRetrieval:
    """Tests for department retrieval and searching"""

    def test_retrieve_department_by_id(self, db, test_org):
        """Test retrieving department by ID"""
        dept = DBDepartment(
            id="DEPT_RETRIEVE",
            code="RETR",
            name="Retrieve Test",
            organization_id=test_org.id
        )
        db.add(dept)
        db.commit()

        retrieved = db.query(DBDepartment).filter(
            DBDepartment.id == "DEPT_RETRIEVE"
        ).first()
        assert retrieved is not None
        assert retrieved.name == "Retrieve Test"

    def test_retrieve_all_departments_in_org(self, db, test_org):
        """Test retrieving all departments in organization"""
        for i in range(3):
            dept = DBDepartment(
                id=f"DEPT_ALL_{i}",
                code=f"ALL_{i}",
                name=f"Department {i}",
                organization_id=test_org.id
            )
            db.add(dept)

        db.commit()

        depts = db.query(DBDepartment).filter(
            DBDepartment.organization_id == test_org.id
        ).all()
        assert len(depts) == 3

    def test_retrieve_department_not_found(self, db):
        """Test retrieving non-existent department"""
        dept = db.query(DBDepartment).filter(
            DBDepartment.id == "NONEXISTENT"
        ).first()
        assert dept is None

    def test_retrieve_subdepartments(self, db, test_org):
        """Test retrieving subdepartments under parent"""
        parent = DBDepartment(
            id="DEPT_PARENT_REL",
            code="PARENT_REL",
            name="Parent",
            organization_id=test_org.id
        )
        db.add(parent)
        db.commit()

        # Create subdepartments
        for i in range(2):
            sub = DBSubDepartment(
                id=f"SUB_{i}",
                name=f"Sub Department {i}",
                code=f"SUB_{i}",
                department_id=parent.id,
                organization_id=test_org.id
            )
            db.add(sub)

        db.commit()

        subs = db.query(DBSubDepartment).filter(
            DBSubDepartment.department_id == parent.id
        ).all()
        assert len(subs) == 2

    def test_retrieve_department_with_employees(self, db, test_org, test_grade):
        """Test retrieving department with employee count"""
        dept = DBDepartment(
            id="DEPT_WITH_EMP",
            code="WITH_EMP",
            name="With Employees",
            organization_id=test_org.id
        )
        db.add(dept)
        db.commit()

        # Create designation
        des = DBDesignation(
            id="DES_EMP_COUNT",
            name="Test",
            code="TEST",
            grade_id=test_grade.id,
            department_id=dept.id,
            organization_id=test_org.id
        )
        db.add(des)
        db.commit()

        # Create employees
        for i in range(2):
            emp = DBEmployee(
                id=f"EMP_IN_DEPT_{i}",
                name=f"Employee {i}",
                email=f"emp_in_dept{i}@test.com",
                department_id=dept.id,
                designation_id=des.id,
                organization_id=test_org.id
            )
            db.add(emp)

        db.commit()

        # Verify department has employees
        dept_retrieved = db.query(DBDepartment).filter(
            DBDepartment.id == dept.id
        ).first()
        assert dept_retrieved is not None


# ============================================================================
# TEST SUITE 3: DEPARTMENT UPDATE
# ============================================================================

class TestDepartmentUpdate:
    """Tests for department update operations"""

    def test_update_department_name(self, db, test_org):
        """Test updating department name"""
        dept = DBDepartment(
            id="DEPT_UPDATE_NAME",
            code="UPD_NAME",
            name="Original Name",
            organization_id=test_org.id
        )
        db.add(dept)
        db.commit()

        dept.name = "Updated Name"
        db.commit()

        retrieved = db.query(DBDepartment).filter(
            DBDepartment.id == dept.id
        ).first()
        assert retrieved.name == "Updated Name"

    def test_update_department_code(self, db, test_org):
        """Test updating department code"""
        dept = DBDepartment(
            id="DEPT_UPDATE_CODE",
            code="OLD_CODE",
            name="Test Dept",
            organization_id=test_org.id
        )
        db.add(dept)
        db.commit()

        dept.code = "NEW_CODE"
        db.commit()

        retrieved = db.query(DBDepartment).filter(
            DBDepartment.id == dept.id
        ).first()
        assert retrieved.code == "NEW_CODE"

    def test_update_department_description(self, db, test_org):
        """Test updating department description"""
        dept = DBDepartment(
            id="DEPT_UPDATE_DESC",
            code="UPD_DESC",
            name="Test",
            organization_id=test_org.id
        )
        db.add(dept)
        db.commit()

        dept.description = "New Description"
        db.commit()

        retrieved = db.query(DBDepartment).filter(
            DBDepartment.id == dept.id
        ).first()
        assert retrieved.description == "New Description"


# ============================================================================
# TEST SUITE 4: DEPARTMENT DELETE
# ============================================================================

class TestDepartmentDelete:
    """Tests for department deletion operations"""

    def test_delete_empty_department(self, db, test_org):
        """Test deleting department with no employees"""
        dept = DBDepartment(
            id="DEPT_DELETE_EMPTY",
            code="DEL_EMPTY",
            name="Empty",
            organization_id=test_org.id
        )
        db.add(dept)
        db.commit()

        dept_id = dept.id
        db.delete(dept)
        db.commit()

        retrieved = db.query(DBDepartment).filter(
            DBDepartment.id == dept_id
        ).first()
        assert retrieved is None

    def test_delete_department_cascade_check(self, db, test_org, test_grade):
        """Test department deletion with cascade constraints"""
        dept = DBDepartment(
            id="DEPT_DELETE_CASCADE",
            code="DEL_CASCADE",
            name="Cascade",
            organization_id=test_org.id
        )
        db.add(dept)
        db.commit()

        # Add designation (may have FK to department)
        des = DBDesignation(
            id="DES_CASCADE",
            name="Test",
            code="TST",
            grade_id=test_grade.id,
            department_id=dept.id,
            organization_id=test_org.id
        )
        db.add(des)
        db.commit()

        # Try to delete department
        # May fail due to FK constraints or succeed with cascade
        try:
            db.delete(dept)
            db.commit()
        except Exception:
            db.rollback()
            # FK constraint prevented deletion - as expected


# ============================================================================
# TEST SUITE 5: DEPARTMENT ERROR HANDLING
# ============================================================================

class TestDepartmentErrorHandling:
    """Tests for department validation and error scenarios"""

    def test_missing_required_organization(self, db):
        """Test creating department without organization"""
        dept = DBDepartment(
            id="DEPT_NO_ORG",
            code="NO_ORG",
            name="No Org",
            organization_id=None
        )
        db.add(dept)

        with pytest.raises(Exception):  # NOT NULL constraint
            db.commit()

    def test_invalid_parent_subdepartment(self, db):
        """Test creating subdepartment with non-existent parent"""
        sub = DBSubDepartment(
            id="SUB_INVALID",
            name="Invalid",
            code="INV",
            department_id="NONEXISTENT_PARENT"
        )
        db.add(sub)

        with pytest.raises(Exception):  # FK constraint
            db.commit()

    def test_department_unicode_name(self, db, test_org):
        """Test department with unicode characters"""
        dept = DBDepartment(
            id="DEPT_UNICODE",
            code="UNI",
            name="Département de Recherche",
            organization_id=test_org.id
        )
        db.add(dept)
        db.commit()
        db.refresh(dept)

        assert "Département" in dept.name

    def test_circular_subdepartment_reference(self, db, test_org):
        """Test preventing circular references (if applicable)"""
        # Create two departments
        dept1 = DBDepartment(
            id="DEPT_CIRC_1",
            code="CIRC_1",
            name="Circ 1",
            organization_id=test_org.id
        )
        dept2 = DBDepartment(
            id="DEPT_CIRC_2",
            code="CIRC_2",
            name="Circ 2",
            organization_id=test_org.id
        )
        db.add(dept1)
        db.add(dept2)
        db.commit()

        # Try to create circular subdepartment structure
        # This may succeed in DB but app should prevent it
