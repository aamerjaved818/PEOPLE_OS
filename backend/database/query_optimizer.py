"""
Database query optimization module for PeopleOS

Implements query optimization techniques including:
- Eager loading / join optimization
- Query result caching
- Index recommendations
- Query performance monitoring
- Connection pooling configuration
"""

import time
import logging
from typing import Any, Optional, List, Dict, Callable, Type
from functools import wraps
from contextlib import contextmanager
from datetime import datetime, timedelta

from sqlalchemy import event, pool, text
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.engine import Engine

from backend.cache.redis_manager import get_cache_manager

logger = logging.getLogger(__name__)


class QueryMetrics:
    """Track query performance metrics"""

    def __init__(self):
        self.total_queries = 0
        self.total_time = 0.0
        self.slow_queries = []
        self.cache_hits = 0
        self.cache_misses = 0

    def add_query(self, duration: float, query: str, slow_threshold: float = 0.1):
        """Record query metrics"""
        self.total_queries += 1
        self.total_time += duration

        if duration > slow_threshold:
            self.slow_queries.append({
                "query": query[:100],  # First 100 chars
                "duration": duration,
                "timestamp": datetime.utcnow(),
            })
            # Keep only last 100 slow queries
            if len(self.slow_queries) > 100:
                self.slow_queries.pop(0)

        if duration > slow_threshold:
            logger.warning(f"Slow query ({duration:.3f}s): {query[:100]}")

    def get_stats(self) -> Dict[str, Any]:
        """Get metrics summary"""
        avg_time = (self.total_time / self.total_queries) if self.total_queries > 0 else 0
        return {
            "total_queries": self.total_queries,
            "total_time": f"{self.total_time:.3f}s",
            "average_time": f"{avg_time:.3f}s",
            "slow_queries": len(self.slow_queries),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
        }


class QueryOptimizer:
    """Optimize database queries"""

    def __init__(self, slow_query_threshold: float = 0.1):
        """
        Initialize query optimizer.

        Args:
            slow_query_threshold: Time (seconds) to consider query slow
        """
        self.metrics = QueryMetrics()
        self.slow_query_threshold = slow_query_threshold
        self._cache_manager = get_cache_manager()

    def setup_query_logging(self, engine: Engine):
        """Setup SQLAlchemy event listeners for query monitoring"""

        @event.listens_for(engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())

        @event.listens_for(engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total_time = time.time() - conn.info['query_start_time'].pop(-1)
            self.metrics.add_query(
                total_time,
                statement,
                self.slow_query_threshold,
            )

    def setup_connection_pool(self, engine_url: str, pool_size: int = 20, max_overflow: int = 10):
        """
        Configure connection pooling.

        Args:
            engine_url: SQLAlchemy engine URL
            pool_size: Number of connections to maintain
            max_overflow: Additional connections above pool_size
        """
        return {
            "poolclass": pool.QueuePool,
            "pool_size": pool_size,
            "max_overflow": max_overflow,
            "pool_pre_ping": True,  # Test connection before using
            "pool_recycle": 3600,  # Recycle connections after 1 hour
            "echo": False,
            "connect_args": {
                "timeout": 10,
                "check_same_thread": False,  # For SQLite only
            },
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get query performance metrics"""
        return self.metrics.get_stats()

    def optimize_joins(self, session: Session, model: Type, relationships: List[str]):
        """
        Optimize query with eager loading.

        Args:
            session: SQLAlchemy session
            model: Model class to query
            relationships: List of relationships to eagerly load

        Returns:
            Optimized query object
        """
        query = session.query(model)
        for relationship in relationships:
            query = query.options(joinedload(getattr(model, relationship)))
        return query


def cached_query(
    ttl: int = 3600,
    key_builder: Optional[Callable] = None,
):
    """
    Decorator for caching query results.

    Args:
        ttl: Time-to-live in seconds (default 1 hour)
        key_builder: Function to generate cache key

    Example:
        @cached_query(ttl=1800)
        def get_employees(session: Session):
            return session.query(Employee).all()
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = f"{func.__module__}:{func.__name__}:{str(args)}{str(kwargs)}"

            # Try cache
            cache_manager = get_cache_manager()
            cached_result = cache_manager.get(cache_key)

            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {func.__name__}")

            return result

        return wrapper

    return decorator


def batch_query(
    session: Session,
    model: Type,
    ids: List[Any],
    batch_size: int = 100,
) -> List[Any]:
    """
    Optimize bulk queries using batching.

    Args:
        session: SQLAlchemy session
        model: Model class
        ids: List of IDs to fetch
        batch_size: Number of IDs per query

    Returns:
        List of model instances
    """
    results = []

    for i in range(0, len(ids), batch_size):
        batch = ids[i : i + batch_size]
        batch_results = session.query(model).filter(model.id.in_(batch)).all()
        results.extend(batch_results)

    return results


@contextmanager
def transaction_scope(session: Session, savepoint: bool = False):
    """
    Context manager for transaction management.

    Args:
        session: SQLAlchemy session
        savepoint: Use savepoint (nested transaction)

    Example:
        with transaction_scope(session):
            employee = Employee(name="John")
            session.add(employee)
    """
    try:
        if savepoint:
            sp = session.begin_nested()
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Transaction error: {e}")
        raise
    finally:
        session.close()


class IndexRecommendations:
    """Provide index recommendations based on slow queries"""

    # Common slow query patterns and index recommendations (uppercase for matching)
    PATTERNS = {
        "WHERE USER_ID =": ["user_id"],
        "WHERE DEPARTMENT_ID =": ["department_id"],
        "WHERE ORGANIZATION_ID =": ["organization_id"],
        "WHERE STATUS =": ["status"],
        "WHERE CREATED_AT >": ["created_at"],
        "WHERE CREATED_AT BETWEEN": ["created_at"],
        "ORDER BY CREATED_AT": ["created_at"],
        "ORDER BY NAME": ["name"],
        "WHERE USER_ID = AND CREATED_AT >": ["user_id", "created_at"],
    }

    def __init__(self):
        self.recommendations: List[Dict[str, Any]] = []

    def analyze_slow_queries(self, metrics: QueryMetrics):
        """Analyze slow queries and recommend indexes"""
        self.recommendations.clear()

        for slow_query in metrics.slow_queries:
            query_text = slow_query["query"].upper()

            for pattern, columns in self.PATTERNS.items():
                if pattern in query_text:
                    self.recommendations.append({
                        "columns": columns,
                        "reason": f"Pattern found: {pattern}",
                        "slow_query_sample": slow_query["query"],
                        "duration": slow_query["duration"],
                    })

        return self.recommendations

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Get index recommendations"""
        return self.recommendations

    def format_create_index(self, table: str, columns: List[str]) -> str:
        """Generate CREATE INDEX SQL"""
        index_name = f"idx_{table}_{'_'.join(columns)}"
        cols_str = ", ".join(columns)
        return f"CREATE INDEX {index_name} ON {table} ({cols_str});"


# Global optimizer instance
_optimizer: Optional[QueryOptimizer] = None


def get_query_optimizer() -> QueryOptimizer:
    """Get global query optimizer instance"""
    global _optimizer
    if _optimizer is None:
        _optimizer = QueryOptimizer()
    return _optimizer


def setup_performance_monitoring(engine: Engine):
    """Setup performance monitoring for database"""
    optimizer = get_query_optimizer()
    optimizer.setup_query_logging(engine)
    logger.info("Performance monitoring enabled")
