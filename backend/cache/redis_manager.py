"""
Redis caching module for PeopleOS

Provides high-performance caching layer for frequently accessed data.
Supports key expiration, cache invalidation, and statistics tracking.
"""

import os
import json
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """Abstract cache backend interface"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache"""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        pass


class RedisCache(CacheBackend):
    """Redis-based cache implementation"""

    def __init__(
        self,
        url: str = "redis://localhost:6379/0",
        ttl: int = 3600,
        max_connections: int = 10,
    ):
        """
        Initialize Redis cache.

        Args:
            url: Redis connection URL
            ttl: Default time-to-live in seconds (1 hour)
            max_connections: Connection pool size
        """
        if not REDIS_AVAILABLE:
            raise ImportError("redis package not installed. Install with: pip install redis")

        self.url = url
        self.default_ttl = ttl
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
        }

        try:
            self.redis = redis.from_url(
                url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30,
                max_connections=max_connections,
            )
            # Test connection
            self.redis.ping()
            logger.info(f"Redis cache initialized: {url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            if value is not None:
                self.stats["hits"] += 1
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            else:
                self.stats["misses"] += 1
                return None
        except Exception as e:
            logger.warning(f"Cache get error for key '{key}': {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            else:
                value = str(value)

            self.redis.setex(key, ttl, value)
            self.stats["sets"] += 1
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            result = self.redis.delete(key)
            if result > 0:
                self.stats["deletes"] += 1
            return result > 0
        except Exception as e:
            logger.warning(f"Cache delete error for key '{key}': {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return self.redis.exists(key) > 0
        except Exception as e:
            logger.warning(f"Cache exists error for key '{key}': {e}")
            return False

    def clear(self) -> bool:
        """Clear all cache"""
        try:
            self.redis.flushdb()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            hits = self.stats["hits"]
            misses = self.stats["misses"]
            total = hits + misses
            hit_ratio = (hits / total * 100) if total > 0 else 0

            info = self.redis.info("memory")
            return {
                "connected": True,
                "hits": hits,
                "misses": misses,
                "hit_ratio": f"{hit_ratio:.1f}%",
                "sets": self.stats["sets"],
                "deletes": self.stats["deletes"],
                "memory_used_mb": info.get("used_memory", 0) / (1024 * 1024),
                "memory_peak_mb": info.get("used_memory_peak", 0) / (1024 * 1024),
            }
        except Exception as e:
            logger.warning(f"Stats error: {e}")
            return {
                "connected": False,
                "error": str(e),
            }


class InMemoryCache(CacheBackend):
    """In-memory cache implementation (fallback)"""

    def __init__(self, ttl: int = 3600):
        """Initialize in-memory cache"""
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = ttl
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
        }
        logger.info("Using in-memory cache (not suitable for production)")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            entry = self.cache[key]
            if entry["expires"] > datetime.utcnow():
                self.stats["hits"] += 1
                return entry["value"]
            else:
                del self.cache[key]
        self.stats["misses"] += 1
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        self.cache[key] = {
            "value": value,
            "expires": datetime.utcnow() + timedelta(seconds=ttl),
        }
        self.stats["sets"] += 1
        return True

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
            self.stats["deletes"] += 1
            return True
        return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if key not in self.cache:
            return False
        entry = self.cache[key]
        if entry["expires"] > datetime.utcnow():
            return True
        del self.cache[key]
        return False

    def clear(self) -> bool:
        """Clear all cache"""
        self.cache.clear()
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hits = self.stats["hits"]
        misses = self.stats["misses"]
        total = hits + misses
        hit_ratio = (hits / total * 100) if total > 0 else 0

        return {
            "type": "in_memory",
            "hits": hits,
            "misses": misses,
            "hit_ratio": f"{hit_ratio:.1f}%",
            "sets": self.stats["sets"],
            "deletes": self.stats["deletes"],
            "cached_keys": len(self.cache),
        }


class CacheManager:
    """Unified cache manager supporting multiple backends"""

    def __init__(self, backend: Optional[CacheBackend] = None):
        """
        Initialize cache manager.

        Args:
            backend: Cache backend (defaults to Redis or in-memory)
        """
        if backend:
            self.backend = backend
        else:
            # Try Redis, fallback to in-memory
            redis_enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
            if redis_enabled and REDIS_AVAILABLE:
                try:
                    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
                    self.backend = RedisCache(redis_url)
                except Exception as e:
                    logger.warning(f"Redis initialization failed, using in-memory cache: {e}")
                    self.backend = InMemoryCache()
            else:
                self.backend = InMemoryCache()

    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        return self.backend.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value"""
        return self.backend.set(key, value, ttl)

    def delete(self, key: str) -> bool:
        """Delete cached value"""
        return self.backend.delete(key)

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.backend.exists(key)

    def clear(self) -> bool:
        """Clear all cache"""
        return self.backend.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.backend.get_stats()

    def cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_parts = list(map(str, args))
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        return ":".join(key_parts)


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


# Convenience functions
def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    return get_cache_manager().get(key)


def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Set value in cache"""
    return get_cache_manager().set(key, value, ttl)


def cache_delete(key: str) -> bool:
    """Delete value from cache"""
    return get_cache_manager().delete(key)


def cache_exists(key: str) -> bool:
    """Check if value exists in cache"""
    return get_cache_manager().exists(key)


def cache_clear() -> bool:
    """Clear all cache"""
    return get_cache_manager().clear()


def cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return get_cache_manager().get_stats()
