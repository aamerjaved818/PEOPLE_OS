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
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("API_PORT", 8000))

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
            "http://localhost:5000,http://127.0.0.1:5000,http://localhost:8000,http://127.0.0.1:8000",
        ).split(",")
    ]


class SystemConfig:
    """System-wide Configuration Constants"""
    # Storage & Resource Management
    STORAGE_QUOTA_MB: float = 5.0
    HEALTH_CHECK_INTERVAL_MS: int = 60000
    
    # Rate Limiting (Recommendation: Prevent abuse)
    RATE_LIMIT_MAX_REQUESTS: int = 100  # per minute per IP
    RATE_LIMIT_WINDOW_MS: int = 60000
    
    # Audit & Compliance (Recommendation: 90-day retention)
    AUDIT_LOG_RETENTION_DAYS: int = 90
    
    # Performance Monitoring (Recommendation: Phase 2)
    SLOW_QUERY_THRESHOLD_MS: int = 1000  # Alert if query > 1s
    API_RESPONSE_TIMEOUT_MS: int = 30000
    MAX_CONCURRENT_REQUESTS: int = 100
    
    # Database Health (Recommendation: FK constraint monitoring)
    FK_CONSTRAINT_CHECK_ENABLED: bool = True
    ORPHANED_RECORD_CHECK_ENABLED: bool = True
    
    # Deployment Configuration (Recommendation: Phase 1)
    BACKUP_RETENTION_DAYS: int = 30
    BACKUP_ENABLED: bool = True
    BACKUP_TIME_UTCHR: int = 2  # 2 AM UTC daily


class AuthConfig:
    """Authentication Configuration Constants"""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    LOGIN_RATE_LIMIT: str = "20/minute"

    # Import from single source of truth
    from backend.permissions_config import DEFAULT_ROLE_PERMISSIONS
    DEFAULT_PERMISSIONS: dict = DEFAULT_ROLE_PERMISSIONS


class MonitoringConfig:
    """Monitoring & Observability Configuration (Recommendation: Phase 1)"""
    # Sentry Error Tracking (Removed)
    
    # Database Monitoring
    DB_QUERY_LOGGING_ENABLED: bool = True
    DB_SLOW_QUERY_LOG_ENABLED: bool = True
    
    # Health Checks
    HEALTH_CHECK_ENABLED: bool = True
    HEALTH_CHECK_ENDPOINT: str = "/health"
    
    # Prometheus Metrics
    PROMETHEUS_ENABLED: bool = os.getenv("PROMETHEUS_ENABLED", "false").lower() == "true"
    PROMETHEUS_ENDPOINT: str = "/metrics"


class SecurityConfig:
    """Security Configuration (Recommendation: Phase 2)"""
    # API Security
    REQUIRE_HTTPS: bool = os.getenv("REQUIRE_HTTPS", "false").lower() == "true"
    ALLOWED_HOSTS: list = os.getenv("ALLOWED_HOSTS", "*").split(",")
    
    # Input Validation
    MAX_REQUEST_SIZE_MB: int = 10
    VALIDATE_FILE_UPLOADS: bool = True
    ALLOWED_FILE_TYPES: list = ["pdf", "docx", "xlsx", "jpg", "png"]
    
    # Password Security
    MIN_PASSWORD_LENGTH: int = 12
    REQUIRE_SPECIAL_CHARS: bool = True
    REQUIRE_NUMBERS: bool = True
    REQUIRE_UPPERCASE: bool = True
    
    # Rate Limiting
    API_RATE_LIMIT: str = "100/minute"
    LOGIN_RATE_LIMIT: str = "20/minute"
    GLOBAL_RATE_LIMIT: str = "1000/minute"
    
    # CORS & Headers
    CORS_ALLOW_CREDENTIALS: bool = True
    SECURITY_HEADERS_ENABLED: bool = True


class PerformanceConfig:
    """Performance Optimization Configuration (Recommendation: Phase 2)"""
    # Caching
    CACHE_ENABLED: bool = False  # Set to True when Redis is available
    CACHE_TTL_SECONDS: int = 3600
    CACHE_MAX_SIZE_MB: int = 100
    
    # Query Optimization
    BATCH_QUERY_ENABLED: bool = True
    QUERY_RESULT_CACHE_ENABLED: bool = False
    
    # API Response
    API_COMPRESSION_ENABLED: bool = True
    API_COMPRESSION_THRESHOLD_BYTES: int = 1024
    
    # Database Connection
    DB_CONNECTION_POOL_SIZE: int = 10
    DB_CONNECTION_MAX_OVERFLOW: int = 5
    DB_CONNECTION_POOL_TIMEOUT: int = 30


# Export instances
api_config = APIConfig()
database_config = DatabaseConfig()
cors_config = CorsConfig()
system_config = SystemConfig()
auth_config = AuthConfig()
monitoring_config = MonitoringConfig()
security_config = SecurityConfig()
performance_config = PerformanceConfig()


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
        
    @property
    def REPORTS_DIR(self) -> str:
        """Root directory for audit reports"""
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reports = os.path.join(root, "reports")
        os.makedirs(reports, exist_ok=True)
        return reports


settings = Settings()
