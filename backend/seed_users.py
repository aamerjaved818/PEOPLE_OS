import bcrypt
from datetime import datetime

from backend.config import settings
from backend.database import get_session_local, engine
from backend.domains.core import models as core_models
from backend.domains.hcm import models as hcm_models

# Ensure all tables are created before seeding
core_models.Base.metadata.create_all(bind=engine)
hcm_models.Base.metadata.create_all(bind=engine)

from backend.domains.core.models import DBUser


# Deterministic UUIDs for system users (same across all environments)
# NOTE: Only Root users should be created as system-wide users.
# Super Admin users are org-scoped and should not be auto-created here.
SYSTEM_USERS = {
    # Removed 'admin' Super Admin user - conflicts with RBAC rule (only Root has system-wide access)
    # 'amer' intentionally omitted to prevent automatic creation of Root user
}


def _hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def seed_system_users() -> int:
    """
    Seed all system users. Returns count of users created.

    Users are seeded with deterministic IDs to ensure consistency.
    Existing users are skipped (not overwritten).
    """
    session = get_session_local()()
    created = 0

    try:
        for user_key, user_data in SYSTEM_USERS.items():
            # Check if user exists by ID
            existing_by_id = session.query(DBUser).filter(
                DBUser.id == user_data["id"]
            ).first()
            
            if existing_by_id:
                print(f"  [SKIP] User '{user_data['username']}' already exists (ID match)")
                continue

            # Check if user exists by Username to prevent UNIQUE constraint failure
            existing_by_username = session.query(DBUser).filter(
                DBUser.username == user_data["username"]
            ).first()

            if existing_by_username:
                print(
                    f"  [SKIP] User '{user_data['username']}' "
                    f"already exists (Username match). "
                    f"ID: {existing_by_username.id} "
                    f"(Expected: {user_data['id']})"
                )
                continue
            
            # Create new user
            now = datetime.utcnow()
            user = DBUser(
                id=user_data["id"],
                username=user_data["username"],
                password_hash=_hash_password(user_data["password"]),
                role=user_data["role"],
                name=user_data["name"],
                email=user_data["email"],
                is_active=user_data["is_active"],
                is_system_user=user_data["is_system_user"],
                created_at=now,
                updated_at=now,
                created_by="system",
                updated_by="system",
            )
            session.add(user)
            print(f"  [NEW] User '{user_data['username']}' created")
            created += 1

        session.commit()
        return created
    except Exception as e:
        session.rollback()
        print(f"  [ERROR] Seeding failed: {str(e)}")
        raise
    finally:
        session.close()


def get_system_user_credentials() -> dict:
    """Return credentials for system users (for documentation)."""
    return {
        user["username"]: user["password"]
        for user in SYSTEM_USERS.values()
    }


if __name__ == "__main__":
    print(f"Seeding system users for environment: {settings.ENVIRONMENT}")
    print(f"Database: {settings.DB_PATH}")
    count = seed_system_users()
    print(f"✅ Seeding complete. {count} users created.")
