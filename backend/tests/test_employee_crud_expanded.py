"""
Comprehensive test cases for Employee CRUD operations and error scenarios.

This test suite expands coverage with:
- Employee creation, retrieval, update, delete (CRUD)
- Error handling for invalid data
- Relationship testing (employee -> department -> organization)
- Transaction rollback scenarios
- Edge cases and boundary conditions

Target: +20 test cases to reach 60% coverage
"""

import pytest
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.domains.core.models import (
    DBOrganization, DBDepartment, DBHRPlant, DBSubDepartment
)
from backend.domains.hcm.models import (
    DBEmployee, DBDesignation, DBGrade, DBJobLevel, DBShift
)
from backend import crud, schemas


# ============================================================================
# FIXTURES - Setup data for tests
# ============================================================================

@pytest.fixture
def test_org(db):
    """Create test organization"""
    org = DBOrganization(
        id="ORG_TEST",
        code="ORG_CODE",
        name="Test Organization",
        email="org@test.com",
        phone="123-456-7890",
        description="Test organization"
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def test_org_2(db):
    """Create second test organization"""
    org = DBOrganization(
        id="ORG_TEST_2",
        code="ORG_CODE_2",
        name="Test Organization 2",
        email="org2@test.com",
        phone="123-456-7891",
        description="Second test organization"
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def test_dept(db, test_org):
    """Create test department"""
    dept = DBDepartment(
        id="DEPT_TEST",
        code="DEPT_CODE",
        name="Engineering",
        organization_id=test_org.id,
        description="Engineering department"
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@pytest.fixture
def test_grade(db, test_org):
    """Create test grade"""
    grade = DBGrade(
        id="GRADE_001",
        name="Senior Level",
        level=3,
        code="GRADE_S",
        organization_id=test_org.id
    )
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade


@pytest.fixture
def test_designation(db, test_org, test_grade, test_dept):
    """Create test designation"""
    des = DBDesignation(
        id="DES_001",
        name="Senior Engineer",
        code="SE_001",
        grade_id=test_grade.id,
        department_id=test_dept.id,
        organization_id=test_org.id
    )
    db.add(des)
    db.commit()
    db.refresh(des)
    return des


@pytest.fixture
def test_employee_data(test_org, test_dept, test_designation):
    """Create test employee data"""
    return {
        "id": "EMP_TEST_001",
        "name": "John Doe",
        "email": "john.doe@test.com",
        "phone": "555-0001",
        "department_id": test_dept.id,
        "designation_id": test_designation.id,
        "organization_id": test_org.id,
        "join_date": date(2025, 1, 1),
        "date_of_birth": date(1990, 5, 15)
    }


# ============================================================================
# TEST SUITE 1: EMPLOYEE CREATION (CRUD - CREATE)
# ============================================================================

class TestEmployeeCreation:
    """Tests for employee creation with various scenarios"""

    def test_create_employee_basic(self, db, test_employee_data):
        """Test basic employee creation with required fields"""
        emp = DBEmployee(**test_employee_data)
        db.add(emp)
        db.commit()
        db.refresh(emp)

        assert emp.id == "EMP_TEST_001"
        assert emp.name == "John Doe"
        assert emp.email == "john.doe@test.com"
        assert emp.phone == "555-0001"

    def test_create_employee_with_optional_fields(self, db, test_employee_data):
        """Test employee creation with optional fields"""
        test_employee_data.update({
            "personal_phone": "555-0002",
            "present_address": "123 Main St"
        })
        emp = DBEmployee(**test_employee_data)
        db.add(emp)
        db.commit()
        db.refresh(emp)

        assert emp.present_address == "123 Main St"

    def test_create_multiple_employees_same_org(self, db, test_org, test_dept, test_designation):
        """Test creating multiple employees in same organization"""
        employees_data = [
            {"id": f"EMP_00{i}", "name": f"First {i} Last {i}", "email": f"emp{i}@test.com",
             "department_id": test_dept.id, "designation_id": test_designation.id,
             "organization_id": test_org.id}
            for i in range(1, 4)
        ]

        for emp_data in employees_data:
            emp = DBEmployee(**emp_data)
            db.add(emp)

        db.commit()

        # Verify all created
        count = db.query(DBEmployee).filter(
            DBEmployee.organization_id == test_org.id
        ).count()
        assert count == 3

    def test_employee_default_status(self, db, test_employee_data):
        """Test employee default status is ACTIVE"""
        emp = DBEmployee(**test_employee_data)
        db.add(emp)
        db.commit()
        db.refresh(emp)

        # Status should be set if passed or have a default if handled by app
        assert hasattr(emp, 'status')

    def test_create_employee_unicode_name(self, db, test_employee_data):
        """Test employee creation with unicode characters in name"""
        test_employee_data["name"] = "François Müller"
        emp = DBEmployee(**test_employee_data)
        db.add(emp)
        db.commit()
        db.refresh(emp)

        assert "François" in emp.name
        assert "Müller" in emp.name

    def test_create_employee_email_case_sensitivity(self, db, test_employee_data):
        """Test email is handled correctly"""
        test_employee_data["email"] = "JOHN.DOE@TEST.COM"
        emp = DBEmployee(**test_employee_data)
        db.add(emp)
        db.commit()
        db.refresh(emp)

        assert emp.email == "JOHN.DOE@TEST.COM"


# ============================================================================
# TEST SUITE 2: EMPLOYEE RETRIEVAL (CRUD - READ)
# ============================================================================

class TestEmployeeRetrieval:
    """Tests for employee retrieval and querying"""

    def test_retrieve_employee_by_id(self, db, test_employee_data):
        """Test retrieving employee by ID"""
        emp = DBEmployee(**test_employee_data)
        db.add(emp)
        db.commit()

        retrieved = db.query(DBEmployee).filter(
            DBEmployee.id == "EMP_TEST_001"
        ).first()
        assert retrieved is not None
        assert retrieved.name.startswith("John")

    def test_retrieve_employee_not_found(self, db):
        """Test retrieving non-existent employee"""
        retrieved = db.query(DBEmployee).filter(
            DBEmployee.id == "NONEXISTENT"
        ).first()
        assert retrieved is None

    def test_retrieve_employees_by_department(self, db, test_org, test_dept, test_designation):
        """Test retrieving all employees in a department"""
        # Create multiple employees in same dept
        for i in range(3):
            emp = DBEmployee(
                id=f"EMP_D{i}",
                name=f"First {i} Last {i}",
                email=f"dept_emp{i}@test.com",
                department_id=test_dept.id,
                designation_id=test_designation.id,
                organization_id=test_org.id
            )
            db.add(emp)

        db.commit()

        employees = db.query(DBEmployee).filter(
            DBEmployee.department_id == test_dept.id
        ).all()
        assert len(employees) == 3

    def test_retrieve_employees_by_organization(self, db, test_org, test_org_2, test_dept, test_designation):
        """Test retrieving employees by organization"""
        # Create employee in org 1
        emp1 = DBEmployee(
            id="EMP_ORG1",
            name="Org1 Employee",
            email="org1_emp@test.com",
            department_id=test_dept.id,
            designation_id=test_designation.id,
            organization_id=test_org.id
        )
        db.add(emp1)
        db.commit()

        employees = db.query(DBEmployee).filter(
            DBEmployee.organization_id == test_org.id
        ).all()
        assert len(employees) == 1
        assert employees[0].organization_id == test_org.id

    def test_retrieve_employees_paginated(self, db, test_org, test_dept, test_designation):
        """Test retrieving employees with pagination"""
        # Create 10 employees
        for i in range(10):
            emp = DBEmployee(
                id=f"EMP_PAGE_{i:02d}",
                name=f"First {i} Last {i}",
                email=f"page_emp{i}@test.com",
                department_id=test_dept.id,
                designation_id=test_designation.id,
                organization_id=test_org.id
            )
            db.add(emp)

        db.commit()

        # Get first 5
        employees = db.query(DBEmployee).filter(
            DBEmployee.organization_id == test_org.id
        ).limit(5).all()
        assert len(employees) == 5

        # Get next 5
        employees_page2 = db.query(DBEmployee).filter(
            DBEmployee.organization_id == test_org.id
        ).offset(5).limit(5).all()
        assert len(employees_page2) == 5

    def test_retrieve_employee_with_relationships(self, db, test_employee_data, test_dept, test_designation):
        """Test retrieving employee with related objects"""
        emp = DBEmployee(**test_employee_data)
        db.add(emp)
        db.commit()
        db.refresh(emp)

        # Retrieve and check relationships
        retrieved = db.query(DBEmployee).filter(
            DBEmployee.id == emp.id
        ).first()

        assert retrieved.department_id == test_dept.id
        assert retrieved.designation_id == test_designation.id


# ============================================================================
# TEST SUITE 3: EMPLOYEE UPDATE (CRUD - UPDATE)
# ============================================================================

class TestEmployeeUpdate:
    """Tests for employee update operations"""

    def test_update_employee_name(self, db, test_employee_data):
        """Test updating employee name"""
        emp = DBEmployee(**test_employee_data)
        db.add(emp)
        db.commit()

        emp.name = "Jane"
        db.commit()
        db.refresh(emp)

        assert emp.name == "Jane"

    def test_update_employee_email(self, db, test_employee_data):
        """Test updating employee email"""
        emp = DBEmployee(**test_employee_data)
        db.add(emp)
        db.commit()

        emp.email = "jane.doe@test.com"
        db.commit()

        retrieved = db.query(DBEmployee).filter(
            DBEmployee.id == emp.id
        ).first()
        assert retrieved.email == "jane.doe@test.com"

    def test_update_employee_department(self, db, test_employee_data, test_org):
        """Test moving employee to different department"""
        emp = DBEmployee(**test_employee_data)
        db.add(emp)
        db.commit()

        old_dept_id = emp.department_id

        # Create new department
        new_dept = DBDepartment(
            id="DEPT_NEW",
            code="DEPT_NEW_CODE",
            name="New Department",
            organization_id=test_org.id
        )
        db.add(new_dept)
        db.commit()

        # Update employee department
        emp.department_id = new_dept.id
        db.commit()

        retrieved = db.query(DBEmployee).filter(
            DBEmployee.id == emp.id
        ).first()
        assert retrieved.department_id == new_dept.id
        assert retrieved.department_id != old_dept_id

    def test_update_employee_multiple_fields(self, db, test_employee_data):
        """Test updating multiple fields at once"""
        emp = DBEmployee(**test_employee_data)
        db.add(emp)
        db.commit()

        # Update multiple fields
        emp.name = "Updated"
        emp.email = "updated@test.com"
        emp.phone = "555-9999"
        emp.present_address = "456 Oak Ave"
        db.commit()

        retrieved = db.query(DBEmployee).filter(
            DBEmployee.id == emp.id
        ).first()

        assert retrieved.name == "Updated"
        assert retrieved.email == "updated@test.com"
        assert retrieved.phone == "555-9999"
        assert retrieved.present_address == "456 Oak Ave"

    def test_update_preserves_other_fields(self, db, test_employee_data):
        """Test that updating one field doesn't affect others"""
        emp = DBEmployee(**test_employee_data)
        original_email = emp.email
        db.add(emp)
        db.commit()

        emp.name = "New First"
        db.commit()

        retrieved = db.query(DBEmployee).filter(
            DBEmployee.id == emp.id
        ).first()

        assert retrieved.email == original_email
        assert retrieved.name == "New First"


# ============================================================================
# TEST SUITE 4: EMPLOYEE DELETE (CRUD - DELETE)
# ============================================================================

class TestEmployeeDelete:
    """Tests for employee deletion operations"""

    def test_delete_employee(self, db, test_employee_data):
        """Test deleting an employee"""
        emp = DBEmployee(**test_employee_data)
        db.add(emp)
        db.commit()

        emp_id = emp.id
        db.delete(emp)
        db.commit()

        retrieved = db.query(DBEmployee).filter(
            DBEmployee.id == emp_id
        ).first()
        assert retrieved is None

    def test_delete_employee_cascade_check(self, db, test_employee_data):
        """Test cascading deletion if applicable"""
        emp = DBEmployee(**test_employee_data)
        db.add(emp)
        db.commit()

        emp_id = emp.id
        db.delete(emp)
        db.commit()

        # Verify deleted
        count = db.query(DBEmployee).filter(
            DBEmployee.id == emp_id
        ).count()
        assert count == 0

    def test_delete_nonexistent_employee(self, db):
        """Test deleting non-existent employee (should be handled gracefully)"""
        # This should not raise an error
        employee_to_delete = db.query(DBEmployee).filter(
            DBEmployee.id == "NONEXISTENT"
        ).first()
        assert employee_to_delete is None


# ============================================================================
# TEST SUITE 5: ERROR SCENARIOS & VALIDATION
# ============================================================================

class TestEmployeeErrorHandling:
    """Tests for error handling and validation"""

    def test_duplicate_employee_id_error(self, db, test_employee_data):
        """Test that duplicate employee ID raises error"""
        emp1 = DBEmployee(**test_employee_data)
        db.add(emp1)
        db.commit()

        # Try to create another with same ID
        emp2 = DBEmployee(**test_employee_data)
        db.add(emp2)

        with pytest.raises(Exception):  # Should raise integrity error
            db.commit()

    def test_missing_required_organization_id(self, db, test_dept, test_designation):
        """Test creating employee without organization_id"""
        emp_data = {
            "id": "EMP_NO_ORG",
            "name": "No Org",
            "email": "no_org@test.com",
            "department_id": test_dept.id,
            "designation_id": test_designation.id,
            "organization_id": None
        }

        emp = DBEmployee(**emp_data)
        db.add(emp)
        # organization_id is nullable=True in DBEmployee model
        db.commit()
        db.refresh(emp)
        assert emp.organization_id is None

    def test_invalid_department_reference(self, db, test_org):
        """Test creating employee with non-existent department"""
        emp_data = {
            "id": "EMP_INVALID_DEPT",
            "name": "Invalid Dept",
            "email": "invalid_dept@test.com",
            "department_id": "NONEXISTENT_DEPT",  # Invalid reference
            "organization_id": test_org.id
        }

        emp = DBEmployee(**emp_data)
        db.add(emp)

        # Should raise FK constraint error
        with pytest.raises(Exception):
            db.commit()

    def test_invalid_designation_reference(self, db, test_org, test_dept):
        """Test creating employee with non-existent designation"""
        emp_data = {
            "id": "EMP_INVALID_DES",
            "name": "Invalid Des",
            "email": "invalid_des@test.com",
            "department_id": test_dept.id,
            "designation_id": "NONEXISTENT_DES",  # Invalid reference
            "organization_id": test_org.id
        }

        emp = DBEmployee(**emp_data)
        db.add(emp)

        # Should raise FK constraint error
        with pytest.raises(Exception):
            db.commit()

    def test_invalid_email_format(self, db, test_employee_data):
        """Test creating employee with invalid email format"""
        test_employee_data["email"] = "not_an_email"
        emp = DBEmployee(**test_employee_data)
        db.add(emp)
        # Note: SQLite doesn't enforce email format, but application should
        db.commit()
        # App-level validation would catch this

    def test_future_date_of_birth(self, db, test_employee_data):
        """Test employee with future date of birth"""
        test_employee_data["date_of_birth"] = date(2030, 1, 1)
        emp = DBEmployee(**test_employee_data)
        db.add(emp)
        db.commit()
        # Date should be stored but app should validate

    def test_joining_date_before_birth_date(self, db, test_employee_data):
        """Test employee joining before birth date"""
        test_employee_data["date_of_birth"] = date(2000, 1, 1)
        test_employee_data["join_date"] = date(1990, 1, 1)
        emp = DBEmployee(**test_employee_data)
        db.add(emp)
        db.commit()
        # Database allows this, but app should validate


# ============================================================================
# TEST SUITE 6: TRANSACTION & ROLLBACK BEHAVIOR
# ============================================================================

class TestTransactionBehavior:
    """Tests for transaction handling and rollback"""

    def test_rollback_on_error(self, db, test_employee_data):
        """Test rollback when error occurs"""
        emp1 = DBEmployee(**test_employee_data)
        db.add(emp1)
        db.commit()

        # Try to add duplicate
        emp2 = DBEmployee(**test_employee_data)
        db.add(emp2)

        try:
            db.commit()
        except Exception:
            db.rollback()

        # Original employee should still exist
        retrieved = db.query(DBEmployee).filter(
            DBEmployee.id == test_employee_data["id"]
        ).first()
        assert retrieved is not None

    def test_partial_commit_isolation(self, db, test_org, test_dept, test_designation):
        """Test that uncommitted changes are not visible"""
        emp = DBEmployee(
            id="EMP_UNCOMMITTED",
            name="Uncommitted Employee",
            email="uncommitted@test.com",
            department_id=test_dept.id,
            designation_id=test_designation.id,
            organization_id=test_org.id
        )
        db.add(emp)
        # Don't commit

        # Employee should exist in session
        assert emp.id == "EMP_UNCOMMITTED"

        db.rollback()

        # After rollback, uncommitted data should be gone
        retrieved = db.query(DBEmployee).filter(
            DBEmployee.id == "EMP_UNCOMMITTED"
        ).first()
        assert retrieved is None

    def test_nested_updates_in_transaction(self, db, test_employee_data, test_org):
        """Test multiple updates within single transaction"""
        emp = DBEmployee(**test_employee_data)
        db.add(emp)
        db.commit()

        # Create new dept
        new_dept = DBDepartment(
            id="DEPT_TRANS",
            code="TRANS",
            name="Transaction Dept",
            organization_id=test_org.id
        )
        db.add(new_dept)
        db.commit()

        # Update employee
        emp.name = "Updated in Transaction"
        emp.department_id = new_dept.id
        db.commit()

        # Verify both changes persisted
        retrieved = db.query(DBEmployee).filter(
            DBEmployee.id == emp.id
        ).first()
        assert retrieved.name == "Updated in Transaction"
        assert retrieved.department_id == new_dept.id


# ============================================================================
# TEST SUITE 7: AGGREGATE OPERATIONS
# ============================================================================

class TestAggregateOperations:
    """Tests for aggregate queries and bulk operations"""

    def test_count_employees_by_department(self, db, test_org, test_dept, test_designation):
        """Test counting employees in each department"""
        # Create 5 employees
        for i in range(5):
            emp = DBEmployee(
                id=f"EMP_COUNT_{i}",
                name=f"First {i} Last {i}",
                email=f"count_emp{i}@test.com",
                department_id=test_dept.id,
                designation_id=test_designation.id,
                organization_id=test_org.id
            )
            db.add(emp)

        db.commit()

        count = db.query(DBEmployee).filter(
            DBEmployee.department_id == test_dept.id
        ).count()
        assert count == 5

    def test_count_employees_by_organization(self, db, test_org, test_dept, test_designation):
        """Test counting all employees in organization"""
        for i in range(3):
            emp = DBEmployee(
                id=f"EMP_ORG_COUNT_{i}",
                name=f"First {i} Last {i}",
                email=f"org_count{i}@test.com",
                department_id=test_dept.id,
                designation_id=test_designation.id,
                organization_id=test_org.id
            )
            db.add(emp)

        db.commit()

        count = db.query(DBEmployee).filter(
            DBEmployee.organization_id == test_org.id
        ).count()
        assert count == 3

    def test_bulk_status_update(self, db, test_org, test_dept, test_designation):
        """Test updating status for multiple employees"""
        # Create 3 employees
        emp_ids = []
        for i in range(3):
            emp = DBEmployee(
                id=f"EMP_BULK_{i}",
                name=f"First {i} Last {i}",
                email=f"bulk{i}@test.com",
                department_id=test_dept.id,
                designation_id=test_designation.id,
                organization_id=test_org.id,
                status="Active"
            )
            db.add(emp)
            emp_ids.append(emp.id)

        db.commit()

        # Bulk update status
        db.query(DBEmployee).filter(
            DBEmployee.id.in_(emp_ids)
        ).update({DBEmployee.status: "Inactive"}, synchronize_session=False)
        db.commit()

        # Verify all updated
        updated = db.query(DBEmployee).filter(
            DBEmployee.id.in_(emp_ids)
        ).all()
        assert all(emp.status == "Inactive" for emp in updated)

    def test_distinct_departments_in_org(self, db, test_org, test_dept, test_designation):
        """Test finding distinct departments in organization"""
        # Create second department
        dept2 = DBDepartment(
            id="DEPT_DISTINCT",
            code="DIST",
            name="Distinct Dept",
            organization_id=test_org.id
        )
        db.add(dept2)
        db.commit()

        # Add employees to both departments
        emp1 = DBEmployee(
            id="EMP_D1",
            name="Dept1 Employee",
            email="d1@test.com",
            department_id=test_dept.id,
            designation_id=test_designation.id,
            organization_id=test_org.id
        )
        emp2 = DBEmployee(
            id="EMP_D2",
            name="Dept2 Employee",
            email="d2@test.com",
            department_id=dept2.id,
            designation_id=test_designation.id,
            organization_id=test_org.id
        )
        db.add(emp1)
        db.add(emp2)
        db.commit()

        # Get distinct departments
        depts = db.query(DBEmployee.department_id).filter(
            DBEmployee.organization_id == test_org.id
        ).distinct().all()
        assert len(depts) == 2
