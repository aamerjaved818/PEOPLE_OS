import os
import sys
from typing import List, Dict, Optional, Any, Union
from pydantic import field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env file
load_dotenv()

# Valid environments
VALID_ENVIRONMENTS = {"development", "test", "stage", "production"}

class Settings(BaseSettings):
    """
    Unified Configuration for PEOPLE_OS.
    Uses Pydantic BaseSettings for validation and type casting.
    """
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    # --- Core Application Settings ---
    APP_ENV: str = "development"
    PROJECT_NAME: str = "peopleOS eBusiness Suite"
    
    # Read version from root VERSION file
    try:
        _version_path = Path(__file__).resolve().parent.parent / "VERSION"
        VERSION: str = _version_path.read_text().strip()
    except Exception:
        VERSION: str = "1.0.0" # Fallback
        
    API_HOST: str = "0.0.0.0"
    API_PORT: int = Field(8000, alias="PORT_API")
    
    # --- Paths ---
    BASE_DIR: Path = Path(__file__).resolve().parent
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    REPORTS_DIR: Path = BASE_DIR.parent / "reports"

    # --- Database Settings ---
    # Default to SQLite for simplicity if not set
    DATABASE_URL: Optional[str] = None
    
    # --- Security & Auth ---
    SECRET_KEY: str = Field("CHANGE_ME_IN_PRODUCTION", alias="JWT_SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: Any = [
        "http://localhost:5000", 
        "http://localhost:8000",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:8000"
    ]
    ALLOWED_HOSTS: Any = ["*"]
    
    @field_validator("CORS_ORIGINS", "ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_list(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v
    
    # --- Celery / Redis ---
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_URL: str = "redis://localhost:6379/1"

    # --- System Limits ---
    STORAGE_QUOTA_MB: float = 5.0
    RATE_LIMIT_MAX_REQUESTS: int = 100
    AUDIT_LOG_RETENTION_DAYS: int = 90
    LOGIN_RATE_LIMIT: str = "20/minute"
    
    # --- Feature Flags ---
    ENABLE_AI_FEATURES: bool = True
    ENABLE_ANALYTICS: bool = False

    # --- Monitoring ---
    PROMETHEUS_ENABLED: bool = False
    SENTRY_DSN: Optional[str] = None
    
    @property
    def ENVIRONMENT(self) -> str:
        """Alias for APP_ENV for backward compatibility"""
        return self.APP_ENV

    @property
    def PORT(self) -> int:
        """Alias for API_PORT for backward compatibility"""
        return self.API_PORT
    
    def model_post_init(self, __context: Any) -> None:
        """Runtime validation and directory creation"""
        # Validate APP_ENV
        if self.APP_ENV not in VALID_ENVIRONMENTS:
            print(f"FATAL: Invalid APP_ENV='{self.APP_ENV}'. Must be one of: {VALID_ENVIRONMENTS}")
            sys.exit(1)
            
        # Create directories
        self.DATA_DIR.mkdir(exist_ok=True)
        self.UPLOAD_DIR.mkdir(exist_ok=True)
        self.REPORTS_DIR.mkdir(exist_ok=True)
        
        # Resolve Database URL dynamically if not set
        if not self.DATABASE_URL:
            db_file = f"people_os_{self.APP_ENV}.db"
            if self.APP_ENV == "development":
                db_file = "people_os_dev.db" # Legacy support
            
            db_path = self.DATA_DIR / db_file
            self.DATABASE_URL = f"sqlite:///{db_path}"

# Initialize single settings instance
settings = Settings()

# Backwards Compatibility Aliases
# These are strictly for migration purposes and should be phased out
class APIConfig:
    PROJECT_NAME = settings.PROJECT_NAME
    VERSION = settings.VERSION
    PORT = settings.API_PORT
    ENVIRONMENT = settings.APP_ENV

class DatabaseConfig:
    DATABASE_URL = settings.DATABASE_URL
    
class CorsConfig:
    CORS_ORIGINS = settings.CORS_ORIGINS

class AuthConfig:
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    LOGIN_RATE_LIMIT = settings.LOGIN_RATE_LIMIT
    # Import here to avoid circular dependency in main logic if needed
    # But for config we try to keep it simple. 
    # The original file imported DEFAULT_ROLE_PERMISSIONS.
    try:
        from backend.permissions_config import DEFAULT_ROLE_PERMISSIONS
        DEFAULT_PERMISSIONS = DEFAULT_ROLE_PERMISSIONS
    except ImportError:
        DEFAULT_PERMISSIONS = {}

class SystemConfig:
    STORAGE_QUOTA_MB = settings.STORAGE_QUOTA_MB
    AUDIT_LOG_RETENTION_DAYS = settings.AUDIT_LOG_RETENTION_DAYS

# Instantiate for legacy imports
api_config = APIConfig()
database_config = DatabaseConfig()
cors_config = CorsConfig()
auth_config = AuthConfig()
system_config = SystemConfig()
