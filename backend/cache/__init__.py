"""
Cache module initialization for PeopleOS
"""

from backend.cache.redis_manager import (
    CacheManager,
    RedisCache,
    InMemoryCache,
    get_cache_manager,
    cache_get,
    cache_set,
    cache_delete,
    cache_exists,
    cache_clear,
    cache_stats,
)

__all__ = [
    "CacheManager",
    "RedisCache",
    "InMemoryCache",
    "get_cache_manager",
    "cache_get",
    "cache_set",
    "cache_delete",
    "cache_exists",
    "cache_clear",
    "cache_stats",
]
