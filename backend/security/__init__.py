"""
Security module for peopleOS eBusiness Suite

Provides OAuth2/JWT authentication, RBAC, audit logging, encryption, and security scanning.
"""

from .oauth2 import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    TokenData,
)
from .rbac import (
    Role,
    Permission,
    get_user_roles,
    check_permission,
    require_permission,
    RBACManager,
)
from .audit_logger import AuditLogger
from .encryption import EncryptionManager
from .security_scanner import (
    SecurityScanner,
    get_security_scanner,
    Vulnerability,
    VulnerabilityLevel,
    VulnerabilityType,
)
from .bandit_analyzer import (
    BanditAnalyzer,
    get_bandit_analyzer,
    BanditIssue,
    BanditSeverity,
)
from .semgrep_analyzer import (
    SemgrepAnalyzer,
    get_semgrep_analyzer,
    SemgrepMatch,
    SemgrepSeverity,
)
from .security_report import (
    SecurityReport,
    get_security_report,
    SecurityMetrics,
    ReportFormat,
)

__all__ = [
    # OAuth2/JWT
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "get_current_user",
    "TokenData",
    # RBAC
    "Role",
    "Permission",
    "get_user_roles",
    "check_permission",
    "require_permission",
    "RBACManager",
    # Audit Logging
    "AuditLogger",
    # Encryption
    "EncryptionManager",
    # Security Scanning
    "SecurityScanner",
    "get_security_scanner",
    "Vulnerability",
    "VulnerabilityLevel",
    "VulnerabilityType",
    # Bandit Analysis
    "BanditAnalyzer",
    "get_bandit_analyzer",
    "BanditIssue",
    "BanditSeverity",
    # Semgrep Analysis
    "SemgrepAnalyzer",
    "get_semgrep_analyzer",
    "SemgrepMatch",
    "SemgrepSeverity",
    # Security Reports
    "SecurityReport",
    "get_security_report",
    "SecurityMetrics",
    "ReportFormat",
]
