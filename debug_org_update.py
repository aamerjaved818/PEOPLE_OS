
import sys
import os
import json
import requests
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from backend import schemas
from backend import crud
from backend.database import SessionLocal

def debug_update():
    # Payload similar to what frontend seems to be sending based on OrganizationFormModal.tsx
    # It sends all fields in formData.
    payload = {
        "id": "ORG-001",
        "name": "People OS Limited",
        "code": "DEF",
        "industry": "Technology",
        "country": "Pakistan",
        "city": "Lahore",
        "email": "contact@peopleos.com",
        "website": "https://peopleos.com",
        "phone": "+92 300 1234567",
        "taxId": "TAX-123",
        "registrationNumber": "REG-456",
        "foundedDate": "2020-01-01",  # Frontend sends YYYY-MM-DD
        "isActive": True,
        # It's a Partial update, but frontend sends everything in formData state
    }
    
    print("--- Simulating Pydantic Validation ---")
    try:
        # Pydantic v2
        org_create = schemas.OrganizationCreate(**payload)
        print("Pydantic Validation: SUCCESS")
        print(org_create.model_dump())
    except Exception as e:
        print(f"Pydantic Validation: FAILED\n{e}")
        return

    print("\n--- Simulating Backend Update Logic ---")
    db = SessionLocal()
    try:
        user_id = "root-system-user-amer-001" # Valid user ID needed? or just string
        updated_org = crud.update_organization(db, "ORG-001", org_create, user_id)
        print("Update Logic: SUCCESS")
        print(f"Updated Org: {updated_org.name}")
        
        # Test serialization too (often where lazy loading fails)
        response_model = schemas.Organization.model_validate(updated_org)
        print("Response Serialization: SUCCESS")
        print(response_model.model_dump_json(by_alias=True))
        
    except Exception as e:
        print(f"Backend/DB Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
