import os
import sys
from sqlalchemy import text

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_engine
from backend.domains.hcm import models as hcm_models
from backend.domains.gen_admin import models as gen_admin_models

def sync_schema():
    engine = get_engine()
    print(f"Syncing schema for {engine.url}...")
    
    with engine.connect() as conn:
        print("Dropping hcm_attendance to force recreation...")
        conn.execute(text("DROP TABLE IF EXISTS hcm_attendance"))
        conn.execute(text("DROP TABLE IF EXISTS hcm_overtime_requests")) # Just in case it's half-baked
        conn.commit()
    
    print("Re-creating all tables from metadata...")
    hcm_models.Base.metadata.create_all(bind=engine)
    print("Schema sync complete.")

if __name__ == "__main__":
    sync_schema()
