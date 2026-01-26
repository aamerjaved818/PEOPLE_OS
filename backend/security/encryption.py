"""
Data encryption module for peopleOS eBusiness Suite

Provides field-level encryption for sensitive data.
"""

import os
from typing import Any, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionManager:
    """Manages encryption and decryption of sensitive fields"""

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption manager.

        Args:
            encryption_key: Base encryption key (if None, uses env variable)
        """
        if encryption_key is None:
            encryption_key = os.getenv("ENCRYPTION_KEY", "default-key-change-in-production")

        # Derive key from master key
        self.key = self._derive_key(encryption_key)
        self.cipher = Fernet(self.key)

    @staticmethod
    def _derive_key(master_key: str, salt: bytes = b"PeopleOS_Salt_001") -> bytes:
        """
        Derive encryption key from master key.

        Args:
            master_key: Base encryption key
            salt: Salt for key derivation

        Returns:
            Fernet-compatible key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(master_key.encode())

        # Convert to Fernet-compatible key (base64)
        import base64

        return base64.urlsafe_b64encode(key)

    def encrypt(self, value: Any) -> str:
        """
        Encrypt a value.

        Args:
            value: Value to encrypt (will be converted to string)

        Returns:
            Encrypted value as string
        """
        if value is None:
            return None

        # Convert to string if needed
        if not isinstance(value, str):
            value = str(value)

        encrypted = self.cipher.encrypt(value.encode())
        return encrypted.decode()

    def decrypt(self, encrypted_value: str) -> str:
        """
        Decrypt a value.

        Args:
            encrypted_value: Encrypted value string

        Returns:
            Decrypted value as string
        """
        if encrypted_value is None:
            return None

        try:
            decrypted = self.cipher.decrypt(encrypted_value.encode())
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt value: {e}")

    @staticmethod
    def generate_key() -> str:
        """
        Generate a new encryption key.

        Returns:
            Base64-encoded Fernet key
        """
        key = Fernet.generate_key()
        return key.decode()


# Global encryption manager instance
_encryption_manager: Optional[EncryptionManager] = None


def get_encryption_manager() -> EncryptionManager:
    """Get global encryption manager instance"""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager


def encrypt_field(value: Any) -> str:
    """Encrypt a field value"""
    manager = get_encryption_manager()
    return manager.encrypt(value)


def decrypt_field(encrypted_value: str) -> str:
    """Decrypt a field value"""
    manager = get_encryption_manager()
    return manager.decrypt(encrypted_value)


class EncryptedString:
    """Descriptor for encrypted string fields in SQLAlchemy models"""

    def __init__(self, attr_name: str):
        self.attr_name = attr_name
        self.encrypted_attr_name = f"_{attr_name}_encrypted"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        encrypted_value = getattr(obj, self.encrypted_attr_name, None)
        if encrypted_value is None:
            return None
        return decrypt_field(encrypted_value)

    def __set__(self, obj, value):
        if value is None:
            encrypted_value = None
        else:
            encrypted_value = encrypt_field(value)
        setattr(obj, self.encrypted_attr_name, encrypted_value)
