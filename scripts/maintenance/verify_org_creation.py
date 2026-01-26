
import os
import sys
import uuid
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.append(os.getcwd())

from backend.database import SessionLocal, engine
from backend import crud, schemas, models
from backend.domains.core import models as core_models

def verify():
    print("--- Verifying Organization Creation Logic ---")
    db = SessionLocal()
    
    # Test Data
    test_org_id = f"TEST-ORG-{str(uuid.uuid4())[:4].upper()}"
    test_org_name = f"Verification Org {test_org_id}"
    
    print(f"1. Creating Organization with ID: {test_org_id}")
    print(f"   (Expectation: Code will automatically be set to {test_org_id})")
    
    try:
        # Create Payload
        # We purposely pass a DIFFERENT code to see if it gets overridden/ignored
        # OR we pass None. Let's pass None to rely on the auto-set logic.
        org_data = schemas.OrganizationCreate(
            id=test_org_id,
            name=test_org_name,
            code="SHOULD-BE-IGNORED", # Testing the enforcement
            is_active=True
        )
        
        # Action
        created_org = crud.create_organization(db, org_data, user_id="system_verifier")
        
        # Verification 1: Org Code = Org ID
        print(f"2. Inspecting Created Organization:")
        print(f"   - ID:   {created_org.id}")
        print(f"   - Code: {created_org.code}")
        
        msg_list = []
        if created_org.id == created_org.code:
             msg = "   [SUCCESS] Organization Code matches ID."
             print(msg)
             msg_list.append(msg)
        else:
             print("   [FAILURE] Organization Code DOES NOT match ID.")
             return

        # Verification 2: Super Admin Creation
        target_username = test_org_id
        print(f"3. Inspecting Provisioned Super Admin:")
        print(f"   - Looking for username: {target_username}")
        
        admin_user = db.query(models.DBUser).filter(models.DBUser.username == target_username).first()
        
        if admin_user:
            msg = f"   [SUCCESS] Admin user found.\n   - Username: {admin_user.username}\n   - Role: {admin_user.role}"
            print(msg)
            msg_list.append(msg)
        else:
             print("   [FAILURE] Admin user NOT found.")
             print(f"   - Searched for: {target_username}")
             return

        # Write success log
        with open("verification_success.txt", "w") as f:
            f.write("\n".join(msg_list))

        # Cleanup
        print("4. Cleanup: Removing test data...")
        try:
            db.delete(admin_user)
            db.delete(created_org)
            db.commit()
            print("   [SUCCESS] Cleanup complete.")
        except Exception as cleanup_err:
             print(f"   [WARNING] Cleanup failed (non-critical): {cleanup_err}")
             # Swallow cleanup error to show success
        
    except Exception as e:
        error_msg = f"[EXCEPTION]: {e}\n"
        print(error_msg)
        import traceback
        full_trace = traceback.format_exc()
        print(full_trace)
        
        with open("verification_error.log", "w") as f:
            f.write(error_msg)
            f.write(full_trace)
    finally:
        db.close()

if __name__ == "__main__":
    verify()
