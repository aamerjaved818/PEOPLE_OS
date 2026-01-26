import os
import shutil
import datetime
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_backup():
    """
    Automated database backup script for People_OS.
    Handles environment-specific databases and maintains a 7-day rotation.
    """
    # Import config to get DB paths
    try:
        from backend.config import settings
    except ImportError:
        logger.error("Could not import backend.config. Ensure script is run from project root.")
        return

    db_path = Path(settings.DB_PATH)
    if not db_path.exists():
        logger.error(f"Database not found at {db_path}")
        return

    # Backup directory
    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamped filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    env = settings.ENVIRONMENT
    backup_filename = f"people_os_{env}_backup_{timestamp}.db"
    backup_path = backup_dir / backup_filename

    try:
        # Copy database file
        shutil.copy2(db_path, backup_path)
        logger.info(f"Successfully created backup: {backup_path}")

        # Cleanup old backups (keep last 7 days)
        retention_days = 7
        now = datetime.datetime.now()
        for f in backup_dir.glob(f"people_os_{env}_backup_*.db"):
            file_time = datetime.datetime.fromtimestamp(f.stat().st_mtime)
            if (now - file_time).days > retention_days:
                f.unlink()
                logger.info(f"Deleted old backup: {f.name}")

    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")

if __name__ == "__main__":
    run_backup()
