
import logging
import json
import uuid
import sys
import os

# Add parent directory to path to allow importing backend modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from backend.database import SessionLocal, engine
from backend.database import SessionLocal, engine
# from backend import models, crud  <-- REMOVED GLOBAL IMPORT
from sqlalchemy import text
# Configure Logging
import logging
from backend.permissions_config import DEFAULT_ROLE_PERMISSIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_permissions():
    from backend.domains.core import models
    from backend import crud  # Local import to prevent eager loading
    db = SessionLocal()
    try:
        logger.info("Checking Role Permissions...")
        
        # Ensure table exists
        models.Base.metadata.create_all(bind=engine)

        # 1. Ensure Default Organization exists
        org = db.query(models.DBOrganization).filter(models.DBOrganization.id == "ORG-001").first()
        if not org:
            logger.info("Creating Default Organization...")
            org = models.DBOrganization(
                id="ORG-001",
                code="DEF",
                name="Default Organization",
                is_active=True
            )
            db.add(org)
            db.commit()
            logger.info("Default Organization created.")
        
        existing_perms = crud.get_all_role_permissions(db)
        
        created_count = 0
        updated_count = 0
        
        for role, default_perms in DEFAULT_ROLE_PERMISSIONS.items():
            if role not in existing_perms or not existing_perms[role]:
                logger.info(f"Seeding permissions for role: {role}")
                crud.update_role_permissions(db, role, default_perms)
                created_count += 1
            else:
                logger.info(f"Permissions for {role} instead of skipping update forced override for dev")
                # Force update to ensure new defaults are applied
                crud.update_role_permissions(db, role, default_perms)
                updated_count += 1
                
        logger.info(f"Seeding Complete. Created: {created_count}, Updated: {updated_count}")

        # --- MANAGE SYSTEM USERS ---
        logger.info("Standardizing System Users (.amer, admin)...")
        
        # 1. Ensure .amer (Root)
        amer = db.query(models.DBUser).filter(models.DBUser.username == ".amer").first()
        if amer:
            amer.role = "Root"
            amer.is_system_user = True
            logger.info("Updated .amer as Root and System User.")
        else:
            # Do NOT create a new Root user automatically. If '.amer' is missing,
            # someone must provision the Root account manually to avoid accidental
            # privilege escalation. Log a warning for operators.
            logger.warning("'.amer' user not found. Skipping automatic creation of Root user.")
        
        # 2. RBAC ENFORCEMENT: Only Root has system-wide access across all organizations.
        # Super Admin users are org-scoped and should NOT be created as system users.
        # Delete conflicting 'admin' Super Admin user if it exists.
        admin = db.query(models.DBUser).filter(models.DBUser.username == "admin").first()
        if admin:
            db.delete(admin)
            logger.info("Removed conflicting 'admin' Super Admin user (only Root should be system-wide).")
        
        db.commit()

        # 3. Unmark 'is_system_user' for everyone else
        logger.info("Unprotecting all other users...")
        sql = text("UPDATE users SET is_system_user = 0 WHERE username NOT IN ('.amer')")
        result = db.execute(sql)
        db.commit()
        logger.info(f"Unprotected users count (approximation): {result.rowcount}")
        
    except Exception as e:
        logger.error(f"Seeding Failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_permissions()
