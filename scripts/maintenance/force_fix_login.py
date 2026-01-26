
from backend.database import SessionLocal
from backend.domains.core.models import DBUser
from backend.dependencies import get_password_hash, verify_password
from sqlalchemy import func

def force_fix_user():
    db = SessionLocal()
    try:
        username_to_fix = "people01"
        print(f"--- Investigating user: {username_to_fix} ---")
        
        # Find user case-insensitively
        user = db.query(DBUser).filter(func.lower(DBUser.username) == username_to_fix.lower()).first()
        
        if not user:
            print(f"ERROR: User '{username_to_fix}' NOT FOUND in database.")
            # Check all users to see if there's a typo
            all_users = db.query(DBUser).all()
            print(f"Total users in DB: {len(all_users)}")
            for u in all_users:
                print(f"  - {u.username} (Role: {u.role}, Active: {u.is_active})")
            return

        print(f"FOUND USER: {user.username}")
        print(f"Current Status: Role={user.role}, IsActive={user.is_active}, OrgID={user.organization_id}")
        
        # Force Reset
        new_password = "people01"
        new_hash = get_password_hash(new_password)
        user.password_hash = new_hash
        user.is_active = True # Ensure active
        
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"SUCCESS: Password for '{user.username}' reset to '{new_password}'.")
        
        # Self-Verification
        print("\n--- Running Internal Verification ---")
        is_verified = verify_password(new_password, user.password_hash)
        print(f"Verification of new hash: {'SUCCESS' if is_verified else 'FAILURE'}")
        
        # Check if uvicorn router logic will match
        match = db.query(DBUser).filter(func.lower(DBUser.username) == username_to_fix.lower()).first()
        print(f"Case-insensitive query match: {'SUCCESS' if match and match.id == user.id else 'FAILURE'}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    force_fix_user()
