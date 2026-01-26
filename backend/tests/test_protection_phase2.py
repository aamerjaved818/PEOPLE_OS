"""
Tests for Phase 2 Task 4 - API Protection

Tests rate limiting, request validation, and DDoS protection mechanisms.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from fastapi import FastAPI, Request, HTTPException
from starlette.testclient import TestClient

from backend.protection.rate_limiter import (
    RateLimiter,
    RateLimitConfig,
    RateLimitStrategy,
    SlidingWindowLimiter,
    TokenBucketLimiter,
    get_rate_limiter,
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
    IPStats,
    get_ddos_protector,
)


class TestRateLimitConfig:
    """Tests for rate limit configuration"""
    
    def test_config_initialization(self):
        """Test rate limit config creation"""
        config = RateLimitConfig(
            endpoint="/api/test",
            requests_per_minute=60
        )
        assert config.endpoint == "/api/test"
        assert config.requests_per_minute == 60
        assert config.strategy == RateLimitStrategy.SLIDING_WINDOW

    def test_config_with_custom_strategy(self):
        """Test config with custom strategy"""
        config = RateLimitConfig(
            endpoint="/api/test",
            requests_per_minute=30,
            strategy=RateLimitStrategy.TOKEN_BUCKET
        )
        assert config.strategy == RateLimitStrategy.TOKEN_BUCKET

    def test_config_hour_limit_calculation(self):
        """Test automatic hour limit calculation"""
        config = RateLimitConfig(
            endpoint="/api/test",
            requests_per_minute=10
        )
        assert config.requests_per_hour == 600


class TestSlidingWindowLimiter:
    """Tests for sliding window rate limiter"""
    
    def test_sliding_window_allow_request(self):
        """Test allowing request within limit"""
        config = RateLimitConfig(
            endpoint="/api/test",
            requests_per_minute=10
        )
        limiter = SlidingWindowLimiter(config)
        
        allowed, status = limiter.is_allowed("client1")
        assert allowed is True
        assert status.remaining == 9

    def test_sliding_window_exceed_limit(self):
        """Test exceeding rate limit"""
        config = RateLimitConfig(
            endpoint="/api/test",
            requests_per_minute=3
        )
        limiter = SlidingWindowLimiter(config)
        
        # Make 3 allowed requests
        for i in range(3):
            allowed, status = limiter.is_allowed("client1")
            assert allowed is True
        
        # 4th request should be blocked
        allowed, status = limiter.is_allowed("client1")
        assert allowed is False
        assert status.remaining == 0
        assert status.retry_after is not None

    def test_sliding_window_different_clients(self):
        """Test rate limiting per client"""
        config = RateLimitConfig(
            endpoint="/api/test",
            requests_per_minute=2
        )
        limiter = SlidingWindowLimiter(config)
        
        # Client 1: 2 requests
        limiter.is_allowed("client1")
        limiter.is_allowed("client1")
        
        # Client 2: should get fresh limit
        allowed, status = limiter.is_allowed("client2")
        assert allowed is True


class TestTokenBucketLimiter:
    """Tests for token bucket rate limiter"""
    
    def test_token_bucket_initialization(self):
        """Test token bucket initialization"""
        config = RateLimitConfig(
            endpoint="/api/test",
            requests_per_minute=60
        )
        limiter = TokenBucketLimiter(config)
        
        assert limiter.tokens_per_second == 1.0
        assert limiter.burst_size == 60

    def test_token_bucket_allow_request(self):
        """Test allowing request with tokens available"""
        config = RateLimitConfig(
            endpoint="/api/test",
            requests_per_minute=10,
            burst_size=20
        )
        limiter = TokenBucketLimiter(config)
        
        allowed, status = limiter.is_allowed("client1")
        assert allowed is True

    def test_token_bucket_burst_allowed(self):
        """Test burst capacity"""
        config = RateLimitConfig(
            endpoint="/api/test",
            requests_per_minute=10,
            burst_size=20
        )
        limiter = TokenBucketLimiter(config)
        
        # Should allow burst of 20 requests initially
        for i in range(15):
            allowed, status = limiter.is_allowed("client1")
            assert allowed is True


class TestRateLimiter:
    """Tests for main rate limiter"""
    
    def test_rate_limiter_add_endpoint(self):
        """Test adding endpoint configuration"""
        limiter = RateLimiter()
        config = RateLimitConfig(
            endpoint="/api/test",
            requests_per_minute=60
        )
        limiter.add_endpoint(config)
        
        assert "/api/test" in limiter.configs

    def test_rate_limiter_check_endpoint(self):
        """Test checking rate limit for endpoint"""
        limiter = RateLimiter()
        config = RateLimitConfig(
            endpoint="/api/test",
            requests_per_minute=5
        )
        limiter.add_endpoint(config)
        
        allowed, status = limiter.is_allowed("client1", "/api/test")
        assert allowed is True

    def test_rate_limiter_unconfigured_endpoint(self):
        """Test checking unconfigured endpoint (should allow)"""
        limiter = RateLimiter()
        
        allowed, status = limiter.is_allowed("client1", "/api/unknown")
        assert allowed is True

    def test_rate_limiter_reset_client(self):
        """Test resetting rate limit for client"""
        limiter = RateLimiter()
        config = RateLimitConfig(
            endpoint="/api/test",
            requests_per_minute=2
        )
        limiter.add_endpoint(config)
        
        # Exhaust limit
        limiter.is_allowed("client1", "/api/test")
        limiter.is_allowed("client1", "/api/test")
        allowed, _ = limiter.is_allowed("client1", "/api/test")
        assert allowed is False
        
        # Reset
        limiter.reset_client("client1", "/api/test")
        allowed, _ = limiter.is_allowed("client1", "/api/test")
        assert allowed is True


class TestRequestValidationConfig:
    """Tests for request validation configuration"""
    
    def test_default_config(self):
        """Test default validation config"""
        config = RequestValidationConfig()
        assert config.max_body_size == 10 * 1024 * 1024
        assert config.max_header_size == 8192
        assert config.require_content_type is True

    def test_custom_config(self):
        """Test custom validation config"""
        config = RequestValidationConfig(
            max_body_size=5 * 1024 * 1024,
            max_header_size=4096,
            require_content_type=False
        )
        assert config.max_body_size == 5 * 1024 * 1024
        assert config.require_content_type is False


class TestPayloadValidator:
    """Tests for payload validation"""
    
    def test_validate_required_fields_success(self):
        """Test successful required field validation"""
        data = {"name": "John", "email": "john@example.com"}
        valid, error = PayloadValidator.validate_required_fields(
            data,
            ["name", "email"]
        )
        assert valid is True
        assert error is None

    def test_validate_required_fields_missing(self):
        """Test missing required field validation"""
        data = {"name": "John"}
        valid, error = PayloadValidator.validate_required_fields(
            data,
            ["name", "email"]
        )
        assert valid is False
        assert "email" in error

    def test_validate_field_types_success(self):
        """Test successful type validation"""
        data = {"age": 30, "name": "John"}
        valid, error = PayloadValidator.validate_field_types(
            data,
            {"age": int, "name": str}
        )
        assert valid is True

    def test_validate_field_types_failure(self):
        """Test type validation failure"""
        data = {"age": "thirty", "name": "John"}
        valid, error = PayloadValidator.validate_field_types(
            data,
            {"age": int}
        )
        assert valid is False
        assert "age" in error

    def test_validate_field_values_success(self):
        """Test successful value validation"""
        data = {"email": "test@example.com"}
        valid, error = PayloadValidator.validate_field_values(
            data,
            {"email": lambda x: "@" in x}
        )
        assert valid is True

    def test_validate_field_values_failure(self):
        """Test value validation failure"""
        data = {"email": "invalid-email"}
        valid, error = PayloadValidator.validate_field_values(
            data,
            {"email": lambda x: "@" in x}
        )
        assert valid is False


class TestInputSanitizer:
    """Tests for input sanitization"""
    
    def test_sanitize_string_removes_nulls(self):
        """Test null byte removal"""
        result = InputSanitizer.sanitize_string("hello\x00world")
        assert result == "helloworld"

    def test_sanitize_string_trims_whitespace(self):
        """Test whitespace trimming"""
        result = InputSanitizer.sanitize_string("  hello  ")
        assert result == "hello"

    def test_sanitize_string_max_length(self):
        """Test maximum length enforcement"""
        result = InputSanitizer.sanitize_string("hello world", max_length=5)
        assert result == "hello"

    def test_sanitize_dict(self):
        """Test dictionary sanitization"""
        data = {
            "name": "  John  ",
            "email": "test@example.com\x00"
        }
        result = InputSanitizer.sanitize_dict(data)
        assert result["name"] == "John"
        assert result["email"] == "test@example.com"

    def test_detect_sql_injection(self):
        """Test SQL injection detection"""
        payloads = [
            "'; DROP TABLE users;--",
            "' OR '1'='1",
            "UNION SELECT * FROM admin"
        ]
        
        for payload in payloads:
            assert InputSanitizer.detect_injection_attempts(payload) is True

    def test_detect_script_injection(self):
        """Test script injection detection"""
        payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "onclick=alert('xss')"
        ]
        
        for payload in payloads:
            assert InputSanitizer.detect_injection_attempts(payload) is True


class TestDDoSProtector:
    """Tests for DDoS protection"""
    
    def test_ddos_config_initialization(self):
        """Test DDoS config creation"""
        config = DDoSConfig(
            max_requests_per_ip_per_minute=100
        )
        assert config.max_requests_per_ip_per_minute == 100

    def test_ip_stats_creation(self):
        """Test IP stats tracking"""
        stats = IPStats(ip_address="192.168.1.1")
        assert stats.ip_address == "192.168.1.1"
        assert stats.request_count == 0

    def test_ddos_check_ip_safe(self):
        """Test checking safe IP"""
        protector = DDoSProtector()
        allowed, threat_level, message = protector.check_ip("192.168.1.1")
        assert allowed is True
        assert threat_level == ThreatLevel.SAFE

    def test_ddos_record_request(self):
        """Test recording normal request"""
        protector = DDoSProtector()
        protector.record_request("192.168.1.1")
        
        stats = protector.get_stats("192.168.1.1")
        assert stats.request_count == 1

    def test_ddos_record_error(self):
        """Test recording error"""
        protector = DDoSProtector()
        protector.record_error("192.168.1.1")
        
        stats = protector.get_stats("192.168.1.1")
        assert stats.error_count == 1

    def test_ddos_block_ip(self):
        """Test IP blocking"""
        protector = DDoSProtector()
        
        # Generate many blocked requests
        for i in range(60):
            protector.record_blocked_request("192.168.1.1")
        
        allowed, threat_level, _ = protector.check_ip("192.168.1.1")
        assert allowed is False
        assert threat_level == ThreatLevel.CRITICAL

    def test_ddos_permanent_blacklist(self):
        """Test permanent blacklisting"""
        protector = DDoSProtector()
        protector.blacklist_ip("192.168.1.1")
        
        allowed, threat_level, _ = protector.check_ip("192.168.1.1")
        assert allowed is False

    def test_ddos_whitelist_ip(self):
        """Test IP whitelisting"""
        protector = DDoSProtector()
        protector.record_request("192.168.1.1")
        protector.whitelist_ip("192.168.1.1")
        
        stats = protector.get_stats("192.168.1.1")
        assert stats is None

    def test_ddos_threat_summary(self):
        """Test threat level summary"""
        protector = DDoSProtector()
        
        protector.record_request("192.168.1.1")
        protector.record_request("192.168.1.2")
        protector.record_request("192.168.1.3")
        
        summary = protector.get_threat_summary()
        assert summary["safe"] == 3

    def test_ddos_error_rate_escalation(self):
        """Test threat escalation on high error rate"""
        config = DDoSConfig(
            error_rate_threshold=0.5,
            error_count_threshold=10
        )
        protector = DDoSProtector(config)
        
        # Generate 60% error rate
        for i in range(100):
            protector.record_request("192.168.1.1")
        for i in range(70):
            protector.record_error("192.168.1.1")
        
        stats = protector.get_stats("192.168.1.1")
        assert stats.threat_level != ThreatLevel.SAFE


class TestRateLimiterIntegration:
    """Integration tests for rate limiting"""
    
    def test_multiple_endpoints(self):
        """Test rate limiting across multiple endpoints"""
        limiter = RateLimiter()
        
        limiter.add_endpoint(RateLimitConfig(
            endpoint="/api/employees",
            requests_per_minute=10
        ))
        limiter.add_endpoint(RateLimitConfig(
            endpoint="/api/departments",
            requests_per_minute=20
        ))
        
        # Each endpoint has independent limits
        for i in range(10):
            allowed, _ = limiter.is_allowed("client1", "/api/employees")
            assert allowed is True
        
        allowed, _ = limiter.is_allowed("client1", "/api/employees")
        assert allowed is False
        
        # But other endpoint should still work
        for i in range(10):
            allowed, _ = limiter.is_allowed("client1", "/api/departments")
            assert allowed is True

    def test_rate_limiter_concurrent_access(self):
        """Test thread safety"""
        import concurrent.futures
        limiter = RateLimiter()
        limiter.add_endpoint(RateLimitConfig(
            endpoint="/api/test",
            requests_per_minute=1000
        ))
        
        def make_request():
            limiter.is_allowed(f"client_{threading.current_thread().ident}", "/api/test")
        
        import threading
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            for f in concurrent.futures.as_completed(futures):
                f.result()


class TestDDoSIntegration:
    """Integration tests for DDoS protection"""
    
    def test_ddos_escalation_chain(self):
        """Test threat level escalation"""
        config = DDoSConfig(
            max_requests_per_ip_per_minute=50,
            error_rate_threshold=0.3
        )
        protector = DDoSProtector(config)
        
        # Simulate attack progression
        for i in range(100):
            protector.record_request("192.168.1.1")
            if i % 3 == 0:
                protector.record_error("192.168.1.1")
        
        stats = protector.get_stats("192.168.1.1")
        assert stats.threat_level in [ThreatLevel.SUSPICIOUS, ThreatLevel.WARNING, ThreatLevel.CRITICAL]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
