from cryptography.fernet import Fernet
from src.helpers.config import get_Settings

class EncryptionService:
    _fernet = None

    @classmethod
    def _get_fernet(cls):
        if cls._fernet is None:
            settings = get_Settings()
            if not settings.ENCRYPTION_KEY:
                raise ValueError("ENCRYPTION_KEY is not set in configuration")
            cls._fernet = Fernet(settings.ENCRYPTION_KEY)
        return cls._fernet

    @classmethod
    def encrypt(cls, data: str) -> str:
        """Encrypts a string."""
        if not data:
            return data
        f = cls._get_fernet()
        return f.encrypt(data.encode()).decode()

    @classmethod
    def decrypt(cls, data: str) -> str:
        """Decrypts a string."""
        if not data:
            return data
        f = cls._get_fernet()
        return f.decrypt(data.encode()).decode()
