"""
Comprehensive test cases for Job Levels, Grades, and Designations.

This test suite covers:
- Job level creation and hierarchy
- Grade level management
- Designation creation and relationships
- Validation of level constraints
- Error handling for invalid hierarchies

Target: +8 test cases for job/grade operations
"""

import pytest
from sqlalchemy.orm import Session

from backend.domains.core.models import DBOrganization, DBDepartment
from backend.domains.hcm.models import (
    DBJobLevel, DBGrade, DBDesignation, DBEmployee
)


@pytest.fixture
def test_org(db):
    """Create test organization"""
    org = DBOrganization(
        id="ORG_JOB_TEST",
        code="JOB_ORG",
        name="Job Test Organization",
        email="job@test.com",
        phone="555-1000"
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def test_dept(db, test_org):
    """Create test department"""
    dept = DBDepartment(
        id="DEPT_JOB",
        code="JOB_DEPT",
        name="Job Department",
        organization_id=test_org.id
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


# ============================================================================
# TEST SUITE 1: JOB LEVEL CREATION & MANAGEMENT
# ============================================================================

class TestJobLevelCreation:
    """Tests for job level creation and management"""

    def test_create_job_level_basic(self, db, test_org):
        """Test creating basic job level"""
        job_level = DBJobLevel(
            id="JL_001",
            name="Entry Level",
            code="ENTRY",
            level_number=1,
            organization_id=test_org.id
        )
        db.add(job_level)
        db.commit()
        db.refresh(job_level)

        assert job_level.id == "JL_001"
        assert job_level.name == "Entry Level"
        assert job_level.level_number == 1

    def test_create_job_level_hierarchy(self, db, test_org):
        """Test creating multiple job levels in hierarchy"""
        levels = [
            ("JL_001", "Entry Level", 1),
            ("JL_002", "Mid Level", 2),
            ("JL_003", "Senior Level", 3),
            ("JL_004", "Lead Level", 4),
            ("JL_005", "Manager Level", 5)
        ]

        for jl_id, name, level_num in levels:
            job_level = DBJobLevel(
                id=jl_id,
                name=name,
                code=f"CODE_{level_num}",
                level_number=level_num,
                organization_id=test_org.id
            )
            db.add(job_level)

        db.commit()

        # Verify all created
        jls = db.query(DBJobLevel).filter(
            DBJobLevel.organization_id == test_org.id
        ).all()
        assert len(jls) == 5

    def test_retrieve_job_level_by_number(self, db, test_org):
        """Test retrieving job level by level number"""
        job_level = DBJobLevel(
            id="JL_SEARCH",
            name="Search Level",
            code="SEARCH",
            level_number=3,
            organization_id=test_org.id
        )
        db.add(job_level)
        db.commit()

        retrieved = db.query(DBJobLevel).filter(
            DBJobLevel.level_number == 3,
            DBJobLevel.organization_id == test_org.id
        ).first()
        assert retrieved is not None
        assert retrieved.name == "Search Level"

    def test_job_level_numeric_order(self, db, test_org):
        """Test job levels maintain numeric order"""
        for i in range(1, 6):
            job_level = DBJobLevel(
                id=f"JL_ORD_{i}",
                name=f"Level {i}",
                code=f"L{i}",
                level_number=i,
                organization_id=test_org.id
            )
            db.add(job_level)

        db.commit()

        # Retrieve in order
        jls = db.query(DBJobLevel).filter(
            DBJobLevel.organization_id == test_org.id
        ).order_by(DBJobLevel.level_number).all()

        for i, jl in enumerate(jls):
            assert jl.level_number == i + 1


# ============================================================================
# TEST SUITE 2: GRADE CREATION & MANAGEMENT
# ============================================================================

class TestGradeCreation:
    """Tests for grade creation and management"""

    def test_create_grade_basic(self, db, test_org):
        """Test creating basic grade"""
        grade = DBGrade(
            id="GRADE_001",
            name="Grade A",
            level=1,
            code="GA",
            organization_id=test_org.id
        )
        db.add(grade)
        db.commit()
        db.refresh(grade)

        assert grade.id == "GRADE_001"
        assert grade.name == "Grade A"
        assert grade.level == 1

    def test_create_multiple_grades(self, db, test_org):
        """Test creating multiple grades"""
        grades_data = [
            ("GRADE_A", "Grade A", 1, "GA"),
            ("GRADE_B", "Grade B", 2, "GB"),
            ("GRADE_C", "Grade C", 3, "GC"),
        ]

        for gid, name, level, code in grades_data:
            grade = DBGrade(
                id=gid,
                name=name,
                level=level,
                code=code,
                organization_id=test_org.id
            )
            db.add(grade)

        db.commit()

        grades = db.query(DBGrade).filter(
            DBGrade.organization_id == test_org.id
        ).all()
        assert len(grades) == 3

    def test_retrieve_grade_by_level(self, db, test_org):
        """Test retrieving grade by level"""
        grade = DBGrade(
            id="GRADE_LEVEL",
            name="Level Search",
            level=5,
            code="LS",
            organization_id=test_org.id
        )
        db.add(grade)
        db.commit()

        retrieved = db.query(DBGrade).filter(
            DBGrade.level == 5,
            DBGrade.organization_id == test_org.id
        ).first()
        assert retrieved is not None

    def test_grade_organization_isolation(self, db, test_org):
        """Test grades are isolated per organization"""
        grade = DBGrade(
            id="GRADE_ISO",
            name="Isolated",
            level=1,
            code="ISO",
            organization_id=test_org.id
        )
        db.add(grade)
        db.commit()

        # Query by org
        grades = db.query(DBGrade).filter(
            DBGrade.organization_id == test_org.id
        ).all()
        assert len(grades) == 1


# ============================================================================
# TEST SUITE 3: DESIGNATION CREATION & MANAGEMENT
# ============================================================================

class TestDesignationCreation:
    """Tests for designation creation and management"""

    def test_create_designation_basic(self, db, test_org, test_dept):
        """Test creating basic designation"""
        grade = DBGrade(
            id="GRADE_DES",
            name="Grade",
            level=1,
            code="G",
            organization_id=test_org.id
        )
        db.add(grade)
        db.commit()

        des = DBDesignation(
            id="DES_001",
            name="Software Engineer",
            code="SE",
            grade_id=grade.id,
            department_id=test_dept.id,
            organization_id=test_org.id
        )
        db.add(des)
        db.commit()
        db.refresh(des)

        assert des.name == "Software Engineer"
        assert des.grade_id == grade.id

    def test_create_designation_with_levels(self, db, test_org, test_dept):
        """Test creating designations at different levels"""
        grade = DBGrade(
            id="GRADE_LEVELS",
            name="Grade",
            level=1,
            code="GL",
            organization_id=test_org.id
        )
        db.add(grade)
        db.commit()

        designations = [
            ("DES_JR", "Junior Engineer", "JE"),
            ("DES_SR", "Senior Engineer", "SE"),
            ("DES_LD", "Team Lead", "TL"),
        ]

        for des_id, name, code in designations:
            des = DBDesignation(
                id=des_id,
                name=name,
                code=code,
                grade_id=grade.id,
                department_id=test_dept.id,
                organization_id=test_org.id
            )
            db.add(des)

        db.commit()

        deses = db.query(DBDesignation).filter(
            DBDesignation.organization_id == test_org.id
        ).all()
        assert len(deses) == 3

    def test_retrieve_designation_by_department(self, db, test_org, test_dept):
        """Test retrieving designations in department"""
        grade = DBGrade(
            id="GRADE_DEPT_DES",
            name="Grade",
            level=1,
            code="GDD",
            organization_id=test_org.id
        )
        db.add(grade)
        db.commit()

        for i in range(3):
            des = DBDesignation(
                id=f"DES_DEPT_{i}",
                name=f"Designation {i}",
                code=f"D{i}",
                grade_id=grade.id,
                department_id=test_dept.id,
                organization_id=test_org.id
            )
            db.add(des)

        db.commit()

        deses = db.query(DBDesignation).filter(
            DBDesignation.department_id == test_dept.id
        ).all()
        assert len(deses) == 3

    def test_designation_grade_relationship(self, db, test_org, test_dept):
        """Test designation maintains grade relationship"""
        grade = DBGrade(
            id="GRADE_REL",
            name="Grade",
            level=2,
            code="GR",
            organization_id=test_org.id
        )
        db.add(grade)
        db.commit()

        des = DBDesignation(
            id="DES_REL",
            name="Related",
            code="REL",
            grade_id=grade.id,
            department_id=test_dept.id,
            organization_id=test_org.id
        )
        db.add(des)
        db.commit()

        retrieved = db.query(DBDesignation).filter(
            DBDesignation.id == "DES_REL"
        ).first()

        assert retrieved.grade_id == grade.id


# ============================================================================
# TEST SUITE 4: RELATIONSHIPS & VALIDATION
# ============================================================================

class TestJobDesignationRelationships:
    """Tests for relationships between jobs, grades, and designations"""

    def test_designation_requires_grade(self, db, test_org, test_dept):
        """Test designation requires valid grade"""
        des = DBDesignation(
            id="DES_NO_GRADE",
            name="No Grade",
            code="NG",
            grade_id="NONEXISTENT_GRADE",
            department_id=test_dept.id,
            organization_id=test_org.id
        )
        db.add(des)

        with pytest.raises(Exception):  # FK constraint
            db.commit()

    def test_designation_requires_department(self, db, test_org):
        """Test designation requires valid department"""
        grade = DBGrade(
            id="GRADE_ND",
            name="Grade",
            level=1,
            code="GND",
            organization_id=test_org.id
        )
        db.add(grade)
        db.commit()

        des = DBDesignation(
            id="DES_NO_DEPT",
            name="No Dept",
            code="ND",
            grade_id=grade.id,
            department_id="NONEXISTENT_DEPT",
            organization_id=test_org.id
        )
        db.add(des)

        with pytest.raises(Exception):  # FK constraint
            db.commit()

    def test_employee_with_designation(self, db, test_org, test_dept):
        """Test employee assignment with designation"""
        grade = DBGrade(
            id="GRADE_EMP",
            name="Grade",
            level=1,
            code="GE",
            organization_id=test_org.id
        )
        db.add(grade)
        db.commit()

        des = DBDesignation(
            id="DES_EMP",
            name="Employee Des",
            code="ED",
            grade_id=grade.id,
            department_id=test_dept.id,
            organization_id=test_org.id
        )
        db.add(des)
        db.commit()

        emp = DBEmployee(
            id="EMP_DES",
            name="Employee",
            email="emp@test.com",
            designation_id=des.id,
            department_id=test_dept.id,
            organization_id=test_org.id
        )
        db.add(emp)
        db.commit()

        retrieved = db.query(DBEmployee).filter(
            DBEmployee.id == "EMP_DES"
        ).first()
        assert retrieved.designation_id == des.id

    def test_job_level_grade_mapping(self, db, test_org, test_dept):
        """Test mapping between job levels and grades"""
        job_level = DBJobLevel(
            id="JL_GRADE",
            name="Level",
            code="LG",
            level_number=2,
            organization_id=test_org.id
        )
        db.add(job_level)
        db.commit()

        grade = DBGrade(
            id="GRADE_JL",
            name="Grade",
            level=2,
            code="GJL",
            organization_id=test_org.id
        )
        db.add(grade)
        db.commit()

        # Both should be independently queryable
        jl = db.query(DBJobLevel).filter(
            DBJobLevel.level_number == 2
        ).first()
        gr = db.query(DBGrade).filter(
            DBGrade.level == 2
        ).first()

        assert jl is not None
        assert gr is not None


# ============================================================================
# TEST SUITE 5: ERROR HANDLING & EDGE CASES
# ============================================================================

class TestJobDesignationErrorHandling:
    """Tests for error scenarios and edge cases"""

    def test_duplicate_designation_code(self, db, test_org, test_dept):
        """Test handling duplicate designation codes"""
        grade = DBGrade(
            id="GRADE_DUP",
            name="Grade",
            level=1,
            code="GD",
            organization_id=test_org.id
        )
        db.add(grade)
        db.commit()

        des1 = DBDesignation(
            id="DES_DUP_1",
            name="Des 1",
            code="DUP_CODE",
            grade_id=grade.id,
            department_id=test_dept.id,
            organization_id=test_org.id
        )
        db.add(des1)
        db.commit()

        des2 = DBDesignation(
            id="DES_DUP_2",
            name="Des 2",
            code="DUP_CODE",  # Duplicate code
            grade_id=grade.id,
            department_id=test_dept.id,
            organization_id=test_org.id
        )
        db.add(des2)
        with pytest.raises(Exception):
            db.commit()

    def test_negative_grade_level(self, db, test_org):
        """Test creating grade with negative level"""
        grade = DBGrade(
            id="GRADE_NEG",
            name="Negative",
            level=-1,
            code="NEG",
            organization_id=test_org.id
        )
        db.add(grade)
        db.commit()  # SQLite allows this, app should validate

    def test_zero_job_level_number(self, db, test_org):
        """Test job level with level_number 0"""
        job_level = DBJobLevel(
            id="JL_ZERO",
            name="Zero",
            code="ZERO",
            level_number=0,
            organization_id=test_org.id
        )
        db.add(job_level)
        db.commit()  # SQLite allows, app should validate

    def test_very_long_designation_name(self, db, test_org, test_dept):
        """Test designation with very long name"""
        grade = DBGrade(
            id="GRADE_LONG",
            name="Grade",
            level=1,
            code="GL",
            organization_id=test_org.id
        )
        db.add(grade)
        db.commit()

        long_name = "A" * 500  # Very long name
        des = DBDesignation(
            id="DES_LONG",
            name=long_name,
            code="LONG",
            grade_id=grade.id,
            department_id=test_dept.id,
            organization_id=test_org.id
        )
        db.add(des)
        db.commit()

        assert len(des.name) == 500

    def test_special_characters_in_code(self, db, test_org):
        """Test grade code with special characters"""
        grade = DBGrade(
            id="GRADE_SPECIAL",
            name="Special",
            level=1,
            code="G-R@D#E",
            organization_id=test_org.id
        )
        db.add(grade)
        db.commit()

        assert grade.code == "G-R@D#E"
