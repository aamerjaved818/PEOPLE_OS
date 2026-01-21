import sqlite3
import bcrypt
import os

DB_PATH = r"backend\data\people_os_dev.db"

def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def promote_admin():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check for 'admin'
        cursor.execute("SELECT id, role, password_hash FROM core_users WHERE username='admin'")
        admin = cursor.fetchone()

        if admin:
            admin_id, current_role, current_pw = admin
            print(f"Found 'admin' (ID: {admin_id}). Current Role: {current_role}")
            
            # Update Role to Super Admin
            new_role = "Super Admin"
            # keeping existing password unless needed, but ensuring role is correct. 
            # User complained about "super_admin_secret", assuming they want their old password or at least the username.
            # I will ONLY update the role to be safe, unless it's missing system flags.
            
            cursor.execute("""
                UPDATE core_users 
                SET role=?, is_system_user=1, updated_at=datetime('now')
                WHERE username='admin'
            """, (new_role,))
            
            if cursor.rowcount > 0:
                print(f"✅ Successfully promoted 'admin' to '{new_role}'.")
            else:
                print("⚠️ Failed to update 'admin'.")
        
        else:
            print("⚠️ User 'admin' not found in DB. It will be seeded by main script if run.")

        # Check for 'super_admin' and remove it if it exists to avoid confusion
        cursor.execute("SELECT id FROM core_users WHERE username='super_admin'")
        super_admin = cursor.fetchone()
        if super_admin:
             print(f"Found duplicate 'super_admin' (ID: {super_admin[0]}). removing...")
             cursor.execute("DELETE FROM core_users WHERE username='super_admin'")
             print("✅ Removed 'super_admin'.")

        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    promote_admin()
