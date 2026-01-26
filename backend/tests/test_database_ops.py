"""
Tests for CRUD utilities and database operations.
"""
import pytest
from sqlalchemy.exc import IntegrityError
from backend.database import get_db, get_session_local, get_engine
from backend.domains.core.models import DBOrganization, DBUser


def test_get_engine():
    """Test engine retrieval"""
    engine = get_engine()
    assert engine is not None


def test_get_session_local():
    """Test session factory"""
    SessionLocal = get_session_local()
    session = SessionLocal()
    assert session is not None
    session.close()


def test_get_db_dependency():
    """Test FastAPI dependency function"""
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None
    
    # Cleanup
    try:
        next(db_gen)
    except StopIteration:
        pass


def test_database_transaction_rollback(db):
    """Test that failed transactions rollback"""
    org = DBOrganization(
        id="ORG_ROLLBACK",
        code="ROLLBACK",
        name="Rollback Test",
        email="rollback@test.com",
        phone="123",
        description="Test"
    )
    db.add(org)
    db.commit()
    
    # Try to add duplicate code
    org2 = DBOrganization(
        id="ORG_ROLLBACK2",
        code="ROLLBACK",  # Duplicate
        name="Rollback Test 2",
        email="rollback2@test.com",
        phone="123",
        description="Test"
    )
    db.add(org2)
    
    with pytest.raises(IntegrityError):
        db.commit()
    
    # Rollback
    db.rollback()
    
    # Verify original org still exists
    retrieved = db.query(DBOrganization).filter_by(id="ORG_ROLLBACK").first()
    assert retrieved is not None


def test_database_multiple_operations(db):
    """Test multiple operations in single transaction"""
    # Create org
    org = DBOrganization(
        id="ORG_MULTI",
        code="MULTI",
        name="Multi Test",
        email="multi@test.com",
        phone="123",
        description="Test"
    )
    db.add(org)
    
    # Create users
    user1 = DBUser(
        id="USR_MULTI1",
        username="multiuser1",
        password_hash="hash",
        role="Admin",
        organization_id=org.id
    )
    user2 = DBUser(
        id="USR_MULTI2",
        username="multiuser2",
        password_hash="hash",
        role="HRManager",
        organization_id=org.id
    )
    
    db.add_all([user1, user2])
    db.commit()
    
    # Verify all exist
    retrieved_org = db.query(DBOrganization).filter_by(id="ORG_MULTI").first()
    retrieved_users = db.query(DBUser).filter_by(organization_id=org.id).all()
    
    assert retrieved_org is not None
    assert len(retrieved_users) == 2


def test_query_filters(db):
    """Test various query filters"""
    # Create test data
    org = DBOrganization(
        id="ORG_QUERY",
        code="QUERY",
        name="Query Test",
        email="query@test.com",
        phone="123",
        description="Test"
    )
    db.add(org)
    db.commit()
    
    user1 = DBUser(
        id="USR_Q1",
        username="quser1",
        password_hash="hash",
        role="Admin",
        organization_id=org.id,
        is_active=True
    )
    user2 = DBUser(
        id="USR_Q2",
        username="quser2",
        password_hash="hash",
        role="HRManager",
        organization_id=org.id,
        is_active=False
    )
    db.add_all([user1, user2])
    db.commit()
    
    # Test filter by role
    admins = db.query(DBUser).filter_by(role="Admin").all()
    assert len(admins) >= 1
    
    # Test filter by is_active
    active = db.query(DBUser).filter_by(is_active=True, organization_id=org.id).all()
    assert len(active) == 1
    
    # Test filter by organization
    org_users = db.query(DBUser).filter_by(organization_id=org.id).all()
    assert len(org_users) == 2


def test_update_operation(db):
    """Test updating records"""
    org = DBOrganization(
        id="ORG_UPDATE",
        code="UPDATE",
        name="Update Test",
        email="update@test.com",
        phone="123",
        description="Initial"
    )
    db.add(org)
    db.commit()
    
    # Update
    org.description = "Updated"
    org.is_active = False
    db.commit()
    
    # Verify
    retrieved = db.query(DBOrganization).filter_by(id="ORG_UPDATE").first()
    assert retrieved.description == "Updated"
    assert retrieved.is_active is False


def test_delete_operation(db):
    """Test deleting records"""
    org = DBOrganization(
        id="ORG_DELETE",
        code="DELETE",
        name="Delete Test",
        email="delete@test.com",
        phone="123",
        description="To delete"
    )
    db.add(org)
    db.commit()
    
    # Verify exists
    check1 = db.query(DBOrganization).filter_by(id="ORG_DELETE").first()
    assert check1 is not None
    
    # Delete
    db.delete(org)
    db.commit()
    
    # Verify deleted
    check2 = db.query(DBOrganization).filter_by(id="ORG_DELETE").first()
    assert check2 is None
