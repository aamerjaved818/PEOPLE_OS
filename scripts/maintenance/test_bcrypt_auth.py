
import bcrypt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")

def verify_password(plain_password, hashed_password):
    try:
        # Support both passlib hashes and raw bcrypt
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode("utf-8")
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)
    except Exception as e:
        print(f"Bcrypt check failed: {e}")
        # Fallback to passlib if bcrypt fails (e.g. unknown format)
        return pwd_context.verify(plain_password, hashed_password)

# TEST
password = "securepassword123"
hashed = get_password_hash(password)
print(f"Hashed: {hashed}")

result = verify_password(password, hashed)
print(f"Verification Result: {result}")

if result:
    print("SUCCESS: Password logic is correct.")
else:
    print("FAILURE: Password logic is incorrect.")
