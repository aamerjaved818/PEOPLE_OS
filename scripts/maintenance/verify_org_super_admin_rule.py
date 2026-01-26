
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.shared.models import models
from backend.shared.models import hcm_models
from backend import schemas, crud
import uuid

from backend.database import SessionLocal

def verify_atomic_creation():
    db = SessionLocal()
    org_id = f"TEST-ORG-{str(uuid.uuid4())[:8]}"
    admin_username = f"admin_{org_id.lower()}"
    
    print(f"--- Scenario 1: Successful Atomic Creation ---")
    payload = schemas.OrganizationWithAdminCreate(
        id=org_id,
        name="Test Organization",
        adminUsername=admin_username,
        adminPassword="securepassword123",
        adminEmail=f"admin@{org_id.lower()}.com",
        adminName="Test Admin"
    )
    
    try:
        new_org = crud.create_organization(db, payload, user_id="ROOT-001")
        print(f"SUCCESS: Organization {new_org.id} created.")
        
        # Verify Admin User
        admin_user = db.query(models.DBUser).filter(models.DBUser.organization_id == org_id).first()
        if admin_user and admin_user.username == admin_username:
            print(f"SUCCESS: Admin user '{admin_user.username}' found in organization.")
        else:
            print("FAILURE: Admin user NOT found or mismatch.")
            
    except Exception as e:
        print(f"FAILURE: Unexpected error in Scenario 1: {e}")
        db.rollback()

    print(f"\n--- Scenario 2: Transactional Rollback (Duplicate Username) ---")
    org_id_2 = f"TEST-ORG-FAIL-{str(uuid.uuid4())[:8]}"
    # Use the SAME admin_username as Scenario 1 to trigger failure in admin provisioning
    payload_fail = schemas.OrganizationWithAdminCreate(
        id=org_id_2,
        name="Failed Organization",
        adminUsername=admin_username, # DUPLICATE
        adminPassword="password",
        adminEmail="fail@test.com"
    )
    
    try:
        crud.create_organization(db, payload_fail, user_id="ROOT-001")
        print("FAILURE: Organization should NOT have been created due to duplicate admin username.")
    except Exception as e:
        print(f"SUCCESS: Correctly failed and rolled back. Error: {e}")
        
        # Verify Org 2 does NOT exist
        exists = db.query(models.DBOrganization).filter(models.DBOrganization.id == org_id_2).first()
        if not exists:
            print(f"SUCCESS: Organization {org_id_2} was NOT persisted (Rollback verified).")
        else:
            print(f"FAILURE: Organization {org_id_2} was persisted despite admin failure!")

    db.close()

if __name__ == "__main__":
    verify_atomic_creation()
