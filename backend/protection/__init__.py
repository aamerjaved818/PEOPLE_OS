"""
peopleOS eBusiness Suite Protection Module

Comprehensive API protection including rate limiting, request validation, and DDoS protection.
"""

from backend.protection.rate_limiter import (
    RateLimiter,
    RateLimitConfig,
    RateLimitStrategy,
    get_rate_limiter,
    initialize_rate_limiter,
)

from backend.protection.request_validator import (
    RequestValidator,
    RequestValidationConfig,
    RequestValidationMiddleware,
    PayloadValidator,
    InputSanitizer,
)

from backend.protection.ddos_protection import (
    DDoSProtector,
    DDoSConfig,
    ThreatLevel,
    get_ddos_protector,
    initialize_ddos_protection,
)

__all__ = [
    "RateLimiter",
    "RateLimitConfig",
    "RateLimitStrategy",
    "get_rate_limiter",
    "initialize_rate_limiter",
    "RequestValidator",
    "RequestValidationConfig",
    "RequestValidationMiddleware",
    "PayloadValidator",
    "InputSanitizer",
    "DDoSProtector",
    "DDoSConfig",
    "ThreatLevel",
    "get_ddos_protector",
    "initialize_ddos_protection",
]
