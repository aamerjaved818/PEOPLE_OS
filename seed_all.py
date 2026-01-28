import uuid
from datetime import datetime
import bcrypt
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend.domains.core import models as core_models
from backend.domains.hcm import models as hcm_models

def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def seed_data():
    # Ensure tables exist
    core_models.Base.metadata.create_all(bind=engine)
    hcm_models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Create System Admin (Database-backed)
        sys_admin_exists = db.query(core_models.DBUser).filter(core_models.DBUser.username == "sysadmin").first()
        if not sys_admin_exists:
            sys_admin = core_models.DBUser(
                id=str(uuid.uuid4()),
                username="sysadmin",
                password_hash=_hash_password("admin123"),
                role="SystemAdmin",
                name="System Administrator",
                email="sysadmin@peopleos.local",
                is_active=True,
                is_system_user=True,
                organization_id=None
            )
            db.add(sys_admin)
            print("Created System Admin: sysadmin")
        
        # 2. Create Organization
        org_exists = db.query(core_models.DBOrganization).filter(core_models.DBOrganization.code == "ORG001").first()
        if not org_exists:
            org = core_models.DBOrganization(
                id=str(uuid.uuid4()),
                code="ORG001",
                name="PeopleOS Corp",
                email="contact@peopleos.corp",
                is_active=True
            )
            db.add(org)
            db.flush()
            print(f"Created Organization: {org.name}")
            
            # 3. Create Super Admin for Org
            super_admin = core_models.DBUser(
                id=str(uuid.uuid4()),
                username="orgadmin",
                password_hash=_hash_password("admin123"),
                role="Super Admin",
                name="PeopleOS Org Admin",
                email="admin@peopleos.corp",
                is_active=True,
                is_system_user=False,
                organization_id=org.id
            )
            db.add(super_admin)
            print(f"Created Org Super Admin: orgadmin for {org.name}")
            
        db.commit()
        print("✅ Seeding complete successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
