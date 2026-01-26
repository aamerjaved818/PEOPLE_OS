import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os

# Set test environment to use in-memory DB
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["APP_ENV"] = "test"

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database import Base
# Ensure all domain models are imported so their tables are registered on Base.metadata
import backend.domains.core.models
import backend.domains.hcm.models
# from backend.main import app, get_db

# Use in-memory SQLite for tests - now handled by DATABASE_URL env var
SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},
    poolclass=StaticPool # Add StaticPool for in-memory
)

from sqlalchemy import event
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    # Disable foreign key enforcement for test convenience (many tests insert
    # records without creating all referenced FK rows). Tests handle
    # validation at application level.
    cursor.execute("PRAGMA foreign_keys=OFF")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    # Create the database and tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Disable foreign keys before dropping tables to avoid dependency errors
        with engine.connect() as conn:
            conn.execute(text("PRAGMA foreign_keys=OFF"))
            Base.metadata.drop_all(bind=conn)
            conn.execute(text("PRAGMA foreign_keys=ON"))


@pytest.fixture(scope="function")
def client():
    from backend.main import app, get_db
    import backend.database as _test_database
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    # Override both DB dependency objects used across modules:
    # - `backend.dependencies.get_db` (imported in main)
    # - `backend.database.get_db` (imported in routers like auth)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[_test_database.get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=OFF"))
        Base.metadata.drop_all(bind=conn)
        conn.execute(text("PRAGMA foreign_keys=ON"))


# ===== Test Fixtures for Leave Module =====

@pytest.fixture
def test_org(db):
    """Create test organization"""
    from backend.domains.core.models import DBOrganization
    
    org = DBOrganization(
        id="ORG-TEST-001",
        code="TEST",
        name="Test Organization",
        country="US",
        email="test@org.test",
        phone="555-0100",
        description="Test Organization",
        created_by="test_admin"
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def test_plant(db, test_org):
    """Create test plant/location"""
    from backend.domains.core.models import DBHRPlant
    
    plant = DBHRPlant(
        id="PLANT-TEST-001",
        organization_id=test_org.id,
        code="TEST",
        name="Test Plant",
        created_by="test_admin"
    )
    db.add(plant)
    db.commit()
    db.refresh(plant)
    return plant


@pytest.fixture
def test_shift(db, test_org):
    """Create test shift"""
    from backend.domains.hcm.models import DBShift
    
    shift = DBShift(
        id="SHIFT-TEST-001",
        code="TEST",
        name="Test Shift",
        organization_id=test_org.id,
        start_time="09:00",
        end_time="17:00",
        created_by="test_admin"
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


@pytest.fixture
def test_job_level(db, test_org):
    """Create test job level"""
    from backend.domains.hcm.models import DBJobLevel
    
    job_level = DBJobLevel(
        id="JOBLVL-TEST-001",
        code="TEST",
        name="Test Job Level",
        organization_id=test_org.id,
        created_by="test_admin"
    )
    db.add(job_level)
    db.commit()
    db.refresh(job_level)
    return job_level


@pytest.fixture
def test_grade(db, test_org, test_job_level):
    """Create test grade"""
    from backend.domains.hcm.models import DBGrade
    
    grade = DBGrade(
        id="GRADE-TEST-001",
        code="TEST",
        name="Test Grade",
        job_level_id=test_job_level.id,
        organization_id=test_org.id,
        created_by="test_admin"
    )
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade


@pytest.fixture
def test_designation(db, test_org, test_grade):
    """Create test designation"""
    from backend.domains.hcm.models import DBDesignation
    
    designation = DBDesignation(
        id="DESIG-TEST-001",
        code="TEST",
        name="Test Designation",
        grade_id=test_grade.id,
        organization_id=test_org.id,
        created_by="test_admin"
    )
    db.add(designation)
    db.commit()
    db.refresh(designation)
    return designation


@pytest.fixture
def test_dept(db, test_org):
    """Create test department"""
    from backend.domains.core.models import DBDepartment
    
    dept = DBDepartment(
        id="DEPT-TEST-001",
        organization_id=test_org.id,
        code="TEST",
        name="Test Department",
        description="Test department",
        isActive=True,
        created_by="test_admin"
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@pytest.fixture
def test_manager(db, test_org, test_plant, test_shift, test_grade, test_designation, test_dept):
    """Create test manager/user"""
    from backend.domains.hcm.models import DBEmployee
    
    manager = DBEmployee(
        id="MGR-TEST-001",
        name="Test Manager",
        email="manager@test.com",
        employee_code="MGR001",
        organization_id=test_org.id,
        department_id=test_dept.id,
        designation_id=test_designation.id,
        grade_id=test_grade.id,
        plant_id=test_plant.id,
        shift_id=test_shift.id,
        status="Active",
        join_date="2025-01-01",
        created_by="test_admin"
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)
    return manager


@pytest.fixture
def test_employee(db, test_org, test_plant, test_shift, test_grade, test_designation, test_dept, test_manager):
    """Create test employee"""
    from backend.domains.hcm.models import DBEmployee
    
    emp = DBEmployee(
        id="EMP-TEST-001",
        name="Test Employee",
        email="test@example.com",
        employee_code="EMP001",
        organization_id=test_org.id,
        department_id=test_dept.id,
        designation_id=test_designation.id,
        grade_id=test_grade.id,
        plant_id=test_plant.id,
        shift_id=test_shift.id,
        status="Active",
        join_date="2025-01-15",
        line_manager_id=test_manager.id,
        created_by="test_admin"
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp
