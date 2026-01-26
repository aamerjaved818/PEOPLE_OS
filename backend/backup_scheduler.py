"""
Database Backup Scheduler for peopleOS eBusiness Suite

Implements automated database backups with retention policy and compression.
Configured via environment variables:
- BACKUP_ENABLED: Enable/disable backups (default: true)
- BACKUP_TIME_UTC: Time for daily backup in UTC (default: 02:00)
- BACKUP_RETENTION_DAYS: Days to keep backups (default: 30)
"""

import logging
import os
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


class BackupManager:
    """Handles database backup and retention operations"""
    
    def __init__(self, backup_dir: str = "backups", retention_days: int = 30):
        """
        Initialize backup manager
        
        Args:
            backup_dir: Directory to store backups
            retention_days: Number of days to retain backups
        """
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
        self.db_path = os.getenv("DATABASE_URL", "sqlite:///./people_os.db").replace("sqlite:///", "")
        
        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Backup manager initialized. Directory: {self.backup_dir}, Retention: {retention_days} days")
    
    def create_backup(self) -> bool:
        """
        Create a backup of the SQLite database
        
        Returns:
            True if backup was successful, False otherwise
        """
        try:
            # Ensure DB file exists
            if not os.path.exists(self.db_path):
                logger.warning(f"Database file not found: {self.db_path}")
                return False
            
            # Generate backup filename with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"people_os_backup_{timestamp}.db"
            backup_path = self.backup_dir / backup_filename
            
            # Create backup using SQLite VACUUM
            conn = sqlite3.connect(self.db_path)
            try:
                # Open connection to backup database
                backup_conn = sqlite3.connect(str(backup_path))
                with backup_conn:
                    conn.backup(backup_conn)
                backup_conn.close()
                
                logger.info(f"Database backup created successfully: {backup_path}")
                logger.info(f"Backup size: {backup_path.stat().st_size / 1024 / 1024:.2f} MB")
                return True
            finally:
                conn.close()
                
        except Exception as e:
            logger.error(f"Backup creation failed: {e}", exc_info=True)
            return False
    
    def cleanup_old_backups(self) -> int:
        """
        Remove backups older than retention period
        
        Returns:
            Number of backups removed
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            removed_count = 0
            
            for backup_file in self.backup_dir.glob("people_os_backup_*.db"):
                # Extract timestamp from filename
                try:
                    # Format: people_os_backup_YYYYMMDD_HHMMSS.db
                    date_str = backup_file.stem.replace("people_os_backup_", "").replace("_", "")
                    backup_date = datetime.strptime(date_str[:8], "%Y%m%d")
                    
                    if backup_date < cutoff_date:
                        backup_file.unlink()
                        logger.info(f"Removed old backup: {backup_file.name}")
                        removed_count += 1
                except (ValueError, IndexError):
                    logger.warning(f"Could not parse date from backup file: {backup_file.name}")
            
            if removed_count > 0:
                logger.info(f"Cleanup completed. Removed {removed_count} old backups.")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}", exc_info=True)
            return 0
    
    def get_backup_stats(self) -> dict:
        """
        Get statistics about backups
        
        Returns:
            Dictionary with backup statistics
        """
        try:
            backup_files = list(self.backup_dir.glob("people_os_backup_*.db"))
            total_size = sum(f.stat().st_size for f in backup_files)
            
            return {
                "backup_count": len(backup_files),
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "oldest_backup": min((f.stat().st_mtime for f in backup_files), default=None),
                "newest_backup": max((f.stat().st_mtime for f in backup_files), default=None),
            }
        except Exception as e:
            logger.error(f"Failed to get backup stats: {e}")
            return {}


def schedule_backups():
    """
    Set up scheduled backups using APScheduler
    
    Respects environment configuration:
    - BACKUP_ENABLED (default: true)
    - BACKUP_TIME_UTC (default: 02:00)
    - BACKUP_RETENTION_DAYS (default: 30)
    """
    # Check if backups are enabled
    if os.getenv("BACKUP_ENABLED", "true").lower() != "true":
        logger.info("Backup scheduling disabled (BACKUP_ENABLED=false)")
        return None
    
    try:
        # Parse backup time (format: HH:MM)
        backup_time = os.getenv("BACKUP_TIME_UTC", "02:00")
        hour, minute = map(int, backup_time.split(":"))
        
        # Get retention days
        retention_days = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
        
        # Initialize backup manager
        backup_manager = BackupManager(retention_days=retention_days)
        
        # Create scheduler
        scheduler = BackgroundScheduler(daemon=True)
        
        # Define backup job
        def backup_job():
            """Execute backup and cleanup"""
            logger.info("Starting scheduled database backup...")
            if backup_manager.create_backup():
                removed = backup_manager.cleanup_old_backups()
                stats = backup_manager.get_backup_stats()
                logger.info(f"Backup job completed. Stats: {stats}")
            else:
                logger.error("Backup job failed")
        
        # Schedule daily backup at specified UTC time
        scheduler.add_job(
            backup_job,
            CronTrigger(hour=hour, minute=minute, timezone='UTC'),
            id='database_backup',
            name='Daily Database Backup',
            replace_existing=True
        )
        
        # Start scheduler
        scheduler.start()
        logger.info(f"Backup scheduler started. Daily backup at {backup_time} UTC, retention: {retention_days} days")
        
        return scheduler
        
    except Exception as e:
        logger.error(f"Failed to schedule backups: {e}", exc_info=True)
        return None


def create_manual_backup() -> bool:
    """
    Manually trigger a database backup
    
    Useful for creating backups before major operations
    
    Returns:
        True if backup was successful
    """
    try:
        backup_manager = BackupManager()
        success = backup_manager.create_backup()
        if success:
            backup_manager.cleanup_old_backups()
        return success
    except Exception as e:
        logger.error(f"Manual backup failed: {e}", exc_info=True)
        return False
