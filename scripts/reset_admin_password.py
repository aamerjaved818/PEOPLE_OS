import sqlite3
import bcrypt
import uuid
import datetime
import sys
sys.path.insert(0, '.')
from backend.config import settings

DB_PATH = settings.DB_PATH


def reset_admin():
    print(f"Using database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    users_to_ensure = [
        {"username": "admin", "password": "admin", "role": "SystemAdmin", "email": "admin@people-os.com", "name": "System Administrator"},
        {"username": ".amer", "password": "amer", "role": "Super Admin", "email": "amer@people-os.local", "name": "Amer"},
    ]

    now = datetime.datetime.now().isoformat()

    for u in users_to_ensure:
        username = u["username"]
        password = u["password"]
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Check if user exists
        c.execute("SELECT id FROM core_users WHERE username = ?", (username,))
        row = c.fetchone()

        if row:
            print(f"User '{username}' found. Updating password...")
            c.execute(
                "UPDATE core_users SET password_hash = ?, updated_at = ? "
                "WHERE username = ?",
                (password_hash, now, username)
            )
        else:
            print(f"User '{username}' not found. Creating...")
            user_id = str(uuid.uuid4())
            c.execute("""
                INSERT INTO core_users (
                    id, username, password_hash, role, name, email,
                    is_active, created_at, updated_at, is_system_user
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                username,
                password_hash,
                u.get("role", "User"),
                u.get("name", username),
                u.get("email", ""),
                1,
                now,
                now,
                1,
            ))

        print(f"✅ User '{username}' password is now '{password}'")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    reset_admin()
