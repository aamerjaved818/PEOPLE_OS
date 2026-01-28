from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend import models
import json

def check_db():
    db = SessionLocal()
    try:
        users = db.query(models.DBUser).all()
        print(f"Total Users: {len(users)}")
        for u in users:
            print(f"- {u.username} ({u.role})")
            
        orgs = db.query(models.DBOrganization).all()
        print(f"Total Organizations: {len(orgs)}")
        for o in orgs:
            print(f"- {o.name} ({o.id})")
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
