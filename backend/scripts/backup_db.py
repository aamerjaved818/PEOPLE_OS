import shutil
import os
import time
from pathlib import Path
from datetime import datetime

def run_backup():
    # Load config
    # In a real app we'd import settings, but for this standalone script we use env or defaults
    db_path = os.getenv("DATABASE_URL", "backend/data/people_os.db")
    if "sqlite:///" in db_path:
        db_path = db_path.replace("sqlite:///", "")
    
    source = Path(db_path)
    if not source.exists():
        # Try relative paths from script location
        source = Path(__file__).parent.parent / "data" / "people_os.db"

    if not source.exists():
        print(f"❌ Source database not found at {source}")
        return

    # Backup directory
    backup_dir = source.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = backup_dir / f"people_os_backup_{timestamp}.db"

    try:
        shutil.copy2(source, destination)
        print(f"✅ Database backed up to: {destination}")
        
        # Cleanup old backups (keep last 7)
        backups = sorted(list(backup_dir.glob("*.db")), key=os.path.getmtime)
        if len(backups) > 7:
            for old_backup in backups[:-7]:
                old_backup.unlink()
                print(f"🗑️ Cleaned up old backup: {old_backup.name}")
                
    except Exception as e:
        print(f"❌ Backup failed: {e}")

if __name__ == "__main__":
    run_backup()
