import logging
import sys
from sqlalchemy import text
from backend.database import engine, Base
from backend.domains.core import models as core_models
from backend.domains.hcm import models as hcm_models


# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migrations():
    """Run database migrations, verify schema, and seed system users."""
    # Get engine dynamically based on current APP_ENV
    logger.info("🚀 Starting Production Database Migration...")
    logger.info(f"📂 Target DB: {engine.url}")

    try:
        # Create tables
        logger.info("📦 Creating Core Tables...")
        core_models.Base.metadata.create_all(bind=engine)

        logger.info("📦 Creating HCM Tables...")
        hcm_models.Base.metadata.create_all(bind=engine)

        # Verify Foreign Keys
        logger.info("🔍 Verifying Foreign Key Constraint Enforcement...")
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA foreign_keys")).fetchone()
            if result and result[0] == 1:
                logger.info("✅ Foreign Keys are ENFORCED.")
            else:
                logger.warning(
                    "⚠️ Foreign Keys are NOT ENFORCED at connection level."
                )

        # Seed System Users
        logger.info("👤 Seeding System Users...")
        from backend.seed_users import seed_system_users
        created = seed_system_users()
        logger.info(f"✅ System Users: {created} new, rest already exist.")

        logger.info("✨ Database Migration Complete.")
        return True
    except Exception as e:
        logger.error(f"❌ Migration Failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
