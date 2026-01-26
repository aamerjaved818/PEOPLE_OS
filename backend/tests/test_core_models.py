"""
Tests for core models (Users, Locations, Audit Logs).
"""
import pytest
from backend.domains.core.models import (
    DBOrganization, DBUser, DBHRPlant, DBPlantDivision, 
    DBAuditLog, DBRolePermission, DBApiKey
)


@pytest.fixture
def test_org(db):
    """Create test organization"""
    org = DBOrganization(
        id="ORG_CORE",
        code="CORE_ORG",
        name="Core Test Org",
        email="core@org.com",
        phone="123",
        description="Test"
    )
    db.add(org)
    db.commit()
    return org


def test_create_user(db, test_org):
    """Test creating a user"""
    user = DBUser(
        id="USR001",
        username="testuser",
        password_hash="hashed_password",
        role="HRManager",
        name="Test User",
        email="test@user.com",
        organization_id=test_org.id,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    retrieved = db.query(DBUser).filter_by(id="USR001").first()
    assert retrieved.username == "testuser"
    assert retrieved.role == "HRManager"


def test_user_unique_username(db, test_org):
    """Test that usernames are unique"""
    user1 = DBUser(
        id="USR002",
        username="duplicate",
        password_hash="hash1",
        role="Admin",
        organization_id=test_org.id
    )
    db.add(user1)
    db.commit()
    
    user2 = DBUser(
        id="USR003",
        username="duplicate",  # Duplicate
        password_hash="hash2",
        role="Admin",
        organization_id=test_org.id
    )
    db.add(user2)
    
    with pytest.raises(Exception):
        db.commit()


def test_user_system_user_flag(db):
    """Test system user without organization"""
    sys_user = DBUser(
        id="SYS_USR",
        username="sysadmin",
        password_hash="hash",
        role="SystemAdmin",
        is_system_user=True
    )
    db.add(sys_user)
    db.commit()
    
    retrieved = db.query(DBUser).filter_by(id="SYS_USR").first()
    assert retrieved.is_system_user is True
    assert retrieved.organization_id is None


def test_create_plant(db, test_org):
    """Test creating a plant/location"""
    plant = DBHRPlant(
        id="PLANT001",
        name="Karachi Factory",
        location="Karachi, Pakistan",
        code="KHI",
        organization_id=test_org.id,
        is_active=True
    )
    db.add(plant)
    db.commit()
    
    retrieved = db.query(DBHRPlant).filter_by(id="PLANT001").first()
    assert retrieved.name == "Karachi Factory"
    assert retrieved.location == "Karachi, Pakistan"


def test_plant_unique_code(db, test_org):
    """Test that plant codes are unique"""
    plant1 = DBHRPlant(
        id="PLANT002",
        name="Lahore Factory",
        location="Lahore",
        code="LHR",
        organization_id=test_org.id
    )
    db.add(plant1)
    db.commit()
    
    plant2 = DBHRPlant(
        id="PLANT003",
        name="Another Lahore",
        location="Lahore",
        code="LHR",  # Duplicate
        organization_id=test_org.id
    )
    db.add(plant2)
    
    with pytest.raises(Exception):
        db.commit()


def test_plant_with_divisions(db, test_org):
    """Test plant with divisions"""
    plant = DBHRPlant(
        id="PLANT004",
        name="Islamabad Factory",
        location="Islamabad",
        code="ISB",
        organization_id=test_org.id
    )
    db.add(plant)
    db.commit()
    
    div1 = DBPlantDivision(
        id="DIV001",
        plant_id=plant.id,
        name="Production",
        code="PROD",
        is_active=True
    )
    div2 = DBPlantDivision(
        id="DIV002",
        plant_id=plant.id,
        name="Quality",
        code="QA",
        is_active=True
    )
    db.add_all([div1, div2])
    db.commit()
    
    divisions = db.query(DBPlantDivision).filter_by(plant_id=plant.id).all()
    assert len(divisions) == 2


def test_create_division(db, test_org):
    """Test creating a division"""
    plant = DBHRPlant(
        id="PLANT005",
        name="Faisalabad Factory",
        location="Faisalabad",
        code="FSD",
        organization_id=test_org.id
    )
    db.add(plant)
    db.commit()
    
    div = DBPlantDivision(
        id="DIV003",
        plant_id=plant.id,
        name="Maintenance",
        code="MTN",
        is_active=True
    )
    db.add(div)
    db.commit()
    
    retrieved = db.query(DBPlantDivision).filter_by(id="DIV003").first()
    assert retrieved.name == "Maintenance"


def test_division_unique_code(db, test_org):
    """Test that division codes are unique"""
    plant = DBHRPlant(
        id="PLANT006",
        name="Test Plant",
        location="Location",
        code="TST",
        organization_id=test_org.id
    )
    db.add(plant)
    db.commit()
    
    div1 = DBPlantDivision(
        id="DIV004",
        plant_id=plant.id,
        name="Division 1",
        code="DIV1"
    )
    db.add(div1)
    db.commit()
    
    div2 = DBPlantDivision(
        id="DIV005",
        plant_id=plant.id,
        name="Division 2",
        code="DIV1"  # Duplicate
    )
    db.add(div2)
    
    with pytest.raises(Exception):
        db.commit()


def test_create_audit_log(db, test_org):
    """Test creating an audit log"""
    audit = DBAuditLog(
        id="AUD001",
        organization_id=test_org.id,
        user="testuser",
        action="CREATE_EMPLOYEE",
        status="Success",
        time="2026-01-15T10:30:00"
    )
    db.add(audit)
    db.commit()
    
    retrieved = db.query(DBAuditLog).filter_by(id="AUD001").first()
    assert retrieved.action == "CREATE_EMPLOYEE"
    assert retrieved.status == "Success"


def test_create_role_permission(db, test_org):
    """Test creating role permissions"""
    perm = DBRolePermission(
        role="HRManager",
        permission="CREATE_EMPLOYEE",
        organization_id=test_org.id
    )
    db.add(perm)
    db.commit()
    
    retrieved = db.query(DBRolePermission).filter_by(role="HRManager").first()
    assert retrieved.permission == "CREATE_EMPLOYEE"


def test_create_api_key(db, test_org):
    """Test creating an API key"""
    key = DBApiKey(
        id="KEY001",
        organization_id=test_org.id
    )
    db.add(key)
    db.commit()
    
    retrieved = db.query(DBApiKey).filter_by(id="KEY001").first()
    assert retrieved.organization_id == test_org.id


def test_plant_cascade_delete(db, test_org):
    """Test that plant cascades to divisions"""
    plant = DBHRPlant(
        id="PLANT007",
        name="Cascade Test",
        location="Location",
        code="CAS",
        organization_id=test_org.id
    )
    db.add(plant)
    db.commit()
    
    div = DBPlantDivision(
        id="DIV006",
        plant_id=plant.id,
        name="Test Division",
        code="TD"
    )
    db.add(div)
    db.commit()
    
    # Verify division exists
    div_check = db.query(DBPlantDivision).filter_by(id="DIV006").first()
    assert div_check is not None
    
    # Delete plant
    db.delete(plant)
    db.commit()
    
    # Verify division is deleted (CASCADE)
    div_after = db.query(DBPlantDivision).filter_by(id="DIV006").first()
    assert div_after is None
