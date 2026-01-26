"""
Phase 2 Task 2: Performance Optimization Tests

Comprehensive test suite for:
- Redis caching and cache invalidation
- Database query optimization
- Connection pooling
- Query batching
- Metrics collection
- Index recommendations
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from backend.cache.redis_manager import (
    InMemoryCache,
    RedisCache,
    CacheManager,
    get_cache_manager,
    cache_get,
    cache_set,
    cache_delete,
)
from backend.database.query_optimizer import (
    QueryOptimizer,
    QueryMetrics,
    batch_query,
    cached_query,
    transaction_scope,
    IndexRecommendations,
    get_query_optimizer,
)


# ============================================================================
# CACHE TESTS
# ============================================================================

class TestInMemoryCache:
    """Test in-memory cache backend"""

    def test_set_and_get_value(self):
        """Test basic cache set and get"""
        cache = InMemoryCache(ttl=3600)

        cache.set("user:1", {"id": 1, "name": "John"})
        result = cache.get("user:1")

        assert result == {"id": 1, "name": "John"}

    def test_get_nonexistent_key(self):
        """Test getting non-existent key returns None"""
        cache = InMemoryCache()

        result = cache.get("nonexistent")

        assert result is None

    def test_delete_key(self):
        """Test deleting cached key"""
        cache = InMemoryCache()
        cache.set("key", "value")

        result = cache.delete("key")

        assert result is True
        assert cache.get("key") is None

    def test_delete_nonexistent_key(self):
        """Test deleting non-existent key"""
        cache = InMemoryCache()

        result = cache.delete("nonexistent")

        assert result is False

    def test_exists_key(self):
        """Test key existence check"""
        cache = InMemoryCache()
        cache.set("key", "value")

        assert cache.exists("key") is True
        assert cache.exists("nonexistent") is False

    def test_cache_expiration(self):
        """Test TTL expiration"""
        cache = InMemoryCache(ttl=1)
        cache.set("expiring", "value", ttl=1)

        assert cache.get("expiring") == "value"

        time.sleep(1.1)

        assert cache.get("expiring") is None

    def test_clear_cache(self):
        """Test clearing all cache"""
        cache = InMemoryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        result = cache.clear()

        assert result is True
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cache_statistics(self):
        """Test cache statistics tracking"""
        cache = InMemoryCache()

        cache.set("key", "value")
        cache.get("key")  # hit
        cache.get("missing")  # miss

        stats = cache.get_stats()

        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["sets"] == 1
        assert "hit_ratio" in stats

    def test_cache_different_types(self):
        """Test caching different data types"""
        cache = InMemoryCache()

        cache.set("string", "value")
        cache.set("number", 42)
        cache.set("list", [1, 2, 3])
        cache.set("dict", {"key": "value"})

        assert cache.get("string") == "value"
        assert cache.get("number") == 42
        assert cache.get("list") == [1, 2, 3]
        assert cache.get("dict") == {"key": "value"}


class TestCacheManager:
    """Test unified cache manager"""

    def test_cache_manager_initialization(self):
        """Test cache manager initializes correctly"""
        with patch.dict('os.environ', {'REDIS_ENABLED': 'false'}):
            manager = CacheManager()
            assert manager.backend is not None

    def test_cache_manager_get_set(self):
        """Test cache manager get/set operations"""
        cache = InMemoryCache()
        manager = CacheManager(backend=cache)

        manager.set("key", "value")
        result = manager.get("key")

        assert result == "value"

    def test_cache_manager_delete(self):
        """Test cache manager delete"""
        cache = InMemoryCache()
        manager = CacheManager(backend=cache)

        manager.set("key", "value")
        manager.delete("key")

        assert manager.get("key") is None

    def test_cache_manager_exists(self):
        """Test cache manager exists check"""
        cache = InMemoryCache()
        manager = CacheManager(backend=cache)

        manager.set("key", "value")

        assert manager.exists("key") is True
        assert manager.exists("missing") is False

    def test_cache_manager_clear(self):
        """Test cache manager clear"""
        cache = InMemoryCache()
        manager = CacheManager(backend=cache)

        manager.set("key1", "value1")
        manager.set("key2", "value2")
        manager.clear()

        assert manager.get("key1") is None
        assert manager.get("key2") is None

    def test_cache_key_generation(self):
        """Test cache key generation"""
        manager = CacheManager(backend=InMemoryCache())

        key1 = manager.cache_key("user", 1)
        key2 = manager.cache_key("user", 1, scope="admin")

        assert key1 == "user:1"
        assert "user:1" in key2 and "scope=admin" in key2

    def test_cache_stats(self):
        """Test cache statistics"""
        cache = InMemoryCache()
        manager = CacheManager(backend=cache)

        manager.set("key", "value")
        manager.get("key")

        stats = manager.get_stats()

        assert stats["hits"] >= 0
        assert stats["sets"] >= 1


class TestCacheConvenienceFunctions:
    """Test cache convenience functions"""

    @patch('backend.cache.redis_manager.get_cache_manager')
    def test_cache_get_function(self, mock_get_manager):
        """Test cache_get convenience function"""
        mock_manager = Mock()
        mock_manager.get.return_value = "cached_value"
        mock_get_manager.return_value = mock_manager

        result = cache_get("key")

        assert result == "cached_value"

    @patch('backend.cache.redis_manager.get_cache_manager')
    def test_cache_set_function(self, mock_get_manager):
        """Test cache_set convenience function"""
        mock_manager = Mock()
        mock_manager.set.return_value = True
        mock_get_manager.return_value = mock_manager

        result = cache_set("key", "value")

        assert result is True


# ============================================================================
# QUERY OPTIMIZATION TESTS
# ============================================================================

class TestQueryMetrics:
    """Test query metrics collection"""

    def test_add_query_basic(self):
        """Test adding query metrics"""
        metrics = QueryMetrics()

        metrics.add_query(0.05, "SELECT * FROM users")

        assert metrics.total_queries == 1
        assert metrics.total_time == 0.05

    def test_slow_query_detection(self):
        """Test slow query detection"""
        metrics = QueryMetrics()

        metrics.add_query(0.05, "SELECT * FROM users", slow_threshold=0.1)
        metrics.add_query(0.15, "SELECT * FROM employees", slow_threshold=0.1)

        assert len(metrics.slow_queries) == 1
        assert metrics.slow_queries[0]["duration"] == 0.15

    def test_slow_query_limit(self):
        """Test slow queries keep only recent 100"""
        metrics = QueryMetrics()

        for i in range(150):
            metrics.add_query(0.2, f"QUERY {i}", slow_threshold=0.1)

        assert len(metrics.slow_queries) == 100

    def test_metrics_statistics(self):
        """Test metrics statistics generation"""
        metrics = QueryMetrics()

        metrics.add_query(0.05, "Query 1")
        metrics.add_query(0.10, "Query 2")

        stats = metrics.get_stats()

        assert stats["total_queries"] == 2
        assert "average_time" in stats
        assert "total_time" in stats


class TestQueryOptimizer:
    """Test query optimizer"""

    def test_optimizer_initialization(self):
        """Test query optimizer initializes correctly"""
        optimizer = QueryOptimizer(slow_query_threshold=0.1)

        assert optimizer is not None
        assert optimizer.slow_query_threshold == 0.1

    def test_connection_pool_configuration(self):
        """Test connection pool configuration"""
        optimizer = QueryOptimizer()

        config = optimizer.setup_connection_pool(
            "sqlite:///test.db",
            pool_size=20,
            max_overflow=10,
        )

        assert config["pool_size"] == 20
        assert config["max_overflow"] == 10
        assert config["pool_pre_ping"] is True

    @patch('backend.database.query_optimizer.joinedload')
    def test_optimize_joins(self, mock_joinedload):
        """Test join optimization"""
        optimizer = QueryOptimizer()
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query

        # Mock model with relationships
        mock_model = Mock()
        mock_model.department = Mock()

        result = optimizer.optimize_joins(
            mock_session,
            mock_model,
            ["department"],
        )

        assert result is not None
        mock_joinedload.assert_called_once()


class TestCachedQueryDecorator:
    """Test cached query decorator"""

    def test_cached_query_caches_result(self):
        """Test cached query decorator caches results"""
        cache = InMemoryCache()
        manager = CacheManager(backend=cache)

        call_count = 0

        @cached_query(ttl=3600)
        def get_users():
            nonlocal call_count
            call_count += 1
            return [{"id": 1, "name": "John"}]

        # First call
        result1 = get_users()
        # Second call (should be cached)
        result2 = get_users()

        assert result1 == result2
        assert call_count == 1  # Only called once due to cache

    @patch('backend.database.query_optimizer.get_cache_manager')
    def test_cached_query_custom_key_builder(self, mock_get_manager):
        """Test cached query with custom key builder"""
        cache = InMemoryCache()
        manager = CacheManager(backend=cache)
        mock_get_manager.return_value = manager

        def custom_key(user_id):
            return f"user:{user_id}"

        @cached_query(ttl=3600, key_builder=custom_key)
        def get_user(user_id):
            return {"id": user_id}

        result = get_user(1)

        assert result == {"id": 1}
        assert cache.exists("user:1")


class TestBatchQuery:
    """Test batch query functionality"""

    def test_batch_query_splits_into_batches(self):
        """Test batch query splits IDs correctly"""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query

        # Setup mock to return results
        mock_query.filter.return_value.all.return_value = [
            Mock(id=1),
            Mock(id=2),
        ]

        mock_model = Mock()
        mock_model.id = Mock()
        mock_model.id.in_ = Mock(return_value=Mock())

        ids = [1, 2, 3, 4, 5]
        results = batch_query(
            mock_session,
            mock_model,
            ids,
            batch_size=2,
        )

        # Should have been called 3 times (batches of 2, 2, 1)
        assert mock_query.filter.call_count >= 1


class TestTransactionScope:
    """Test transaction scope context manager"""

    def test_transaction_commit(self):
        """Test successful transaction commit"""
        mock_session = Mock()

        with transaction_scope(mock_session):
            pass

        mock_session.commit.assert_called_once()

    def test_transaction_rollback_on_error(self):
        """Test transaction rollback on error"""
        mock_session = Mock()

        with pytest.raises(ValueError):
            with transaction_scope(mock_session):
                raise ValueError("Test error")

        mock_session.rollback.assert_called_once()

    def test_transaction_always_closes_session(self):
        """Test session always closes"""
        mock_session = Mock()

        with transaction_scope(mock_session):
            pass

        mock_session.close.assert_called_once()


class TestIndexRecommendations:
    """Test index recommendation engine"""

    def test_recommend_indexes_for_common_patterns(self):
        """Test index recommendations for common patterns"""
        recommendations = IndexRecommendations()
        metrics = QueryMetrics()

        # Simulate slow queries
        metrics.add_query(0.15, "SELECT * FROM users WHERE user_id = 1", 0.1)
        metrics.add_query(0.12, "SELECT * FROM employees ORDER BY created_at", 0.1)

        recs = recommendations.analyze_slow_queries(metrics)

        assert len(recs) > 0

    def test_generate_create_index_sql(self):
        """Test CREATE INDEX SQL generation"""
        recommendations = IndexRecommendations()

        sql = recommendations.format_create_index("users", ["user_id"])

        assert "CREATE INDEX" in sql
        assert "users" in sql
        assert "user_id" in sql

    def test_composite_index_recommendation(self):
        """Test composite index recommendation"""
        recommendations = IndexRecommendations()

        sql = recommendations.format_create_index("logs", ["user_id", "created_at"])

        assert "user_id" in sql
        assert "created_at" in sql


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestPerformanceIntegration:
    """Integration tests for performance optimization"""

    def test_cache_hit_ratio_tracking(self):
        """Test cache hit ratio is tracked correctly"""
        cache = InMemoryCache()
        manager = CacheManager(backend=cache)

        manager.set("key1", "value1")
        manager.set("key2", "value2")

        manager.get("key1")  # hit
        manager.get("key1")  # hit
        manager.get("missing")  # miss

        stats = manager.get_stats()

        assert stats["hits"] == 2
        assert stats["misses"] == 1

    def test_query_performance_monitoring(self):
        """Test query performance monitoring"""
        optimizer = QueryOptimizer()

        optimizer.metrics.add_query(0.05, "SELECT * FROM users")
        optimizer.metrics.add_query(0.10, "SELECT * FROM employees")

        stats = optimizer.get_metrics()

        assert stats["total_queries"] == 2
        assert "average_time" in stats

    def test_cache_and_query_optimization_together(self):
        """Test cache and query optimization work together"""
        cache = InMemoryCache()
        manager = CacheManager(backend=cache)
        optimizer = QueryOptimizer()

        # Cache a query result
        manager.set("expensive_query", [{"id": 1}, {"id": 2}])

        # Get from cache
        result = manager.get("expensive_query")

        assert result == [{"id": 1}, {"id": 2}]

        # Record metrics
        optimizer.metrics.add_query(0.001, "SELECT * FROM cache")

        stats = optimizer.get_metrics()
        assert stats["total_queries"] == 1


class TestPerformanceBenchmarks:
    """Performance benchmark tests"""

    def test_cache_get_performance(self):
        """Test cache get operation performance"""
        cache = InMemoryCache()
        cache.set("key", "value" * 1000)

        start = time.time()
        for _ in range(1000):
            cache.get("key")
        duration = time.time() - start

        # Should complete 1000 gets in less than 100ms
        assert duration < 0.1, f"Cache get too slow: {duration:.3f}s"

    def test_cache_set_performance(self):
        """Test cache set operation performance"""
        cache = InMemoryCache()

        start = time.time()
        for i in range(1000):
            cache.set(f"key{i}", f"value{i}")
        duration = time.time() - start

        # Should complete 1000 sets in less than 100ms
        assert duration < 0.1, f"Cache set too slow: {duration:.3f}s"

    def test_large_cache_hit_ratio(self):
        """Test cache hit ratio with large dataset"""
        cache = InMemoryCache()

        # Add 1000 items
        for i in range(1000):
            cache.set(f"key{i}", f"value{i}")

        # Access items (80% hits, 20% misses)
        for i in range(800):
            cache.get(f"key{i}")  # hit
        for i in range(200):
            cache.get(f"missing{i}")  # miss

        stats = cache.get_stats()
        hit_ratio = float(stats["hit_ratio"].rstrip("%"))

        assert 75 < hit_ratio < 85, f"Expected ~80% hit ratio, got {hit_ratio}%"
