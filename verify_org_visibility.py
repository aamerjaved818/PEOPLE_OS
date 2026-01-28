import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.database import get_session_local
from backend.routers.core_org import get_organizations
from backend.schemas import OrganizationList

# Mock User Context
mock_sysadmin = {
    "id": "f7bb9802-fa89-4659-8679-f1367f92482b",
    "username": "sysadmin",
    "role": "SystemAdmin",
    "organization_id": None
}

mock_root = {
    "id": "root-user-id",
    "username": "root",
    "role": "Root",
    "organization_id": None
}

# Generic Admin (Should see nothing if no org assigned)
mock_generic = {
    "id": "generic-user-id",
    "username": "generic",
    "role": "Business Admin",
    "organization_id": None
}

def verify():
    SessionMaker = get_session_local()
    db = SessionMaker()
    try:
        print("--- Testing SystemAdmin Visibility ---")
        orgs_sysadmin = get_organizations(db, mock_sysadmin)
        print(f"SystemAdmin sees {len(orgs_sysadmin)} organizations.")
        for org in orgs_sysadmin:
            print(f" - {org.name} ({org.code})")

        print("\n--- Testing Root Visibility ---")
        orgs_root = get_organizations(db, mock_root)
        print(f"Root sees {len(orgs_root)} organizations.")
        
        print("\n--- Testing Generic Admin (No Org) Visibility ---")
        orgs_generic = get_organizations(db, mock_generic)
        print(f"Generic Admin sees {len(orgs_generic)} organizations.")

    except Exception as e:
        print(f"Verification Failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify()
