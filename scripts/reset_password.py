import sqlite3
import bcrypt
import sys
import argparse
from pathlib import Path

def get_password_hash(password):
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")

def reset_password(username, new_password):
    db_path = Path("backend/data/people_os_dev.db")
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return

    db = sqlite3.connect(str(db_path))
    cur = db.cursor()
    
    hashed_password = get_password_hash(new_password)
    
    cur.execute("UPDATE core_users SET password_hash = ? WHERE username = ?", (hashed_password, username))
    
    if cur.rowcount > 0:
        db.commit()
        print(f"Successfully reset password for user '{username}' to '{new_password}'")
    else:
        print(f"User '{username}' not found in database.")
    
    db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    reset_password(args.username, args.password)
