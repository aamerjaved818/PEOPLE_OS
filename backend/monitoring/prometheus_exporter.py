"""
Prometheus metrics exporter for peopleOS eBusiness Suite

Exposes detailed system, application, and business metrics for Prometheus scraping.
"""

from datetime import datetime
from typing import Dict, Optional
from enum import Enum

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)


class MetricNamespace(str, Enum):
    """Metric namespaces for organizing metrics"""
    SYSTEM = "peopleOS_system"
    API = "peopleOS_api"
    DATABASE = "peopleOS_database"
    CACHE = "peopleOS_cache"
    BUSINESS = "peopleOS_business"


class PrometheusMetrics:
    """Prometheus metrics collection and export"""

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """Initialize Prometheus metrics"""
        self.registry = registry or CollectorRegistry()
        self._init_system_metrics()
        self._init_api_metrics()
        self._init_database_metrics()
        self._init_cache_metrics()
        self._init_business_metrics()

    def _init_system_metrics(self):
        """Initialize system metrics"""
        # System health
        self.system_health = Gauge(
            f"{MetricNamespace.SYSTEM.value}_health_score",
            "System health score (0-5)",
            registry=self.registry
        )
        
        # Uptime
        self.system_uptime_seconds = Gauge(
            f"{MetricNamespace.SYSTEM.value}_uptime_seconds",
            "Application uptime in seconds",
            registry=self.registry
        )
        
        # CPU and Memory
        self.system_cpu_percent = Gauge(
            f"{MetricNamespace.SYSTEM.value}_cpu_percent",
            "CPU usage percentage",
            registry=self.registry
        )
        
        self.system_memory_percent = Gauge(
            f"{MetricNamespace.SYSTEM.value}_memory_percent",
            "Memory usage percentage",
            registry=self.registry
        )
        
        # Database connections
        self.db_connections_active = Gauge(
            f"{MetricNamespace.SYSTEM.value}_db_connections_active",
            "Active database connections",
            registry=self.registry
        )

    def _init_api_metrics(self):
        """Initialize API metrics"""
        # Request counter
        self.api_requests_total = Counter(
            f"{MetricNamespace.API.value}_requests_total",
            "Total API requests",
            ["method", "endpoint", "status"],
            registry=self.registry
        )
        
        # Request latency histogram
        self.api_latency_seconds = Histogram(
            f"{MetricNamespace.API.value}_latency_seconds",
            "API request latency in seconds",
            ["method", "endpoint"],
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
            registry=self.registry
        )
        
        # Error counter
        self.api_errors_total = Counter(
            f"{MetricNamespace.API.value}_errors_total",
            "Total API errors",
            ["method", "endpoint", "error_type"],
            registry=self.registry
        )
        
        # Active requests gauge
        self.api_requests_in_progress = Gauge(
            f"{MetricNamespace.API.value}_requests_in_progress",
            "API requests currently in progress",
            registry=self.registry
        )

    def _init_database_metrics(self):
        """Initialize database metrics"""
        # Query latency
        self.db_query_latency_seconds = Histogram(
            f"{MetricNamespace.DATABASE.value}_query_latency_seconds",
            "Database query execution time",
            ["operation", "table"],
            buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
            registry=self.registry
        )
        
        # Query counter
        self.db_queries_total = Counter(
            f"{MetricNamespace.DATABASE.value}_queries_total",
            "Total database queries",
            ["operation", "table"],
            registry=self.registry
        )
        
        # Slow query counter
        self.db_slow_queries_total = Counter(
            f"{MetricNamespace.DATABASE.value}_slow_queries_total",
            "Total slow database queries (>100ms)",
            ["operation", "table"],
            registry=self.registry
        )
        
        # Connection pool stats
        self.db_pool_size = Gauge(
            f"{MetricNamespace.DATABASE.value}_pool_size",
            "Database connection pool size",
            registry=self.registry
        )
        
        self.db_pool_checked_out = Gauge(
            f"{MetricNamespace.DATABASE.value}_pool_checked_out",
            "Database connections checked out",
            registry=self.registry
        )

    def _init_cache_metrics(self):
        """Initialize cache metrics"""
        # Cache hits
        self.cache_hits_total = Counter(
            f"{MetricNamespace.CACHE.value}_hits_total",
            "Total cache hits",
            ["cache_type"],
            registry=self.registry
        )
        
        # Cache misses
        self.cache_misses_total = Counter(
            f"{MetricNamespace.CACHE.value}_misses_total",
            "Total cache misses",
            ["cache_type"],
            registry=self.registry
        )
        
        # Cache hit ratio gauge
        self.cache_hit_ratio = Gauge(
            f"{MetricNamespace.CACHE.value}_hit_ratio",
            "Cache hit ratio (0-1)",
            ["cache_type"],
            registry=self.registry
        )
        
        # Cache size
        self.cache_size_bytes = Gauge(
            f"{MetricNamespace.CACHE.value}_size_bytes",
            "Cache size in bytes",
            ["cache_type"],
            registry=self.registry
        )
        
        # Cache latency
        self.cache_latency_seconds = Histogram(
            f"{MetricNamespace.CACHE.value}_latency_seconds",
            "Cache operation latency",
            ["operation", "cache_type"],
            buckets=(0.0001, 0.0005, 0.001, 0.005, 0.01),
            registry=self.registry
        )

    def _init_business_metrics(self):
        """Initialize business metrics"""
        # Employee count
        self.employees_total = Gauge(
            f"{MetricNamespace.BUSINESS.value}_employees_total",
            "Total employees in system",
            ["org"],
            registry=self.registry
        )
        
        # Department count
        self.departments_total = Gauge(
            f"{MetricNamespace.BUSINESS.value}_departments_total",
            "Total departments",
            ["org"],
            registry=self.registry
        )
        
        # Active users
        self.active_users_total = Gauge(
            f"{MetricNamespace.BUSINESS.value}_active_users_total",
            "Active users in last 24 hours",
            registry=self.registry
        )
        
        # Data operations
        self.data_changes_total = Counter(
            f"{MetricNamespace.BUSINESS.value}_data_changes_total",
            "Total data modifications",
            ["resource_type", "operation"],
            registry=self.registry
        )
        
        # Errors by type
        self.errors_by_type_total = Counter(
            f"{MetricNamespace.BUSINESS.value}_errors_by_type_total",
            "Errors by type",
            ["error_type"],
            registry=self.registry
        )

    def record_api_request(
        self,
        method: str,
        endpoint: str,
        status: int,
        latency_seconds: float,
        error_type: Optional[str] = None
    ):
        """Record API request metrics"""
        self.api_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        self.api_latency_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(latency_seconds)
        
        if error_type:
            self.api_errors_total.labels(
                method=method,
                endpoint=endpoint,
                error_type=error_type
            ).inc()

    def record_database_query(
        self,
        operation: str,
        table: str,
        latency_seconds: float
    ):
        """Record database query metrics"""
        self.db_queries_total.labels(
            operation=operation,
            table=table
        ).inc()
        
        self.db_query_latency_seconds.labels(
            operation=operation,
            table=table
        ).observe(latency_seconds)
        
        # Track slow queries (>0.1s)
        if latency_seconds > 0.1:
            self.db_slow_queries_total.labels(
                operation=operation,
                table=table
            ).inc()

    def record_cache_operation(
        self,
        cache_type: str,
        operation: str,
        hit: bool,
        latency_seconds: float
    ):
        """Record cache operation metrics"""
        if hit:
            self.cache_hits_total.labels(cache_type=cache_type).inc()
        else:
            self.cache_misses_total.labels(cache_type=cache_type).inc()
        
        self.cache_latency_seconds.labels(
            operation=operation,
            cache_type=cache_type
        ).observe(latency_seconds)

    def update_cache_hit_ratio(self, cache_type: str, ratio: float):
        """Update cache hit ratio"""
        self.cache_hit_ratio.labels(cache_type=cache_type).set(ratio)

    def record_business_change(
        self,
        resource_type: str,
        operation: str
    ):
        """Record business data change"""
        self.data_changes_total.labels(
            resource_type=resource_type,
            operation=operation
        ).inc()

    def record_error(self, error_type: str):
        """Record error metric"""
        self.errors_by_type_total.labels(error_type=error_type).inc()

    def get_metrics(self) -> bytes:
        """Export metrics in Prometheus format"""
        return generate_latest(self.registry)

    def get_content_type(self) -> str:
        """Get Prometheus content type"""
        return CONTENT_TYPE_LATEST


# Global metrics instance
_metrics_instance: Optional[PrometheusMetrics] = None


def get_metrics() -> PrometheusMetrics:
    """Get global metrics instance"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = PrometheusMetrics()
    return _metrics_instance


def initialize_metrics() -> PrometheusMetrics:
    """Initialize metrics"""
    global _metrics_instance
    _metrics_instance = PrometheusMetrics()
    return _metrics_instance
