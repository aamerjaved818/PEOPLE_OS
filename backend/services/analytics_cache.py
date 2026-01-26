"""
Analytics Cache Manager - Caches frequently accessed metrics
Uses in-memory cache with TTL and invalidation on data changes
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import hashlib
import json
import logging
from functools import wraps
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class CacheManager:
    """Simple in-memory cache with TTL and invalidation"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._dependencies: Dict[str, List[str]] = {}  # Track cache dependencies
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600, depends_on: Optional[List[str]] = None):
        """Set cache value with TTL and dependencies
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds (default 1 hour)
            depends_on: List of entity types this depends on (e.g., ['Employee', 'Department'])
        """
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.now()
        }
        
        if depends_on:
            for dependency in depends_on:
                if dependency not in self._dependencies:
                    self._dependencies[dependency] = []
                if key not in self._dependencies[dependency]:
                    self._dependencies[dependency].append(key)
        
        logger.debug(f"Cache SET: {key} (TTL: {ttl_seconds}s)")
    
    def get(self, key: str) -> Optional[Any]:
        """Get cache value if not expired"""
        if key not in self._cache:
            logger.debug(f"Cache MISS: {key}")
            return None
        
        cached = self._cache[key]
        if datetime.now() > cached['expires_at']:
            del self._cache[key]
            logger.debug(f"Cache EXPIRED: {key}")
            return None
        
        logger.debug(f"Cache HIT: {key}")
        return cached['value']
    
    def invalidate(self, entity_type: str):
        """Invalidate all caches that depend on this entity type
        
        Args:
            entity_type: Entity type that changed (e.g., 'Employee', 'Department')
        """
        if entity_type not in self._dependencies:
            return
        
        keys_to_delete = self._dependencies[entity_type]
        for key in keys_to_delete:
            if key in self._cache:
                del self._cache[key]
                logger.info(f"Cache INVALIDATED: {key} (due to {entity_type} change)")
        
        del self._dependencies[entity_type]
    
    def clear(self):
        """Clear all caches"""
        self._cache.clear()
        self._dependencies.clear()
        logger.info("Cache CLEARED: All caches invalidated")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        active_count = sum(1 for c in self._cache.values() if datetime.now() <= c['expires_at'])
        expired_count = len(self._cache) - active_count
        
        return {
            'active_items': active_count,
            'expired_items': expired_count,
            'total_items': len(self._cache),
            'dependencies_tracked': len(self._dependencies),
            'timestamp': datetime.now().isoformat()
        }


# Global cache instance
_cache = CacheManager()


def cache_dashboard_summary(ttl_seconds: int = 3600):
    """Decorator to cache dashboard summary results
    
    Args:
        ttl_seconds: Cache TTL in seconds (default 1 hour)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(db: Session, organization_id: str, *args, **kwargs):
            cache_key = f"dashboard_summary:{organization_id}"
            
            # Try to get from cache
            cached_result = _cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Calculate metrics
            result = func(db, organization_id, *args, **kwargs)
            
            # Cache with dependencies
            _cache.set(
                cache_key,
                result,
                ttl_seconds=ttl_seconds,
                depends_on=['Employee', 'Candidate', 'Department']
            )
            
            return result
        return wrapper
    return decorator


def cache_headcount_trends(ttl_seconds: int = 3600):
    """Decorator to cache headcount trends"""
    def decorator(func):
        @wraps(func)
        def wrapper(db: Session, organization_id: str, *args, **kwargs):
            cache_key = f"headcount_trends:{organization_id}"
            
            cached_result = _cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(db, organization_id, *args, **kwargs)
            _cache.set(cache_key, result, ttl_seconds=ttl_seconds, depends_on=['Employee'])
            return result
        return wrapper
    return decorator


def cache_recruitment_funnel(ttl_seconds: int = 3600):
    """Decorator to cache recruitment funnel"""
    def decorator(func):
        @wraps(func)
        def wrapper(db: Session, organization_id: str, *args, **kwargs):
            cache_key = f"recruitment_funnel:{organization_id}"
            
            cached_result = _cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(db, organization_id, *args, **kwargs)
            _cache.set(cache_key, result, ttl_seconds=ttl_seconds, depends_on=['Candidate'])
            return result
        return wrapper
    return decorator


def cache_payroll_summary(ttl_seconds: int = 86400):
    """Decorator to cache payroll summary (24 hour TTL)"""
    def decorator(func):
        @wraps(func)
        def wrapper(db: Session, organization_id: str, *args, **kwargs):
            cache_key = f"payroll_summary:{organization_id}:{datetime.now().strftime('%Y-%m')}"
            
            cached_result = _cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(db, organization_id, *args, **kwargs)
            _cache.set(cache_key, result, ttl_seconds=ttl_seconds, depends_on=['PayrollLedger'])
            return result
        return wrapper
    return decorator


def cache_report(report_type: str, ttl_seconds: int = 86400):
    """Decorator to cache generated reports (24 hour TTL by default)"""
    def decorator(func):
        @wraps(func)
        def wrapper(db: Session, organization_id: str, *args, **kwargs):
            # Generate cache key from parameters
            param_hash = hashlib.md5(str((organization_id, args, tuple(sorted(kwargs.items())))).encode()).hexdigest()[:8]
            cache_key = f"report:{report_type}:{organization_id}:{param_hash}"
            
            cached_result = _cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Using cached report: {report_type}")
                return cached_result
            
            result = func(db, organization_id, *args, **kwargs)
            _cache.set(cache_key, result, ttl_seconds=ttl_seconds, depends_on=['Employee', 'Candidate', 'PayrollLedger'])
            return result
        return wrapper
    return decorator


class AnalyticsCacheService:
    """Service to manage analytics caching"""
    
    @staticmethod
    def get_cache_manager() -> CacheManager:
        """Get global cache manager instance"""
        return _cache
    
    @staticmethod
    def cache_is_enabled() -> bool:
        """Check if caching is enabled"""
        return True
    
    @staticmethod
    def on_employee_created(organization_id: str):
        """Invalidate caches when employee is created"""
        _cache.invalidate('Employee')
        logger.info(f"Analytics cache invalidated: Employee created in {organization_id}")
    
    @staticmethod
    def on_employee_updated(organization_id: str):
        """Invalidate caches when employee is updated"""
        _cache.invalidate('Employee')
        logger.info(f"Analytics cache invalidated: Employee updated in {organization_id}")
    
    @staticmethod
    def on_employee_deleted(organization_id: str):
        """Invalidate caches when employee is deleted"""
        _cache.invalidate('Employee')
        logger.info(f"Analytics cache invalidated: Employee deleted from {organization_id}")
    
    @staticmethod
    def on_candidate_created(organization_id: str):
        """Invalidate caches when candidate is created"""
        _cache.invalidate('Candidate')
        logger.info(f"Analytics cache invalidated: Candidate created in {organization_id}")
    
    @staticmethod
    def on_candidate_updated(organization_id: str):
        """Invalidate caches when candidate is updated"""
        _cache.invalidate('Candidate')
        logger.info(f"Analytics cache invalidated: Candidate updated in {organization_id}")
    
    @staticmethod
    def on_payroll_created(organization_id: str):
        """Invalidate caches when payroll is created"""
        _cache.invalidate('PayrollLedger')
        logger.info(f"Analytics cache invalidated: Payroll created in {organization_id}")
    
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """Get cache statistics"""
        return _cache.stats()
    
    @staticmethod
    def clear_all():
        """Clear all caches"""
        _cache.clear()
