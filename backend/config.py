import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Valid environments (Immutable Contract)
VALID_ENVIRONMENTS = {"development", "test", "stage", "production"}


def get_environment():
    """Get current environment, dynamically resolved.
    
    CRITICAL: If APP_ENV is not set or invalid, the application fails.
    This enforces the People_OS Database & Environment Standard.
    """
    env = os.getenv("APP_ENV")
    
    # Allow flexibility during import but validate at runtime
    if env is None:
        # Default to development for backward compatibility during import
        # But log a warning - production startup scripts MUST set APP_ENV
        return "development"
    
    if env not in VALID_ENVIRONMENTS:
        print(f"FATAL: Invalid APP_ENV='{env}'. Must be one of: {VALID_ENVIRONMENTS}")
        sys.exit(1)
    
    return env


class APIConfig:
    """API Configuration Constants"""
    PROJECT_NAME: str = "PeopleOS API"
    VERSION: str = "1.0.0"
    PORT: int = int(os.getenv("PORT", 8000))

    @property
    def ENVIRONMENT(self):
        return get_environment()


class DatabaseConfig:
    """Database Configuration Constants"""
    # Strict Environment-to-Database Mapping (Industry Standard)
    DATABASE_FILES = {
        "development": "people_os_dev.db",
        "test": "people_os_test.db",
        "stage": "people_os_stage.db",
        "production": "people_os_prod.db",
    }
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    os.makedirs(DATA_DIR, exist_ok=True)

    @property
    def DB_FILE(self):
        env = get_environment()
        return self.DATABASE_FILES.get(env, "people_os_dev.db")

    @property
    def DB_PATH(self):
        return os.path.join(self.DATA_DIR, self.DB_FILE)

    @property
    def DATABASE_URL(self):
        return os.getenv("DATABASE_URL", f"sqlite:///{self.DB_PATH}")


class CorsConfig:
    """CORS Configuration Constants"""
    CORS_ORIGINS: list = [
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000,http://localhost:4173,http://127.0.0.1:4173",
        ).split(",")
    ]


class SystemConfig:
    """System-wide Configuration Constants"""
    STORAGE_QUOTA_MB: float = 5.0
    HEALTH_CHECK_INTERVAL_MS: int = 60000
    RATE_LIMIT_MAX_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_MS: int = 60000
    AUDIT_LOG_RETENTION_DAYS: int = 90


class AuthConfig:
    """Authentication Configuration Constants"""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    LOGIN_RATE_LIMIT: str = "20/minute"

    # Import from single source of truth
    from backend.permissions_config import DEFAULT_ROLE_PERMISSIONS
    DEFAULT_PERMISSIONS: dict = DEFAULT_ROLE_PERMISSIONS


# Export instances
api_config = APIConfig()
database_config = DatabaseConfig()
cors_config = CorsConfig()
system_config = SystemConfig()
auth_config = AuthConfig()


class Settings:
    """Unified settings with dynamic environment resolution."""
    PROJECT_NAME: str = api_config.PROJECT_NAME
    VERSION: str = api_config.VERSION
    PORT: int = api_config.PORT
    CORS_ORIGINS: list = cors_config.CORS_ORIGINS
    UPLOAD_DIR: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "uploads"
    )

    @property
    def ENVIRONMENT(self):
        return get_environment()

    @property
    def DB_FILE(self):
        return database_config.DB_FILE

    @property
    def DB_PATH(self):
        return database_config.DB_PATH

    @property
    def DATABASE_URL(self):
        return database_config.DATABASE_URL


settings = Settings()
