"""
Rate limiting and request throttling for peopleOS eBusiness Suite API

Implements per-endpoint rate limiting with sliding window and token bucket algorithms.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
import threading
from collections import defaultdict


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies"""
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    FIXED_WINDOW = "fixed_window"


@dataclass
class RateLimitConfig:
    """Rate limit configuration for an endpoint"""
    endpoint: str
    requests_per_minute: int
    requests_per_hour: int = None
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    burst_size: Optional[int] = None
    
    def __post_init__(self):
        if self.requests_per_hour is None:
            self.requests_per_hour = self.requests_per_minute * 60


@dataclass
class RateLimitStatus:
    """Current rate limit status"""
    allowed: bool
    remaining: int
    reset_time: datetime
    retry_after: Optional[int] = None
    limit: int = 0


@dataclass
class RequestRecord:
    """Record of a request for rate limiting"""
    timestamp: datetime
    client_id: str
    endpoint: str
    
    
class SlidingWindowLimiter:
    """Sliding window rate limiter"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = threading.RLock()
    
    def is_allowed(self, client_id: str) -> Tuple[bool, RateLimitStatus]:
        """Check if request is allowed"""
        with self.lock:
            now = datetime.utcnow()
            minute_ago = now - timedelta(minutes=1)
            hour_ago = now - timedelta(hours=1)
            
            # Clean old requests
            key = f"{client_id}:{self.config.endpoint}"
            self.requests[key] = [
                req for req in self.requests[key]
                if req > hour_ago
            ]
            
            # Check minute limit
            minute_requests = [
                req for req in self.requests[key]
                if req > minute_ago
            ]
            
            if len(minute_requests) >= self.config.requests_per_minute:
                # Limit exceeded
                reset_time = minute_requests[0] + timedelta(minutes=1)
                retry_after = int((reset_time - now).total_seconds())
                return False, RateLimitStatus(
                    allowed=False,
                    remaining=0,
                    reset_time=reset_time,
                    retry_after=retry_after,
                    limit=self.config.requests_per_minute
                )
            
            # Check hour limit
            hour_requests = [
                req for req in self.requests[key]
                if req > hour_ago
            ]
            
            if len(hour_requests) >= self.config.requests_per_hour:
                reset_time = hour_requests[0] + timedelta(hours=1)
                retry_after = int((reset_time - now).total_seconds())
                return False, RateLimitStatus(
                    allowed=False,
                    remaining=0,
                    reset_time=reset_time,
                    retry_after=retry_after,
                    limit=self.config.requests_per_hour
                )
            
            # Request allowed
            self.requests[key].append(now)
            remaining = self.config.requests_per_minute - len(minute_requests) - 1
            reset_time = now + timedelta(minutes=1)
            
            return True, RateLimitStatus(
                allowed=True,
                remaining=remaining,
                reset_time=reset_time,
                limit=self.config.requests_per_minute
            )


class TokenBucketLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.buckets: Dict[str, Tuple[float, datetime]] = {}
        self.lock = threading.RLock()
        
        # Calculate tokens per second
        self.tokens_per_second = config.requests_per_minute / 60.0
        self.burst_size = config.burst_size or config.requests_per_minute
    
    def is_allowed(self, client_id: str, tokens_needed: int = 1) -> Tuple[bool, RateLimitStatus]:
        """Check if request is allowed"""
        with self.lock:
            now = datetime.utcnow()
            key = f"{client_id}:{self.config.endpoint}"
            
            # Initialize bucket
            if key not in self.buckets:
                self.buckets[key] = (float(self.burst_size), now)
            
            tokens, last_update = self.buckets[key]
            
            # Add tokens based on time elapsed
            elapsed = (now - last_update).total_seconds()
            tokens = min(
                self.burst_size,
                tokens + (elapsed * self.tokens_per_second)
            )
            
            # Check if enough tokens
            if tokens >= tokens_needed:
                tokens -= tokens_needed
                self.buckets[key] = (tokens, now)
                
                remaining = int(tokens)
                reset_time = now + timedelta(seconds=tokens_needed / self.tokens_per_second)
                
                return True, RateLimitStatus(
                    allowed=True,
                    remaining=remaining,
                    reset_time=reset_time,
                    limit=self.config.requests_per_minute
                )
            else:
                # Not enough tokens
                refill_time = (tokens_needed - tokens) / self.tokens_per_second
                reset_time = now + timedelta(seconds=refill_time)
                retry_after = int(refill_time)
                
                return False, RateLimitStatus(
                    allowed=False,
                    remaining=0,
                    reset_time=reset_time,
                    retry_after=retry_after,
                    limit=self.config.requests_per_minute
                )


class RateLimiter:
    """Main rate limiter managing multiple endpoints"""
    
    def __init__(self):
        self.limiters: Dict[str, tuple] = {}
        self.configs: Dict[str, RateLimitConfig] = {}
        self.lock = threading.RLock()
    
    def add_endpoint(self, config: RateLimitConfig):
        """Add endpoint configuration"""
        with self.lock:
            self.configs[config.endpoint] = config
            
            if config.strategy == RateLimitStrategy.SLIDING_WINDOW:
                limiter = SlidingWindowLimiter(config)
            elif config.strategy == RateLimitStrategy.TOKEN_BUCKET:
                limiter = TokenBucketLimiter(config)
            else:
                limiter = SlidingWindowLimiter(config)
            
            self.limiters[config.endpoint] = (limiter, config)
    
    def is_allowed(self, client_id: str, endpoint: str) -> Tuple[bool, RateLimitStatus]:
        """Check if request is allowed for endpoint"""
        if endpoint not in self.limiters:
            # No limit configured
            return True, RateLimitStatus(
                allowed=True,
                remaining=-1,
                reset_time=datetime.utcnow() + timedelta(hours=1),
                limit=-1
            )
        
        limiter, config = self.limiters[endpoint]
        return limiter.is_allowed(client_id)
    
    def get_status(self, client_id: str, endpoint: str) -> RateLimitStatus:
        """Get current rate limit status"""
        if endpoint not in self.limiters:
            return RateLimitStatus(
                allowed=True,
                remaining=-1,
                reset_time=datetime.utcnow() + timedelta(hours=1),
                limit=-1
            )
        
        limiter, config = self.limiters[endpoint]
        allowed, status = limiter.is_allowed(client_id)
        return status
    
    def reset_client(self, client_id: str, endpoint: Optional[str] = None):
        """Reset rate limit for client"""
        with self.lock:
            if endpoint:
                if endpoint in self.limiters:
                    limiter, _ = self.limiters[endpoint]
                    key = f"{client_id}:{endpoint}"
                    if hasattr(limiter, 'requests'):
                        limiter.requests.pop(key, None)
                    elif hasattr(limiter, 'buckets'):
                        limiter.buckets.pop(key, None)
            else:
                # Reset all endpoints for client
                for endpoint_name, (limiter, _) in self.limiters.items():
                    key = f"{client_id}:{endpoint_name}"
                    if hasattr(limiter, 'requests'):
                        limiter.requests.pop(key, None)
                    elif hasattr(limiter, 'buckets'):
                        limiter.buckets.pop(key, None)


# Global rate limiter instance
_rate_limiter_instance: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        _rate_limiter_instance = RateLimiter()
        _initialize_default_limits()
    return _rate_limiter_instance


def _initialize_default_limits():
    """Initialize default rate limits"""
    limiter = _rate_limiter_instance
    
    # API endpoints
    limiter.add_endpoint(RateLimitConfig(
        endpoint="/api/employees",
        requests_per_minute=60,
        strategy=RateLimitStrategy.SLIDING_WINDOW
    ))
    
    limiter.add_endpoint(RateLimitConfig(
        endpoint="/api/departments",
        requests_per_minute=60,
        strategy=RateLimitStrategy.SLIDING_WINDOW
    ))
    
    limiter.add_endpoint(RateLimitConfig(
        endpoint="/api/job-levels",
        requests_per_minute=60,
        strategy=RateLimitStrategy.SLIDING_WINDOW
    ))
    
    limiter.add_endpoint(RateLimitConfig(
        endpoint="/api/auth/login",
        requests_per_minute=10,
        requests_per_hour=100,
        strategy=RateLimitStrategy.SLIDING_WINDOW
    ))
    
    limiter.add_endpoint(RateLimitConfig(
        endpoint="/api/auth/refresh",
        requests_per_minute=30,
        strategy=RateLimitStrategy.TOKEN_BUCKET,
        burst_size=50
    ))


def initialize_rate_limiter() -> RateLimiter:
    """Initialize rate limiter"""
    global _rate_limiter_instance
    _rate_limiter_instance = RateLimiter()
    _initialize_default_limits()
    return _rate_limiter_instance
