
import os
import sys

# Add parent directory to path to allow importing backend modules
sys.path.append(os.getcwd())

from backend.database import SessionLocal
from backend.domains.core.models import DBOrganization


from backend.database import SessionLocal
from backend.domains.core.models import DBOrganization, DBUser
from backend import crud

def migrate():
    print("--- Starting Migration: Org Code Sync & Admin Cleanup ---")
    db = SessionLocal()
    try:
        # 1. Sync Org Code
        org = db.query(DBOrganization).filter(DBOrganization.id == "ORG-001").first()
        if org:
            print(f"Checking Default Org: {org.name}")
            if org.code != "ORG-001":
                org.code = "ORG-001"
                db.commit()
                print("✅ Updated Org Code to match ID (ORG-001)")
            else:
                print("✅ Org Code already correct")
                
            # 2. Remove Legacy Super Admins (Clean Slate)
            # Remove generic 'admin'
            legacy_admin = db.query(DBUser).filter(DBUser.username == "admin").first()
            if legacy_admin:
                db.delete(legacy_admin)
                print("✅ Legacy 'admin' removed.")
            
            # Remove previous iteration 'admin@org001' if it exists
            prev_admin = db.query(DBUser).filter(DBUser.username == "admin@org001").first()
            if prev_admin:
                db.delete(prev_admin)
                print("✅ Previous 'admin@org001' removed.")
                
            db.commit()

            # 3. Provision New Standard Admin (Username = Org Code)
            print("Provisioning new Simple Admin (User=Code)...")
            try:
                # This will now use the updated logic in crud.py: Username=ORG-001, Pass=ORG-001
                crud.provision_org_admin(db, org, "system_migration")
                db.commit()
                print(f"✅ New Default Admin '{org.code}' provisioned successfully.")
            except Exception as e:
                print(f"⚠️ Provisioning note: {e}")

        else:
            print("❌ Default Organization ORG-001 not found.")
            
    except Exception as e:
        print(f"❌ Migration Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
