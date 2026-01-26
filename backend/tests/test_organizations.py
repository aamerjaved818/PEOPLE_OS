"""
Tests for Organization CRUD operations and FK constraints.
"""
import pytest
from backend.domains.core.models import DBOrganization
from backend.crud import (
    create_organization, get_organization, get_organizations,
    update_organization, delete_organization
)


def test_create_organization(db):
    """Test creating a new organization"""
    org_data = {
        "code": "ORG001",
        "name": "Test Organization",
        "email": "org@test.com",
        "phone": "1234567890",
        "description": "Test org"
    }
    from backend import schemas
    org_schema = schemas.OrganizationCreate(**org_data)
    org = create_organization(db, org_schema, user_id="admin")
    assert org.code == "ORG001"
    assert org.name == "Test Organization"
    assert org.is_active is True


def test_create_organization_duplicate_code_fails(db):
    """Test that duplicate organization codes fail"""
    org_data = {
        "code": "ORG002",
        "name": "Org 2",
        "email": "org2@test.com",
        "phone": "1234567890",
        "description": "Test"
    }
    from backend import schemas
    org_schema = schemas.OrganizationCreate(**org_data)
    create_organization(db, org_schema, user_id="admin")
    
    # Attempt duplicate
    with pytest.raises(Exception):
        create_organization(db, org_schema, user_id="admin")


def test_get_organization(db):
    """Test retrieving an organization"""
    org_data = {
        "code": "ORG003",
        "name": "Org 3",
        "email": "org3@test.com",
        "phone": "1234567890",
        "description": "Test"
    }
    from backend import schemas
    org_schema = schemas.OrganizationCreate(**org_data)
    created = create_organization(db, org_schema, user_id="admin")
    retrieved = get_organization(db, created.id)
    assert retrieved.id == created.id
    assert retrieved.name == "Org 3"


def test_list_organizations(db):
    """Test listing organizations"""
    org_data1 = {
        "code": "ORG004",
        "name": "Org 4",
        "email": "org4@test.com",
        "phone": "1234567890",
        "description": "Test"
    }
    org_data2 = {
        "code": "ORG005",
        "name": "Org 5",
        "email": "org5@test.com",
        "phone": "1234567890",
        "description": "Test"
    }
    from backend import schemas
    org_schema1 = schemas.OrganizationCreate(**org_data1)
    org_schema2 = schemas.OrganizationCreate(**org_data2)
    create_organization(db, org_schema1, user_id="admin")
    create_organization(db, org_schema2, user_id="admin")
    
    orgs = get_organizations(db)
    assert len(orgs) >= 2


def test_update_organization(db):
    """Test updating an organization"""
    org_data = {
        "code": "ORG006",
        "name": "Org 6",
        "email": "org6@test.com",
        "phone": "1234567890",
        "description": "Test"
    }
    from backend import schemas
    org_schema = schemas.OrganizationCreate(**org_data)
    org = create_organization(db, org_schema, user_id="admin")
    
    update_data = {"name": "Updated Org 6", "currency": "USD"}
    update_schema = schemas.OrganizationCreate(**{**org_data, **update_data})
    updated = update_organization(db, org.id, update_schema, user_id="admin")
    assert updated.name == "Updated Org 6"
    assert updated.currency == "USD"


def test_delete_organization(db):
    """Test deleting an organization"""
    org_data = {
        "code": "ORG007",
        "name": "Org 7",
        "email": "org7@test.com",
        "phone": "1234567890",
        "description": "Test"
    }
    from backend import schemas
    org_schema = schemas.OrganizationCreate(**org_data)
    org = create_organization(db, org_schema, user_id="admin")
    org_id = org.id
    
    # Clean up any dependent records before deleting
    # Deactivate any active departments
    from backend.domains.core.models import DBDepartment
    db.query(DBDepartment).filter(
        DBDepartment.organization_id == org_id,
        DBDepartment.isActive == True
    ).update({DBDepartment.isActive: False})
    db.commit()
    
    delete_organization(db, org_id, current_user_id="admin")
    retrieved = get_organization(db, org_id)
    assert retrieved is None
